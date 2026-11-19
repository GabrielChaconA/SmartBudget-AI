"""Reglas deterministas del veredicto de un pago. El modelo NO participa:
con las mismas cifras el resultado siempre es el mismo.

| Regla | Condición | Severidad |
|---|---|---|
| exceeds_free_money | dinero libre después del pago < 0 | block |
| low_buffer | 0 <= libre después < colchón (10 % del ingreso) | caution |
| very_high_income_share | pago >= 50 % del ingreso mensual | block |
| high_income_share | 25 % <= pago < 50 % del ingreso | caution |
| exceeds_budget | presupuesto restante del mes - pago < 0 | caution |
| goals_at_risk | metas necesitan > 0 y libre después < lo que necesitan al mes | caution |
| within_means | ninguna de las anteriores | ok |

Veredicto: ``no_recomendable`` si hay algún block; ``precaucion`` si hay algún caution;
si no, ``recomendable``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from app.services.purchase.metrics import PurchaseMetrics


class Verdict(str, Enum):
    RECOMENDABLE = "recomendable"
    PRECAUCION = "precaucion"
    NO_RECOMENDABLE = "no_recomendable"


class Severity(str, Enum):
    BLOCK = "block"
    CAUTION = "caution"
    OK = "ok"


@dataclass(frozen=True)
class Thresholds:
    caution_income_pct: Decimal = Decimal("25")
    block_income_pct: Decimal = Decimal("50")
    buffer_income_pct: Decimal = Decimal("10")


DEFAULT_THRESHOLDS = Thresholds()


@dataclass(frozen=True)
class Reason:
    code: str
    severity: Severity


class MissingDataError(ValueError):
    pass


def evaluate(m: PurchaseMetrics, t: Thresholds = DEFAULT_THRESHOLDS) -> tuple[Verdict, tuple[Reason, ...]]:
    if m.missing_required:
        raise MissingDataError(f"Faltan datos: {', '.join(m.missing_required)}")
    assert m.free_after_purchase is not None and m.pct_of_monthly_income is not None
    assert m.safety_buffer is not None

    reasons: list[Reason] = []
    free_after = m.free_after_purchase

    if free_after < 0:
        reasons.append(Reason("exceeds_free_money", Severity.BLOCK))
    elif free_after < m.safety_buffer:
        reasons.append(Reason("low_buffer", Severity.CAUTION))

    if m.pct_of_monthly_income >= t.block_income_pct:
        reasons.append(Reason("very_high_income_share", Severity.BLOCK))
    elif m.pct_of_monthly_income >= t.caution_income_pct:
        reasons.append(Reason("high_income_share", Severity.CAUTION))

    if m.budget_remaining_after_purchase is not None and m.budget_remaining_after_purchase < 0:
        reasons.append(Reason("exceeds_budget", Severity.CAUTION))

    if m.goals_monthly_need > 0 and free_after < m.goals_monthly_need:
        reasons.append(Reason("goals_at_risk", Severity.CAUTION))

    if not reasons:
        return Verdict.RECOMENDABLE, (Reason("within_means", Severity.OK),)

    severities = {r.severity for r in reasons}
    if Severity.BLOCK in severities:
        return Verdict.NO_RECOMENDABLE, tuple(reasons)
    return Verdict.PRECAUCION, tuple(reasons)
