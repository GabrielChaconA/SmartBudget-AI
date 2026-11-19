import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from tests.conftest import AUTH, FakeOllama, make_settings


def test_health_ok_when_ollama_up_and_model_downloaded(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.models = ["qwen3:8b", "gemma4:e4b"]

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "up"
    assert body["ollama"] == "up"
    assert body["model"] == "qwen3:8b"
    assert body["model_downloaded"] is True
    assert body["test_models"] == {"gemma4:e4b": True, "gemma4:26b": False}


def test_health_reports_ollama_unavailable(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.down = True

    response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "ollama_unavailable"
    assert body["service"] == "up"
    assert body["ollama"] == "down"
    assert body["model_downloaded"] is None


def test_health_reports_model_not_downloaded(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.models = ["llama3.2:latest"]

    response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "model_not_downloaded"
    assert body["ollama"] == "up"
    assert body["model_downloaded"] is False


def test_health_does_not_require_token(client: TestClient):
    assert client.get("/health").status_code in (200, 503)


@pytest.mark.parametrize("headers", [{}, {"X-AI-Service-Token": "wrong-token-value-123"}])
def test_protected_routes_reject_missing_or_wrong_token(client: TestClient, headers: dict):
    response = client.get("/v1/models", headers=headers)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_models_lists_default_and_test_models(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.models = ["qwen3:8b", "gemma4:26b"]

    response = client.get("/v1/models", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {
        "default": "qwen3:8b",
        "models": [
            {"name": "qwen3:8b", "default": True, "downloaded": True},
            {"name": "gemma4:e4b", "default": False, "downloaded": False},
            {"name": "gemma4:26b", "default": False, "downloaded": True},
        ],
    }


def test_models_returns_uniform_503_when_ollama_down(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.down = True

    response = client.get("/v1/models", headers=AUTH)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "model_unavailable"


def test_changing_model_only_needs_env_var():
    settings = make_settings(ollama_model="gemma4:e4b", ai_allowed_models="")
    assert settings.default_model == "gemma4:e4b"
    assert settings.allowed_models == ["gemma4:e4b"]


def test_untagged_model_is_normalized_to_latest():
    assert make_settings(ollama_model="llama3.2").default_model == "llama3.2:latest"


def test_short_token_is_rejected_at_startup():
    with pytest.raises(ValidationError):
        make_settings(ai_service_token="short")
