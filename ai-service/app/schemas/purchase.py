from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, PlainSerializer

from app.schemas.common import Usage
from app.schemas.context import FinancialContext, Language, Money

Percent = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
VerdictValue = Literal["recomendable", "precaucion", "no_recomendable"]


class PurchaseCheckRequest(BaseModel):
    context: FinancialContext = Field(default_factory=FinancialContext)
    amount: Decimal = Field(gt=0, le=Decimal("10000000000"), examples=[8000])
    description: str | None = Field(None, max_length=200, examples=["TV"])
    language: Language = "es"


class PurchaseMessageOutput(BaseModel):
    """Lo que el modelo debe devolver (prompts/output/purchase_message.schema.json)."""

    message: str = Field(min_length=1, max_length=800)


class CommitmentOut(BaseModel):
    name: str
    amount: Money
    date: date


class PurchaseMetricsOut(BaseModel):
    """Cifras calculadas en Python. Son las que se muestran al usuario."""

    amount: Money
    currency: str
    as_of: date
    liquid_balance: Money | None
    monthly_income: Money | None
    next_payday: date | None
    days_until_payday: int | None
    commitments: list[CommitmentOut]
    commitments_before_payday: Money | None
    free_money: Money | None
    free_after_purchase: Money | None
    pct_of_monthly_income: Percent | None
    safety_buffer: Money | None
    budget_total: Money | None
    budget_spent: Money | None
    budget_remaining: Money | None
    budget_remaining_after_purchase: Money | None
    goals_monthly_need: Money


class PurchaseReasonOut(BaseModel):
    code: str = Field(examples=["high_income_share"])
    severity: Literal["block", "caution", "ok"]
    message: str


class PurchaseCheckResponse(BaseModel):
    status: Literal["ok", "insufficient_data"]
    verdict: VerdictValue | None = Field(description="null si faltan datos")
    reasons: list[PurchaseReasonOut]
    metrics: PurchaseMetricsOut
    message: str = Field(description="Mensaje para el usuario; siempre aclara que es una sugerencia")
    message_source: Literal["model", "template"] = Field(
        description="template si el modelo falló o su texto traía cifras no calculadas"
    )
    prompt_version: str = Field(examples=["purchase_check@1.0"])
    model: str | None = None
    usage: Usage | None = None
    missing_data: list[str] = Field(
        default_factory=list, description="Datos que faltan (requeridos u opcionales)"
    )
