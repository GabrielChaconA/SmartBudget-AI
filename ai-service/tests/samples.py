"""Datos de ejemplo (ficticios) con la forma que enviará FinancialContextBuilder (SBI-10)."""

import json
from typing import Any

import httpx

CONTEXT: dict[str, Any] = {
    "as_of": "2026-11-19",
    "currency": "MXN",
    "monthly_income": "20000.00",
    "payday": 30,
    "month_income": 20000,
    "month_expenses": 9000,
    "accounts": [
        {"name": "Cartera", "type": "cash", "balance": "2000.00"},
        {"name": "BBVA", "type": "bank", "balance": 18000},
        {"name": "Tarjeta", "type": "credit", "balance": -5000},
    ],
    "subscriptions": [
        {"name": "Netflix", "amount": 299, "billing_cycle": "monthly", "next_billing_date": "2026-11-25"},
        {"name": "Spotify", "amount": 129, "billing_cycle": "monthly", "next_billing_date": "2026-12-05"},
    ],
    "budgets": [
        {"category": "Comida", "amount": 6000, "spent": 4000},
        {"category": "Entretenimiento", "amount": 2000, "spent": 1000},
    ],
    "goals": [
        {"name": "Viaje", "target_amount": 12000, "current_amount": 6000, "deadline": "2027-05-19", "status": "active"}
    ],
    "recent_transactions": [
        {"date": "2026-11-18 14:30:00", "type": "expense", "amount": 450, "category": "Comida", "description": "Súper"}
    ],
}


def ollama_reply(data: dict[str, Any]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "qwen3:8b",
            "message": {"role": "assistant", "content": json.dumps(data, ensure_ascii=False)},
            "done": True,
            "prompt_eval_count": 900,
            "eval_count": 60,
        },
    )
