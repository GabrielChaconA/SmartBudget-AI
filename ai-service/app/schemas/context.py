"""Contexto financiero que arma Laravel (FinancialContextBuilder, SBI-10) y envía
en cada petición. El servicio no consulta la base de datos.

Los montos aceptan número o string ("18217.65", como los devuelve PostgreSQL) y se
manejan como Decimal. Se permiten campos extra para no romper si SBI-10 agrega datos.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

Language = Literal["es", "en"]

Money = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class _Item(BaseModel):
    model_config = ConfigDict(extra="allow")


class Account(_Item):
    name: str
    type: str | None = Field(None, examples=["bank", "cash", "credit"])
    balance: Money
    currency: str | None = None


class Fund(_Item):
    name: str
    balance: Money
    categories: list[str] = Field(default_factory=list)


class Subscription(_Item):
    name: str
    amount: Money
    billing_cycle: str | None = Field(None, examples=["monthly", "yearly"])
    next_billing_date: date | None = None
    status: str | None = None


class Budget(_Item):
    category: str
    amount: Money = Field(description="Límite del mes")
    spent: Money | None = Field(None, description="Gastado en el mes")


class Goal(_Item):
    name: str
    target_amount: Money
    current_amount: Money = Decimal("0")
    deadline: date | None = None
    status: str | None = "active"


class Investment(_Item):
    symbol: str
    type: str | None = None
    quantity: Decimal
    average_price: Money
    current_price: Money | None = None
    currency: str | None = None


class Transaction(_Item):
    date: datetime | date
    type: str = Field(examples=["income", "expense"])
    amount: Money
    category: str | None = None
    description: str | None = None


class FinancialContext(_Item):
    as_of: date | None = Field(None, description="Fecha de referencia; por defecto, hoy")
    currency: str = "MXN"
    monthly_income: Money | None = None
    payday: int | None = Field(None, ge=1, le=31, description="Día del mes en que cobra")
    month_income: Money | None = None
    month_expenses: Money | None = None
    accounts: list[Account] = Field(default_factory=list)
    funds: list[Fund] = Field(default_factory=list)
    subscriptions: list[Subscription] = Field(default_factory=list)
    budgets: list[Budget] = Field(default_factory=list)
    goals: list[Goal] = Field(default_factory=list)
    investments: list[Investment] = Field(default_factory=list)
    recent_transactions: list[Transaction] = Field(default_factory=list)

    def is_empty(self) -> bool:
        """True si no hay ningún dato financiero con el que responder."""
        has_income = bool(self.monthly_income) or bool(self.month_income)
        lists = (
            self.accounts, self.funds, self.subscriptions, self.budgets,
            self.goals, self.investments, self.recent_transactions,
        )
        return not has_income and not any(lists) and not self.month_expenses

    def for_prompt(self) -> dict:
        return self.model_dump(mode="json")
