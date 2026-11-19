"""IAL-05: montos, métricas y reglas del veredicto (deterministas, sin modelo)."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from app.schemas.context import FinancialContext
from app.services.purchase.amounts import detect_purchase_intent, parse_number
from app.services.purchase.metrics import PurchaseMetrics, compute_metrics, next_payday
from app.services.purchase.verdict_rules import MissingDataError, Severity, Verdict, evaluate
from tests.samples import CONTEXT

TODAY = date(2026, 11, 19)
D = Decimal


def metrics_for(amount, **ctx_overrides) -> PurchaseMetrics:
    ctx = FinancialContext.model_validate({**CONTEXT, **ctx_overrides})
    return compute_metrics(ctx, D(str(amount)), TODAY)


def base_metrics(**overrides) -> PurchaseMetrics:
    """Métricas sintéticas para probar las reglas en sus límites exactos."""
    values = dict(
        amount=D("1000.00"), currency="MXN", as_of=TODAY,
        liquid_balance=D("20000.00"), monthly_income=D("20000.00"),
        next_payday=date(2026, 11, 30), days_until_payday=11, commitments=(),
        commitments_before_payday=D("0.00"), free_money=D("20000.00"),
        free_after_purchase=D("19000.00"), pct_of_monthly_income=D("5.0"),
        safety_buffer=D("2000.00"), budget_total=D("8000.00"), budget_spent=D("0.00"),
        budget_remaining=D("8000.00"), budget_remaining_after_purchase=D("7000.00"),
        goals_monthly_need=D("0.00"), missing_required=(), missing_optional=(),
    )
    values.update(overrides)
    return PurchaseMetrics(**values)


def codes(reasons) -> list[str]:
    return [r.code for r in reasons]


# ------------------------------------------------------------------ montos
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("8000", "8000"), ("8,000", "8000"), ("8.000", "8000"), ("8,000.50", "8000.50"),
        ("8.000,50", "8000.50"), ("8,5", "8.5"), ("12.50", "12.50"), ("1,234,567", "1234567"),
    ],
)
def test_parse_number(raw, expected):
    assert parse_number(raw) == D(expected)


@pytest.mark.parametrize(
    ("message", "amount", "description"),
    [
        ("quiero pagar 8,000 de una TV", "8000", "una TV"),
        ("¿Puedo comprar una laptop de $15,500.50?", "15500.50", None),
        ("me alcanza para gastar 8 mil en un viaje?", "8000", "un viaje"),
        ("quiero comprar 2 llantas de 3,500 pesos", "3500", None),
        ("pagar 12000 a 12 meses", "12000", None),
        ("I want to buy a TV for $8,000", "8000", None),
        ("can I afford 1.5k on shoes?", "1500", "shoes"),
    ],
)
def test_detect_purchase_intent(message, amount, description):
    intent = detect_purchase_intent(message)
    assert intent is not None
    assert intent.amount == D(amount)
    assert intent.description == description


@pytest.mark.parametrize(
    "message",
    ["¿Cuánto gasté este mes?", "quiero pagar mi tarjeta", "mi ahorro subió 10%", "hola", "¿cuánto puedo gastar?"],
)
def test_no_purchase_intent(message):
    assert detect_purchase_intent(message) is None


# ---------------------------------------------------------------- métricas
@pytest.mark.parametrize(
    ("today", "payday", "expected"),
    [
        (date(2026, 11, 19), 30, date(2026, 11, 30)),
        (date(2026, 11, 30), 30, date(2026, 12, 30)),  # hoy es payday -> el siguiente
        (date(2026, 1, 31), 31, date(2026, 2, 28)),  # mes corto
        (date(2026, 12, 20), 15, date(2027, 1, 15)),  # cambio de año
    ],
)
def test_next_payday(today, payday, expected):
    assert next_payday(today, payday) == expected


def test_metrics_from_sample_context():
    m = metrics_for(8000)

    assert m.liquid_balance == D("20000.00")  # Cartera + BBVA; la tarjeta de crédito no cuenta
    assert m.next_payday == date(2026, 11, 30) and m.days_until_payday == 11
    assert [c.name for c in m.commitments] == ["Netflix"]  # Spotify se cobra después del payday
    assert m.commitments_before_payday == D("299.00")
    assert m.free_money == D("19701.00")
    assert m.free_after_purchase == D("11701.00")
    assert m.pct_of_monthly_income == D("40.0")
    assert m.safety_buffer == D("2000.00")
    assert (m.budget_total, m.budget_spent, m.budget_remaining) == (D("8000.00"), D("5000.00"), D("3000.00"))
    assert m.budget_remaining_after_purchase == D("-5000.00")
    assert m.goals_monthly_need == D("1000.00")  # 6000 restantes / 6 meses
    assert m.missing_required == () and m.missing_optional == ()


def test_commitment_on_payday_counts():
    subs = [{"name": "Renta", "amount": 5000, "next_billing_date": "2026-11-30"}]
    assert metrics_for(100, subscriptions=subs).commitments_before_payday == D("5000.00")


def test_inactive_subscriptions_are_ignored():
    subs = [{"name": "Viejo", "amount": 999, "next_billing_date": "2026-11-20", "status": "cancelled"}]
    assert metrics_for(100, subscriptions=subs).commitments_before_payday == D("0.00")


@pytest.mark.parametrize(
    ("override", "missing"),
    [
        ({"monthly_income": None}, "monthly_income"),
        ({"monthly_income": 0}, "monthly_income"),
        ({"payday": None}, "payday"),
        ({"accounts": []}, "accounts"),
        ({"accounts": [{"name": "Tarjeta", "type": "credit", "balance": -100}]}, "accounts"),
    ],
)
def test_missing_required_data_is_reported_not_assumed(override, missing):
    m = metrics_for(1000, **override)

    assert missing in m.missing_required
    with pytest.raises(MissingDataError):
        evaluate(m)


def test_missing_optional_data_is_reported():
    m = metrics_for(
        1000,
        budgets=[],
        subscriptions=[{"name": "Sin fecha", "amount": 100}],
        goals=[{"name": "Casa", "target_amount": 100000}],
    )

    assert set(m.missing_optional) == {"budgets", "subscription_dates", "goal_deadlines"}
    assert m.budget_remaining is None
    assert m.missing_required == ()


# ------------------------------------------------------------------ reglas
@pytest.mark.parametrize(
    ("amount", "verdict", "expected_codes"),
    [
        (1500, Verdict.RECOMENDABLE, ["within_means"]),
        (8000, Verdict.PRECAUCION, ["high_income_share", "exceeds_budget"]),
        (19000, Verdict.NO_RECOMENDABLE, ["low_buffer", "very_high_income_share", "exceeds_budget", "goals_at_risk"]),
        (20000, Verdict.NO_RECOMENDABLE, ["exceeds_free_money", "very_high_income_share", "exceeds_budget", "goals_at_risk"]),
    ],
)
def test_verdict_on_sample_context(amount, verdict, expected_codes):
    result, reasons = evaluate(metrics_for(amount))

    assert result is verdict
    assert codes(reasons) == expected_codes


def test_same_numbers_always_same_verdict():
    results = {evaluate(metrics_for(8000)) for _ in range(20)}
    assert len(results) == 1


@pytest.mark.parametrize(
    ("free_after", "expected"),
    [("-0.01", "exceeds_free_money"), ("0.00", "low_buffer"), ("1999.99", "low_buffer"), ("2000.00", None)],
)
def test_free_money_and_buffer_limits(free_after, expected):
    _, reasons = evaluate(base_metrics(free_after_purchase=D(free_after)))
    found = [c for c in codes(reasons) if c in ("exceeds_free_money", "low_buffer")]
    assert found == ([expected] if expected else [])


@pytest.mark.parametrize(
    ("pct", "verdict", "code"),
    [
        ("24.9", Verdict.RECOMENDABLE, "within_means"),
        ("25.0", Verdict.PRECAUCION, "high_income_share"),
        ("49.9", Verdict.PRECAUCION, "high_income_share"),
        ("50.0", Verdict.NO_RECOMENDABLE, "very_high_income_share"),
    ],
)
def test_income_share_limits(pct, verdict, code):
    result, reasons = evaluate(base_metrics(pct_of_monthly_income=D(pct)))
    assert result is verdict
    assert codes(reasons) == [code]


@pytest.mark.parametrize(("after", "flagged"), [("-0.01", True), ("0.00", False)])
def test_budget_limit(after, flagged):
    _, reasons = evaluate(base_metrics(budget_remaining_after_purchase=D(after)))
    assert ("exceeds_budget" in codes(reasons)) is flagged


def test_unknown_budget_does_not_trigger_rule():
    _, reasons = evaluate(base_metrics(budget_remaining_after_purchase=None))
    assert codes(reasons) == ["within_means"]


@pytest.mark.parametrize(
    ("need", "free_after", "flagged"),
    [("0.00", "100.00", False), ("5000.00", "4999.99", True), ("5000.00", "5000.00", False)],
)
def test_goals_limit(need, free_after, flagged):
    m = base_metrics(goals_monthly_need=D(need), free_after_purchase=D(free_after), safety_buffer=D("0"))
    _, reasons = evaluate(m)
    assert ("goals_at_risk" in codes(reasons)) is flagged


def test_block_wins_over_caution():
    m = base_metrics(free_after_purchase=D("-1"), budget_remaining_after_purchase=D("-1"))
    verdict, reasons = evaluate(m)
    assert verdict is Verdict.NO_RECOMENDABLE
    assert {r.severity for r in reasons} == {Severity.BLOCK, Severity.CAUTION}


def test_rules_do_not_mutate_metrics():
    m = base_metrics()
    evaluate(m)
    assert m == replace(m)
