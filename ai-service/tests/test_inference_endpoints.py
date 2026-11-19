"""IAL-04: POST /v1/chat y POST /v1/insights."""

import httpx
import pytest
from fastapi.testclient import TestClient

from tests.conftest import AUTH, FakeOllama
from tests.samples import CONTEXT, ollama_reply

CHAT_OK = {"reply": "Este mes llevas 9,000.00 MXN de gastos.", "intent": "spending"}
INSIGHTS_OK = {
    "insights": [
        {
            "title": "Comida al 67 %",
            "message": "Llevas 4,000.00 MXN de 6,000.00 MXN en comida.",
            "category": "budget",
            "priority": "medium",
        }
    ]
}


def chat_body(**overrides):
    body = {"context": CONTEXT, "history": [], "message": "¿Cuánto llevo gastado?", "language": "es"}
    body.update(overrides)
    return body


# ----------------------------------------------------------------- /v1/chat
def test_chat_success(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda request: ollama_reply(CHAT_OK)

    response = client.post("/v1/chat", json=chat_body(), headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["reply"] == CHAT_OK["reply"]
    assert body["intent"] == "spending"
    assert body["prompt_version"] == "chat@1.0"
    assert body["model"] == "qwen3:8b"
    assert body["usage"]["prompt_tokens"] == 900

    sent = fake_ollama.chat_bodies()[0]
    assert sent["messages"][-1] == {"role": "user", "content": "¿Cuánto llevo gastado?"}
    assert "BBVA" in sent["messages"][0]["content"]  # contexto inyectado


def test_chat_sends_history_trimmed_to_limit(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda request: ollama_reply(CHAT_OK)
    history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"mensaje {i}"} for i in range(20)
    ]

    client.post("/v1/chat", json=chat_body(history=history), headers=AUTH)

    contents = [m["content"] for m in fake_ollama.chat_bodies()[0]["messages"]]
    assert "mensaje 19" in contents and "mensaje 8" in contents
    assert "mensaje 7" not in contents  # AI_MAX_HISTORY_MESSAGES=12 por defecto


def test_chat_empty_context_returns_insufficient_data_without_calling_model(
    client: TestClient, fake_ollama: FakeOllama
):
    response = client.post("/v1/chat", json=chat_body(context={}), headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["intent"] == "insufficient_data"
    assert body["model"] is None
    assert "no tengo suficientes datos" in body["reply"].lower()
    assert fake_ollama.chat_bodies() == []


def test_chat_english(client: TestClient, fake_ollama: FakeOllama):
    response = client.post("/v1/chat", json=chat_body(context={}, language="en"), headers=AUTH)

    assert "enough data" in response.json()["reply"]


def test_chat_model_down_returns_uniform_503(client: TestClient, fake_ollama: FakeOllama):
    def refuse(request):
        raise httpx.ConnectError("refused", request=request)

    fake_ollama.chat_handler = refuse

    response = client.post("/v1/chat", json=chat_body(), headers=AUTH)

    assert response.status_code == 503
    assert response.json() == {
        "error": {"code": "model_unavailable", "message": "Ollama no está disponible", "retryable": True}
    }


def test_chat_model_not_downloaded_returns_503(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.models = []

    response = client.post("/v1/chat", json=chat_body(), headers=AUTH)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "model_unavailable"


def test_chat_timeout_returns_uniform_504(client: TestClient, fake_ollama: FakeOllama):
    def slow(request):
        raise httpx.ReadTimeout("timed out", request=request)

    fake_ollama.chat_handler = slow

    response = client.post("/v1/chat", json=chat_body(), headers=AUTH)

    assert response.status_code == 504
    assert response.json()["error"]["code"] == "model_timeout"


def test_chat_invalid_model_output_returns_503(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda request: ollama_reply({"respuesta": "sin schema"})

    response = client.post("/v1/chat", json=chat_body(), headers=AUTH)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "invalid_model_output"


def test_chat_requires_token(client: TestClient):
    assert client.post("/v1/chat", json=chat_body()).status_code == 401


def test_chat_validation_error_does_not_echo_input(client: TestClient):
    response = client.post(
        "/v1/chat",
        json=chat_body(message="", context={**CONTEXT, "monthly_income": "secreto-123"}),
        headers=AUTH,
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "secreto-123" not in response.text


@pytest.mark.parametrize("model", ["gemma4:e4b", "gemma4:26b"])
def test_chat_with_allowed_test_model(client: TestClient, fake_ollama: FakeOllama, model: str):
    fake_ollama.models = ["qwen3:8b", model]
    fake_ollama.chat_handler = lambda request: ollama_reply(CHAT_OK)

    response = client.post("/v1/chat", json=chat_body(), headers={**AUTH, "X-AI-Model": model})

    assert response.status_code == 200
    assert response.json()["model"] == model
    assert fake_ollama.chat_bodies()[0]["model"] == model


def test_chat_with_model_not_allowed(client: TestClient):
    response = client.post("/v1/chat", json=chat_body(), headers={**AUTH, "X-AI-Model": "llama3:70b"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "model_not_allowed"


# ------------------------------------------------------------- /v1/insights
def test_insights_success(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda request: ollama_reply(INSIGHTS_OK)

    response = client.post("/v1/insights", json={"context": CONTEXT, "language": "es"}, headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["insights"] == INSIGHTS_OK["insights"]
    assert body["prompt_version"] == "insights@1.0"
    assert body["reason"] is None
    sent = fake_ollama.chat_bodies()[0]
    assert sent["format"]["properties"]["insights"]["maxItems"] == 3


def test_insights_empty_context(client: TestClient, fake_ollama: FakeOllama):
    response = client.post("/v1/insights", json={"context": {}, "language": "es"}, headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["insights"] == []
    assert body["reason"]
    assert fake_ollama.chat_bodies() == []


@pytest.mark.parametrize(
    "bad",
    [
        {"insights": []},  # menos de 1
        {"insights": INSIGHTS_OK["insights"] * 4},  # más de 3
        {"insights": [{**INSIGHTS_OK["insights"][0], "category": "lotería"}]},
    ],
    ids=["empty", "too-many", "bad-category"],
)
def test_insights_invalid_output_returns_empty_list_with_reason(
    client: TestClient, fake_ollama: FakeOllama, bad: dict
):
    fake_ollama.chat_handler = lambda request: ollama_reply(bad)

    response = client.post("/v1/insights", json={"context": CONTEXT}, headers=AUTH)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "model_error"
    assert body["insights"] == []
    assert body["reason"]
    assert len(fake_ollama.chat_bodies()) == 2  # reintentó una vez


def test_insights_model_down_returns_503(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.down = True

    response = client.post("/v1/insights", json={"context": CONTEXT}, headers=AUTH)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "model_unavailable"


def test_openapi_documents_inference_endpoints(client: TestClient):
    spec = client.get("/openapi.json").json()

    assert "/v1/chat" in spec["paths"] and "/v1/insights" in spec["paths"]
    schemas = spec["components"]["schemas"]
    assert {"ChatRequest", "ChatResponse", "InsightsRequest", "InsightsResponse", "ErrorResponse"} <= set(schemas)
