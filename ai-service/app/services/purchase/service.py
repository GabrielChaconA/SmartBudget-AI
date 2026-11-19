"""Evaluación de pagos "Quiero pagar X".

1. Calcula las métricas en Python (metrics.py).
2. Decide el veredicto con reglas (verdict_rules.py).
3. Pide al modelo SOLO la redacción del mensaje a partir de cifras y veredicto ya
   calculados. Si el texto trae cifras que no salen de los cálculos, afirma haber
   movido dinero, o el modelo falla, se usa un mensaje de plantilla.
4. Siempre agrega el aviso de que es una sugerencia y la decisión es del usuario.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from decimal import Decimal
from typing import Any

from app.schemas.common import Usage
from app.schemas.context import FinancialContext
from app.schemas.purchase import (
    CommitmentOut,
    PurchaseCheckResponse,
    PurchaseMessageOutput,
    PurchaseMetricsOut,
    PurchaseReasonOut,
)
from app.services.exceptions import InvalidModelOutput, ModelTimeout, ModelUnavailable
from app.services.ollama_client import OllamaClient
from app.services.prompt_loader import PromptRegistry, money, pct
from app.services.purchase.amounts import find_numbers
from app.services.purchase.metrics import PurchaseMetrics, compute_metrics
from app.services.purchase.verdict_rules import DEFAULT_THRESHOLDS, evaluate

logger = logging.getLogger("app.purchase")

TASK = "purchase_check"

# Frases en las que el modelo afirma haber ejecutado (o que ejecutará) un movimiento.
_EXECUTION_CLAIMS = re.compile(
    r"\b(ya (?:pagu[eé]|transfer[ií]|realic[eé])|he (?:pagado|transferido|realizado el pago)|"
    r"realizar[eé] el pago|proceder[eé] a pagar|voy a (?:pagar|transferir)|"
    r"i(?:'ve| have) (?:paid|transferred|made the payment)|i will (?:pay|transfer)|i'll (?:pay|transfer))\b",
    re.IGNORECASE,
)

METRIC_KEYS = (
    "amount",
    "liquid_balance",
    "commitments_before_payday",
    "free_money",
    "free_after_purchase",
    "pct_of_monthly_income",
    "next_payday",
    "budget_remaining",
    "goals_monthly_need",
)


def format_date(value: date | None, language: str) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y") if language == "es" else value.isoformat()


def formatted_values(m: PurchaseMetrics, language: str) -> dict[str, str]:
    """Cifras ya formateadas para los textos y el prompt (siempre de los cálculos)."""
    cur = m.currency
    return {
        "amount": money(m.amount, cur),
        "liquid_balance": money(m.liquid_balance, cur),
        "commitments_before_payday": money(m.commitments_before_payday, cur),
        "commitments": money(m.commitments_before_payday, cur),
        "free_money": money(m.free_money, cur),
        "free_after_purchase": money(m.free_after_purchase, cur),
        "free_after": money(m.free_after_purchase, cur),
        "pct_of_monthly_income": pct(m.pct_of_monthly_income),
        "pct_income": pct(m.pct_of_monthly_income),
        "next_payday": format_date(m.next_payday, language),
        "days_until_payday": str(m.days_until_payday) if m.days_until_payday is not None else "—",
        "buffer": money(m.safety_buffer, cur),
        "budget_remaining": money(m.budget_remaining, cur),
        "goals_monthly_need": money(m.goals_monthly_need, cur),
        "goals_need": money(m.goals_monthly_need, cur),
    }


def allowed_numbers(m: PurchaseMetrics) -> set[Decimal]:
    values: list[Decimal] = [Decimal(0), Decimal(len(m.commitments))]
    for v in (
        m.amount, m.liquid_balance, m.monthly_income, m.commitments_before_payday, m.free_money,
        m.free_after_purchase, m.pct_of_monthly_income, m.safety_buffer, m.budget_total,
        m.budget_spent, m.budget_remaining, m.budget_remaining_after_purchase, m.goals_monthly_need,
    ):
        if v is not None:
            values.append(v)
    values.extend(c.amount for c in m.commitments)
    if m.days_until_payday is not None:
        values.append(Decimal(m.days_until_payday))
    for d in [m.next_payday, m.as_of, *(c.date for c in m.commitments)]:
        if d is not None:
            values.extend(Decimal(x) for x in (d.day, d.month, d.year))

    allowed: set[Decimal] = set()
    for v in values:
        for candidate in (v, abs(v)):
            allowed.add(candidate.quantize(Decimal("0.01")))
            allowed.add(candidate.quantize(Decimal("1")).quantize(Decimal("0.01")))
    return allowed


def is_grounded(message: str, allowed: set[Decimal]) -> bool:
    """True si todas las cifras del texto salen de los cálculos."""
    return all(t.value.quantize(Decimal("0.01")) in allowed for t in find_numbers(message))


def metrics_out(m: PurchaseMetrics) -> PurchaseMetricsOut:
    return PurchaseMetricsOut(
        amount=m.amount,
        currency=m.currency,
        as_of=m.as_of,
        liquid_balance=m.liquid_balance,
        monthly_income=m.monthly_income,
        next_payday=m.next_payday,
        days_until_payday=m.days_until_payday,
        commitments=[CommitmentOut(name=c.name, amount=c.amount, date=c.date) for c in m.commitments],
        commitments_before_payday=m.commitments_before_payday,
        free_money=m.free_money,
        free_after_purchase=m.free_after_purchase,
        pct_of_monthly_income=m.pct_of_monthly_income,
        safety_buffer=m.safety_buffer,
        budget_total=m.budget_total,
        budget_spent=m.budget_spent,
        budget_remaining=m.budget_remaining,
        budget_remaining_after_purchase=m.budget_remaining_after_purchase,
        goals_monthly_need=m.goals_monthly_need,
    )


def _join(items: list[str], language: str) -> str:
    if len(items) <= 1:
        return "".join(items)
    last = " y " if language == "es" else " and "
    return ", ".join(items[:-1]) + last + items[-1]


async def evaluate_purchase(
    ctx: FinancialContext,
    amount: Decimal,
    description: str | None,
    language: str,
    *,
    ollama: OllamaClient,
    prompts: PromptRegistry,
    model: str,
    today: date | None = None,
) -> PurchaseCheckResponse:
    today = today or ctx.as_of or date.today()
    m = compute_metrics(ctx, amount, today, buffer_income_pct=DEFAULT_THRESHOLDS.buffer_income_pct)
    values = formatted_values(m, language)
    version = prompts.version(TASK)
    missing = list(m.missing_required) + list(m.missing_optional)

    if m.missing_required:
        labels = [prompts.text(TASK, language, f"missing.{key}") for key in m.missing_required]
        return PurchaseCheckResponse(
            status="insufficient_data",
            verdict=None,
            reasons=[],
            metrics=metrics_out(m),
            message=prompts.text(TASK, language, "insufficient_data", missing=_join(labels, language)),
            message_source="template",
            prompt_version=version,
            missing_data=missing,
        )

    verdict, reasons = evaluate(m)
    reasons_out = [
        PurchaseReasonOut(
            code=r.code,
            severity=r.severity.value,
            message=prompts.text(TASK, language, f"reasons.{r.code}", **values),
        )
        for r in reasons
    ]

    variables: dict[str, Any] = {
        "amount": values["amount"],
        "description": description,
        "verdict_label": prompts.text(TASK, language, f"verdicts.{verdict.value}"),
        "reasons": [r.message for r in reasons_out],
        "metrics": [
            {"label": prompts.text(TASK, language, f"metrics.{key}"), "value": values[key]}
            for key in METRIC_KEYS
            if values[key] != "—"
        ],
    }
    rendered = prompts.render(TASK, language, variables=variables)

    message: str | None = None
    used_model: str | None = None
    usage = None
    try:
        result = await ollama.chat_structured(
            rendered.messages, PurchaseMessageOutput, schema=rendered.schema, model=model, task=TASK
        )
        text = result.data.message.strip()
        if not is_grounded(text, allowed_numbers(m)):
            logger.warning("purchase.message ungrounded_figures model=%s", result.model)
        elif _EXECUTION_CLAIMS.search(text):
            logger.warning("purchase.message execution_claim model=%s", result.model)
        else:
            message, used_model, usage = text, result.model, Usage.from_result(result)
    except (ModelUnavailable, ModelTimeout, InvalidModelOutput) as exc:
        # El veredicto no depende del modelo: seguimos con un mensaje de plantilla.
        logger.warning("purchase.message model_failed code=%s", exc.code)

    source = "model" if message else "template"
    if message is None:
        message = prompts.text(TASK, language, f"fallback.{verdict.value}", **values)
    disclaimer = prompts.text(TASK, language, "disclaimer")

    return PurchaseCheckResponse(
        status="ok",
        verdict=verdict.value,
        reasons=reasons_out,
        metrics=metrics_out(m),
        message=f"{message} {disclaimer}",
        message_source=source,
        prompt_version=version,
        model=used_model,
        usage=usage,
        missing_data=missing,
    )
