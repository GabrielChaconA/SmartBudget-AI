"""IAL-02: cliente de Ollama con salida estructurada, contra un Ollama simulado."""

import asyncio
import json
import logging
from typing import Literal

import httpx
import pytest
from pydantic import BaseModel

from app.services.exceptions import InvalidModelOutput, ModelTimeout, ModelUnavailable
from app.services.ollama_client import OllamaClient
from tests.conftest import FakeOllama, make_settings

pytestmark = pytest.mark.anyio

SECRET_USER_TEXT = "mi saldo es 12345.67 en la cuenta Banorte"


class Answer(BaseModel):
    reply: str
    mood: Literal["happy", "sad"]


SCHEMA = {
    "type": "object",
    "properties": {"reply": {"type": "string"}, "mood": {"enum": ["happy", "sad"]}},
    "required": ["reply", "mood"],
    "additionalProperties": False,
}
MESSAGES = [
    {"role": "system", "content": "Eres un asistente."},
    {"role": "user", "content": SECRET_USER_TEXT},
]


def chat_ok(content: str | dict) -> httpx.Response:
    if isinstance(content, dict):
        content = json.dumps(content)
    return httpx.Response(
        200,
        json={
            "model": "qwen3:8b",
            "message": {"role": "assistant", "content": content},
            "done": True,
            "prompt_eval_count": 42,
            "eval_count": 7,
            "load_duration": 5_000_000,
        },
    )


def sequence(*responses):
    items = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        item = items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return handler


@pytest.fixture
def anyio_backend():
    return "asyncio"


def make_client(fake: FakeOllama, **overrides) -> OllamaClient:
    return OllamaClient(make_settings(**overrides), transport=httpx.MockTransport(fake))


async def test_valid_response_is_parsed_and_validated(fake_ollama: FakeOllama, caplog):
    fake_ollama.capabilities["qwen3:8b"] = ["completion", "thinking"]
    fake_ollama.chat_handler = sequence(chat_ok({"reply": "hola", "mood": "happy"}))
    client = make_client(fake_ollama)

    with caplog.at_level(logging.INFO, logger="app.ollama"):
        result = await client.chat_structured(MESSAGES, Answer, schema=SCHEMA, task="test")

    assert result.data == Answer(reply="hola", mood="happy")
    assert result.model == "qwen3:8b"
    assert (result.prompt_tokens, result.completion_tokens, result.attempts) == (42, 7, 1)

    body = fake_ollama.chat_bodies()[0]
    assert body["format"] == SCHEMA
    assert body["stream"] is False
    assert body["think"] is False  # el modelo soporta thinking -> se desactiva
    assert body["messages"] == MESSAGES

    log = caplog.text
    assert "model=qwen3:8b" in log and "duration_ms=" in log
    assert "prompt_tokens=42" in log and "completion_tokens=7" in log
    assert "12345" not in log and "Banorte" not in log  # sin datos financieros


async def test_think_flag_not_sent_when_model_has_no_thinking(fake_ollama: FakeOllama):
    fake_ollama.capabilities["qwen3:8b"] = ["completion"]
    fake_ollama.chat_handler = sequence(chat_ok({"reply": "x", "mood": "sad"}))

    await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert "think" not in fake_ollama.chat_bodies()[0]


async def test_schema_from_pydantic_model_when_none_given(fake_ollama: FakeOllama):
    fake_ollama.chat_handler = sequence(chat_ok({"reply": "x", "mood": "sad"}))

    await make_client(fake_ollama).chat_structured(MESSAGES, Answer)

    assert fake_ollama.chat_bodies()[0]["format"] == Answer.model_json_schema()


async def test_invalid_json_is_retried_once_then_succeeds(fake_ollama: FakeOllama):
    fake_ollama.chat_handler = sequence(
        chat_ok("esto no es json"), chat_ok({"reply": "ok", "mood": "happy"})
    )

    result = await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert result.attempts == 2
    assert result.data.reply == "ok"


@pytest.mark.parametrize(
    "bad",
    ["{not json", json.dumps({"reply": "x", "mood": "angry"}), json.dumps({"reply": "x"})],
    ids=["invalid-json", "enum-violation", "missing-field"],
)
async def test_invalid_output_twice_raises_invalid_model_output(fake_ollama: FakeOllama, bad: str):
    fake_ollama.chat_handler = sequence(chat_ok(bad), chat_ok(bad))

    with pytest.raises(InvalidModelOutput):
        await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert len(fake_ollama.chat_bodies()) == 2  # un intento + un reintento, nada más


async def test_json_inside_code_fence_is_accepted(fake_ollama: FakeOllama):
    fake_ollama.chat_handler = sequence(chat_ok('```json\n{"reply": "x", "mood": "happy"}\n```'))

    result = await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert result.data.mood == "happy"


async def test_read_timeout_raises_model_timeout_without_retry(fake_ollama: FakeOllama):
    fake_ollama.chat_handler = sequence(httpx.ReadTimeout("timed out"))

    with pytest.raises(ModelTimeout):
        await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert len(fake_ollama.chat_bodies()) == 1


async def test_configurable_total_timeout(fake_ollama: FakeOllama):
    async def slow_transport(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/chat":
            await asyncio.sleep(2)
        return fake_ollama(request)

    client = OllamaClient(
        make_settings(ollama_timeout_seconds=0.05), transport=httpx.MockTransport(slow_transport)
    )

    with pytest.raises(ModelTimeout):
        await client.chat_structured(MESSAGES, Answer, schema=SCHEMA)


async def test_ollama_down_raises_model_unavailable_after_bounded_retries(fake_ollama: FakeOllama):
    calls = []

    def refuse(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        raise httpx.ConnectError("connection refused", request=request)

    fake_ollama.chat_handler = refuse

    with pytest.raises(ModelUnavailable):
        await make_client(fake_ollama, ollama_max_retries=2).chat_structured(
            MESSAGES, Answer, schema=SCHEMA
        )

    assert len(calls) == 3  # 1 + OLLAMA_MAX_RETRIES


async def test_ollama_completely_down_fails_before_chat(fake_ollama: FakeOllama):
    fake_ollama.down = True

    with pytest.raises(ModelUnavailable):
        await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)


async def test_server_error_is_retried(fake_ollama: FakeOllama):
    fake_ollama.chat_handler = sequence(
        httpx.Response(500, json={"error": "boom"}), chat_ok({"reply": "x", "mood": "happy"})
    )

    result = await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)

    assert result.data.reply == "x"


async def test_model_not_downloaded_raises_model_unavailable(fake_ollama: FakeOllama):
    fake_ollama.models = []

    with pytest.raises(ModelUnavailable, match="no está descargado"):
        await make_client(fake_ollama).chat_structured(MESSAGES, Answer, schema=SCHEMA)


async def test_override_model_is_used(fake_ollama: FakeOllama):
    fake_ollama.models = ["qwen3:8b", "gemma4:e4b"]
    fake_ollama.chat_handler = sequence(chat_ok({"reply": "x", "mood": "happy"}))

    result = await make_client(fake_ollama).chat_structured(
        MESSAGES, Answer, schema=SCHEMA, model="gemma4:e4b"
    )

    assert result.model == "gemma4:e4b"
    assert fake_ollama.chat_bodies()[0]["model"] == "gemma4:e4b"
