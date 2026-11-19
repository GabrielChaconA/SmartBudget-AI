"""Fixtures compartidas. Ollama siempre se simula con httpx.MockTransport:
ninguna prueba necesita Ollama real ni red."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.ollama_client import OllamaClient

TEST_TOKEN = "test-token-0123456789abcdef"
AUTH = {"X-AI-Service-Token": TEST_TOKEN}

Handler = Callable[[httpx.Request], httpx.Response]


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "ollama_host": "http://ollama.test",
        "ollama_model": "qwen3:8b",
        "ai_allowed_models": "gemma4:e4b,gemma4:26b",
        "ai_service_token": TEST_TOKEN,
        "ollama_timeout_seconds": 2,
        "ollama_retry_backoff_seconds": 0,
        "log_level": "INFO",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)  # type: ignore[call-arg]


def tags_response(*names: str) -> httpx.Response:
    return httpx.Response(200, json={"models": [{"name": n, "model": n} for n in names]})


class FakeOllama:
    """Router mínimo que imita la API HTTP de Ollama."""

    def __init__(self) -> None:
        self.models: list[str] = ["qwen3:8b"]
        self.capabilities: dict[str, list[str]] = {}
        self.chat_handler: Handler | None = None
        self.down = False
        self.requests: list[httpx.Request] = []

    def chat_bodies(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requests if r.url.path == "/api/chat"]

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.down:
            raise httpx.ConnectError("connection refused", request=request)
        path = request.url.path
        if path == "/api/tags":
            return tags_response(*self.models)
        if path == "/api/show":
            name = json.loads(request.content)["model"]
            if name not in self.models:
                return httpx.Response(404, json={"error": f"model '{name}' not found"})
            caps = self.capabilities.get(name, ["completion"])
            return httpx.Response(200, json={"capabilities": caps})
        if path == "/api/chat":
            assert self.chat_handler is not None, "chat_handler no configurado"
            return self.chat_handler(request)
        return httpx.Response(404, json={"error": "not found"})


@pytest.fixture
def fake_ollama() -> FakeOllama:
    return FakeOllama()


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def client(settings: Settings, fake_ollama: FakeOllama) -> Iterator[TestClient]:
    ollama = OllamaClient(settings, transport=httpx.MockTransport(fake_ollama))
    app = create_app(settings, ollama=ollama)
    with TestClient(app) as test_client:
        yield test_client
