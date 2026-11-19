"""Única pieza del sistema que habla con Ollama."""

from __future__ import annotations

import logging

import httpx

from app.config import Settings, normalize_model_name
from app.services.exceptions import ModelUnavailable

logger = logging.getLogger("app.ollama")


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

    async def aclose(self) -> None:
        await self._http.aclose()

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
