"""Única pieza del sistema que habla con Ollama.

Envoltorio sobre ``POST /api/chat`` con:
- mensajes de sistema + historial,
- salida estructurada (parámetro ``format`` con un JSON Schema) validada con
  jsonschema + Pydantic; si no cumple se reintenta una vez y luego se lanza
  ``InvalidModelOutput`` (nunca se devuelve texto sin validar),
- ``think: false`` cuando el modelo soporta modo thinking,
- timeouts y reintentos acotados ante errores de conexión / 5xx.

Los logs registran modelo, duración y tokens; nunca el contenido de los mensajes.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import httpx
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as SchemaValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from app.config import Settings, normalize_model_name
from app.services.exceptions import InvalidModelOutput, ModelTimeout, ModelUnavailable

logger = logging.getLogger("app.ollama")

T = TypeVar("T", bound=BaseModel)

# Reintentos cuando la salida no cumple el schema (criterio: "se reintenta una vez").
INVALID_OUTPUT_RETRIES = 1

_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)

Message = dict[str, str]


@dataclass(frozen=True)
class StructuredResult(Generic[T]):
    data: T
    model: str
    duration_ms: int
    prompt_tokens: int | None
    completion_tokens: int | None
    attempts: int


class OllamaClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._settings = settings
        self._http = httpx.AsyncClient(
            base_url=settings.ollama_host,
            timeout=httpx.Timeout(
                settings.ollama_timeout_seconds,
                connect=settings.ollama_connect_timeout_seconds,
            ),
            transport=transport,
        )
        self._capabilities: dict[str, frozenset[str]] = {}

    async def aclose(self) -> None:
        await self._http.aclose()

    # ------------------------------------------------------------------ status
    async def list_local_models(self) -> set[str]:
        """Nombres (normalizados) de los modelos descargados en Ollama."""
        try:
            response = await self._http.get(
                "/api/tags", timeout=self._settings.ollama_health_timeout_seconds
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("ollama.tags failed error=%s", type(exc).__name__)
            raise ModelUnavailable("Ollama no está disponible") from exc

        return {
            normalize_model_name(item.get("name") or item.get("model", ""))
            for item in payload.get("models", [])
        }

    async def capabilities(self, model: str) -> frozenset[str]:
        """Capacidades del modelo (``completion``, ``thinking``, ``tools``...), en caché."""
        if model in self._capabilities:
            return self._capabilities[model]
        try:
            response = await self._http.post(
                "/api/show",
                json={"model": model},
                timeout=self._settings.ollama_health_timeout_seconds,
            )
        except httpx.HTTPError as exc:
            raise ModelUnavailable("Ollama no está disponible") from exc
        if response.status_code == 404:
            raise ModelUnavailable(f"El modelo '{model}' no está descargado en Ollama")
        if response.status_code >= 400:
            raise ModelUnavailable(f"Ollama respondió {response.status_code} al consultar el modelo")
        caps = frozenset(response.json().get("capabilities") or [])
        self._capabilities[model] = caps
        return caps

    # -------------------------------------------------------------- inference
    async def chat_structured(
        self,
        messages: list[Message],
        response_model: type[T],
        *,
        schema: dict[str, Any] | None = None,
        model: str | None = None,
        task: str = "unknown",
    ) -> StructuredResult[T]:
        """Llama a /api/chat forzando ``format=schema`` y devuelve ``response_model`` validado."""
        model = normalize_model_name(model or self._settings.ollama_model)
        schema = schema or response_model.model_json_schema()
        validator = Draft202012Validator(schema)

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "format": schema,
            "keep_alive": self._settings.ollama_keep_alive,
            "options": {
                "temperature": self._settings.ollama_temperature,
                "num_ctx": self._settings.ollama_num_ctx,
            },
        }
        if "thinking" in await self.capabilities(model):
            payload["think"] = False

        total_attempts = 1 + INVALID_OUTPUT_RETRIES
        for attempt in range(1, total_attempts + 1):
            body, duration_ms = await self._post_chat(payload, task=task, attempt=attempt)
            content = (body.get("message") or {}).get("content") or ""
            try:
                data = response_model.model_validate(_parse_json(content, validator))
            except (ValueError, SchemaValidationError, PydanticValidationError) as exc:
                logger.warning(
                    "ollama.chat invalid_output task=%s model=%s attempt=%d/%d error=%s",
                    task, model, attempt, total_attempts, type(exc).__name__,
                )
                continue
            return StructuredResult(
                data=data,
                model=model,
                duration_ms=duration_ms,
                prompt_tokens=body.get("prompt_eval_count"),
                completion_tokens=body.get("eval_count"),
                attempts=attempt,
            )

        raise InvalidModelOutput(
            f"El modelo '{model}' no devolvió una respuesta válida tras {total_attempts} intentos"
        )

    async def _post_chat(self, payload: dict[str, Any], *, task: str, attempt: int) -> tuple[dict[str, Any], int]:
        model = payload["model"]
        transport_attempts = 1 + self._settings.ollama_max_retries
        timeout = self._settings.ollama_timeout_seconds

        for try_no in range(1, transport_attempts + 1):
            started = time.perf_counter()
            failure: str
            try:
                response = await asyncio.wait_for(
                    self._http.post("/api/chat", json=payload), timeout=timeout
                )
            except httpx.ConnectTimeout:
                failure = "connect_timeout"
            except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
                logger.warning("ollama.chat timeout task=%s model=%s timeout_s=%s", task, model, timeout)
                raise ModelTimeout(f"El modelo no respondió en {timeout:g} s") from exc
            except httpx.TransportError as exc:
                failure = type(exc).__name__
            else:
                duration_ms = int((time.perf_counter() - started) * 1000)
                if response.status_code == 404:
                    raise ModelUnavailable(f"El modelo '{model}' no está descargado en Ollama")
                if response.status_code < 400:
                    try:
                        body = response.json()
                    except ValueError as exc:
                        raise InvalidModelOutput("Ollama devolvió un cuerpo que no es JSON") from exc
                    logger.info(
                        "ollama.chat ok task=%s model=%s attempt=%d duration_ms=%d "
                        "prompt_tokens=%s completion_tokens=%s load_ms=%s",
                        task, model, attempt, duration_ms,
                        body.get("prompt_eval_count"), body.get("eval_count"),
                        _ns_to_ms(body.get("load_duration")),
                    )
                    return body, duration_ms
                if response.status_code < 500:
                    raise ModelUnavailable(f"Ollama rechazó la petición ({response.status_code})")
                failure = f"http_{response.status_code}"

            logger.warning(
                "ollama.chat failed task=%s model=%s try=%d/%d reason=%s",
                task, model, try_no, transport_attempts, failure,
            )
            if try_no < transport_attempts:
                await asyncio.sleep(self._settings.ollama_retry_backoff_seconds * try_no)

        raise ModelUnavailable("Ollama no está disponible")


def _parse_json(content: str, validator: Draft202012Validator) -> Any:
    match = _FENCE.match(content)
    if match:
        content = match.group(1)
    data = json.loads(content)  # ValueError si no es JSON
    validator.validate(data)  # SchemaValidationError si no cumple
    return data


def _ns_to_ms(value: Any) -> int | None:
    return int(value) // 1_000_000 if isinstance(value, int) else None
