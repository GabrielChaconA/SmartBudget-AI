"""IAL-05: POST /v1/purchase-check y la detección de pagos dentro de /v1/chat."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from tests.conftest import AUTH, FakeOllama
from tests.samples import CONTEXT, ollama_reply

DISCLAIMER_ES = "Es solo una sugerencia: la decisión es tuya."


def check(client: TestClient, amount, **extra):
    body = {"context": CONTEXT, "amount": amount, "description": "TV", "language": "es", **extra}
    return client.post("/v1/purchase-check", json=body, headers=AUTH)


def test_purchase_check_uses_model_only_for_wording(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply(
        {"message": "Puedes pagarlo, pero equivale al 40.0% de tu ingreso y te quedarían 11,701.00 MXN."}
    )

    response = check(client, 8000)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["verdict"] == "precaucion"
    assert [r["code"] for r in body["reasons"]] == ["high_income_share", "exceeds_budget"]
    assert body["reasons"][0]["message"] == "El pago equivale al 40.0% de tu ingreso mensual."
    assert body["metrics"]["free_after_purchase"] == 11701.0
    assert body["metrics"]["pct_of_monthly_income"] == 40.0
    assert body["metrics"]["commitments"] == [{"name": "Netflix", "amount": 299.0, "date": "2026-11-25"}]
    assert body["message_source"] == "model"
    assert body["message"].endswith(DISCLAIMER_ES)
    assert body["prompt_version"] == "purchase_check@1.0"
    assert body["model"] == "qwen3:8b"

    # Al modelo se le pasan cifras y veredicto ya calculados, no el contexto completo.
    prompt = fake_ollama.chat_bodies()[0]["messages"][-1]["content"]
    assert "Con precaución" in prompt and "11,701.00 MXN" in prompt
    assert "BBVA" not in prompt


def test_verdict_does_not_depend_on_model(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply({"message": "¡Claro, cómpralo sin problema!"})

    body = check(client, 20000).json()

    assert body["verdict"] == "no_recomendable"


def test_invented_figures_fall_back_to_template(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply({"message": "Te quedarían 50,000.00 MXN, sin problema."})

    body = check(client, 1500).json()

    assert body["verdict"] == "recomendable"
    assert body["message_source"] == "template"
    assert "50,000" not in body["message"]
    assert body["message"] == (
        "Según tus números, puedes hacer este pago de 1,500.00 MXN: te quedarían "
        f"18,201.00 MXN libres hasta el 30/11/2026. {DISCLAIMER_ES}"
    )
    assert body["model"] is None


def test_execution_claims_fall_back_to_template(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply({"message": "Listo, ya pagué la TV por ti."})

    body = check(client, 1500).json()

    assert body["message_source"] == "template"
    assert "pagué" not in body["message"]


@pytest.mark.parametrize("failure", ["down", "timeout", "invalid"])
def test_model_failure_still_returns_deterministic_verdict(
    client: TestClient, fake_ollama: FakeOllama, failure: str
):
    def handler(request):
        if failure == "down":
            raise httpx.ConnectError("refused", request=request)
        if failure == "timeout":
            raise httpx.ReadTimeout("slow", request=request)
        return ollama_reply({"no": "schema"})

    fake_ollama.chat_handler = handler

    response = check(client, 8000)

    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] == "precaucion"
    assert body["message_source"] == "template"
    assert body["message"].endswith(DISCLAIMER_ES)


def test_missing_income_is_reported_instead_of_assumed(client: TestClient, fake_ollama: FakeOllama):
    response = check(client, 1000, context={**CONTEXT, "monthly_income": None})

    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["verdict"] is None
    assert "monthly_income" in body["missing_data"]
    assert body["metrics"]["pct_of_monthly_income"] is None
    assert "tu ingreso mensual" in body["message"]
    assert fake_ollama.chat_bodies() == []


def test_several_missing_fields_listed(client: TestClient):
    body = check(client, 1000, context={"accounts": []}).json()

    assert body["status"] == "insufficient_data"
    assert set(body["missing_data"]) >= {"accounts", "monthly_income", "payday"}
    assert "el saldo de tus cuentas, tu ingreso mensual y tu día de pago" in body["message"]


@pytest.mark.parametrize("amount", [0, -5, "abc"])
def test_invalid_amount_is_rejected(client: TestClient, amount):
    assert check(client, amount).status_code == 422


def test_english(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.down = True

    body = check(client, 1500, language="en").json()

    assert body["message"].endswith("This is only a suggestion: the decision is yours.")
    assert body["reasons"][0]["message"].startswith("The payment fits")


def test_purchase_check_requires_token(client: TestClient):
    assert client.post("/v1/purchase-check", json={"amount": 1}).status_code == 401


# ---------------------------------------------------------- dentro del chat
def test_chat_detects_payment_intent(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply(
        {"message": "Puedes pagar la TV, pero te pasarías del presupuesto del mes."}
    )

    response = client.post(
        "/v1/chat",
        json={"context": CONTEXT, "history": [], "message": "quiero pagar 8,000 de una TV", "language": "es"},
        headers=AUTH,
    )

    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "purchase_check"
    assert body["prompt_version"] == "purchase_check@1.0"
    assert body["purchase"]["verdict"] == "precaucion"
    assert body["purchase"]["metrics"]["amount"] == 8000.0
    assert body["reply"] == body["purchase"]["message"]
    assert "(una TV)" in fake_ollama.chat_bodies()[0]["messages"][-1]["content"]


def test_chat_without_amount_uses_normal_chat(client: TestClient, fake_ollama: FakeOllama):
    fake_ollama.chat_handler = lambda r: ollama_reply({"reply": "¿De cuánto sería el pago?", "intent": "purchase_check"})

    body = client.post(
        "/v1/chat",
        json={"context": CONTEXT, "message": "quiero comprar una TV", "language": "es"},
        headers=AUTH,
    ).json()

    assert body["intent"] == "purchase_check"
    assert body["purchase"] is None
    assert json.loads(json.dumps(fake_ollama.chat_bodies()[0]["format"]))["required"] == ["reply", "intent"]
