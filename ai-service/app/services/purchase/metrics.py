"""Métricas deterministas para evaluar un pago. Todo en Python con Decimal, sin LLM.

Definiciones:
- liquid_balance: suma de saldos de cuentas que no son crédito/préstamo/inversión.
- next_payday: siguiente fecha (estrictamente posterior a hoy) con el día ``payday``;
  si el mes es más corto se usa su último día.
- commitments_before_payday: suscripciones activas con next_billing_date entre hoy y
  el próximo payday (inclusive: un cargo el mismo día de pago puede llegar antes que
  el sueldo).
- free_money = liquid_balance - commitments_before_payday.
- pct_of_monthly_income = amount / monthly_income * 100.
- budget_*: suma de presupuestos del mes (amount) y de lo gastado (spent).
- goals_monthly_need: lo que las metas activas con fecha límite necesitan por mes
  (restante / meses que faltan, mínimo 1).
- safety_buffer: colchón sugerido = buffer_income_pct % del ingreso mensual.

Si falta un dato necesario se registra en ``missing_required`` / ``missing_optional``
en lugar de suponer un valor.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.schemas.context import FinancialContext

NON_LIQUID_ACCOUNT_TYPES = frozenset({"credit", "credit_card", "loan", "debt", "investment"})
INACTIVE_STATUSES = frozenset({"cancelled", "canceled", "paused", "inactive", "completed", "archived"})

CENT = Decimal("0.01")
TENTH = Decimal("0.1")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Commitment:
    name: str
    amount: Decimal
    date: date


@dataclass(frozen=True)
class PurchaseMetrics:
    amount: Decimal
    currency: str
    as_of: date
    liquid_balance: Decimal | None
    monthly_income: Decimal | None
    next_payday: date | None
    days_until_payday: int | None
    commitments: tuple[Commitment, ...]
    commitments_before_payday: Decimal | None
    free_money: Decimal | None
    free_after_purchase: Decimal | None
    pct_of_monthly_income: Decimal | None
    safety_buffer: Decimal | None
    budget_total: Decimal | None
    budget_spent: Decimal | None
    budget_remaining: Decimal | None
    budget_remaining_after_purchase: Decimal | None
    goals_monthly_need: Decimal
    missing_required: tuple[str, ...]
    missing_optional: tuple[str, ...]


def next_payday(today: date, payday: int) -> date:
    def in_month(year: int, month: int) -> date:
        return date(year, month, min(payday, calendar.monthrange(year, month)[1]))

    candidate = in_month(today.year, today.month)
    if candidate > today:
        return candidate
    year, month = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return in_month(year, month)


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)


def compute_metrics(
    ctx: FinancialContext,
    amount: Decimal,
    today: date,
    *,
    buffer_income_pct: Decimal = Decimal("10"),
) -> PurchaseMetrics:
    amount = money(amount)
    missing_required: list[str] = []
    missing_optional: list[str] = []

    # --- saldo líquido
    liquid_accounts = [a for a in ctx.accounts if (a.type or "").lower() not in NON_LIQUID_ACCOUNT_TYPES]
    liquid_balance = money(sum((a.balance for a in liquid_accounts), Decimal(0))) if liquid_accounts else None
    if liquid_balance is None:
        missing_required.append("accounts")

    # --- ingreso
    income = ctx.monthly_income if ctx.monthly_income and ctx.monthly_income > 0 else None
    if income is None:
        missing_required.append("monthly_income")

    # --- payday y compromisos
    payday_date = next_payday(today, ctx.payday) if ctx.payday else None
    if payday_date is None:
        missing_required.append("payday")

    commitments: list[Commitment] = []
    commitments_total: Decimal | None = None
    if payday_date is not None:
        for sub in ctx.subscriptions:
            if (sub.status or "").lower() in INACTIVE_STATUSES:
                continue
            if sub.next_billing_date is None:
                if "subscription_dates" not in missing_optional:
                    missing_optional.append("subscription_dates")
                continue
            if today <= sub.next_billing_date <= payday_date:
                commitments.append(Commitment(sub.name, money(sub.amount), sub.next_billing_date))
        commitments.sort(key=lambda c: c.date)
        commitments_total = money(sum((c.amount for c in commitments), Decimal(0)))

    free_money = (
        money(liquid_balance - commitments_total)
        if liquid_balance is not None and commitments_total is not None
        else None
    )
    free_after = money(free_money - amount) if free_money is not None else None
    pct = (amount / income * 100).quantize(TENTH, rounding=ROUND_HALF_UP) if income else None
    buffer = money(income * buffer_income_pct / 100) if income else None

    # --- presupuestos del mes
    budget_total = budget_spent = budget_remaining = budget_after = None
    if ctx.budgets and all(b.spent is not None for b in ctx.budgets):
        budget_total = money(sum((b.amount for b in ctx.budgets), Decimal(0)))
        budget_spent = money(sum((b.spent for b in ctx.budgets), Decimal(0)))  # type: ignore[misc]
        budget_remaining = money(budget_total - budget_spent)
        budget_after = money(budget_remaining - amount)
    else:
        missing_optional.append("budgets")

    # --- metas activas
    goals_need = Decimal(0)
    for goal in ctx.goals:
        if (goal.status or "active").lower() in INACTIVE_STATUSES:
            continue
        remaining = goal.target_amount - goal.current_amount
        if remaining <= 0:
            continue
        if goal.deadline is None:
            if "goal_deadlines" not in missing_optional:
                missing_optional.append("goal_deadlines")
            continue
        months_left = max(1, months_between(today, goal.deadline))
        goals_need += remaining / months_left
    goals_need = money(goals_need)

    return PurchaseMetrics(
        amount=amount,
        currency=ctx.currency,
        as_of=today,
        liquid_balance=liquid_balance,
        monthly_income=money(income) if income else None,
        next_payday=payday_date,
        days_until_payday=(payday_date - today).days if payday_date else None,
        commitments=tuple(commitments),
        commitments_before_payday=commitments_total,
        free_money=free_money,
        free_after_purchase=free_after,
        pct_of_monthly_income=pct,
        safety_buffer=buffer,
        budget_total=budget_total,
        budget_spent=budget_spent,
        budget_remaining=budget_remaining,
        budget_remaining_after_purchase=budget_after,
        goals_monthly_need=goals_need,
        missing_required=tuple(missing_required),
        missing_optional=tuple(missing_optional),
    )
