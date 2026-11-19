"""Request / response de los endpoints internos de inferencia (/v1/chat, /v1/insights)."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.context import FinancialContext, Language

ChatIntent = Literal[
    "general",
    "spending",
    "budgets",
    "subscriptions",
    "goals",
    "investments",
    "purchase_check",
    "out_of_scope",
]
InsightCategory = Literal[
    "spending", "budget", "subscriptions", "savings", "goals", "investments", "income", "general"
]


class Usage(BaseModel):
    """Métricas de la llamada al modelo (útiles para comparar modelos)."""

    duration_ms: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    attempts: int = 1


# ------------------------------------------------------------------- chat
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    context: FinancialContext = Field(default_factory=FinancialContext)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=100,
        description="Mensajes previos (Laravel los guarda; el servicio no tiene estado).",
    )
    message: str = Field(min_length=1, max_length=2000)
    language: Language = "es"


class ChatModelOutput(BaseModel):
    """Lo que el modelo debe devolver (prompts/output/chat_reply.schema.json)."""

    reply: str = Field(min_length=1, max_length=1500)
    intent: ChatIntent


class ChatResponse(BaseModel):
    status: Literal["ok", "insufficient_data"]
    reply: str
    intent: ChatIntent | Literal["insufficient_data"]
    prompt_version: str = Field(examples=["chat@1.0"])
    model: str | None = Field(None, description="null si no se llamó al modelo")
    usage: Usage | None = None


# --------------------------------------------------------------- insights
class InsightsRequest(BaseModel):
    context: FinancialContext = Field(default_factory=FinancialContext)
    language: Language = "es"


class Insight(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=400)
    category: InsightCategory
    priority: Literal["low", "medium", "high"]


class InsightsModelOutput(BaseModel):
    """Lo que el modelo debe devolver (prompts/output/insights.schema.json)."""

    insights: list[Insight] = Field(min_length=1, max_length=3)


class InsightsResponse(BaseModel):
    status: Literal["ok", "insufficient_data", "model_error"]
    insights: list[Insight] = Field(max_length=3)
    reason: str | None = Field(None, description="Motivo cuando la lista viene vacía")
    prompt_version: str = Field(examples=["insights@1.0"])
    model: str | None = None
    usage: Usage | None = None
