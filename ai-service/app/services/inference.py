"""Casos de uso de chat e insights. Sin estado y sin acceso a base de datos:
todo llega en la petición (contexto armado por Laravel)."""

from __future__ import annotations

from app.config import Settings
from app.schemas.inference import (
    ChatModelOutput,
    ChatRequest,
    ChatResponse,
    InsightsModelOutput,
    InsightsRequest,
    InsightsResponse,
    Usage,
)
from app.services.exceptions import InvalidModelOutput
from app.services.ollama_client import OllamaClient, StructuredResult
from app.services.prompt_loader import PromptRegistry


def usage_of(result: StructuredResult) -> Usage:
    return Usage(
        duration_ms=result.duration_ms,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
        attempts=result.attempts,
    )


async def run_chat(
    req: ChatRequest,
    *,
    ollama: OllamaClient,
    prompts: PromptRegistry,
    settings: Settings,
    model: str,
) -> ChatResponse:
    if req.context.is_empty():
        # No se llama al modelo: sin datos no hay respuesta que no sea inventada.
        return ChatResponse(
            status="insufficient_data",
            reply=prompts.text("chat", req.language, "insufficient_data"),
            intent="insufficient_data",
            prompt_version=prompts.version("chat"),
            model=None,
        )

    limit = settings.ai_max_history_messages
    history = [m.model_dump() for m in req.history][-limit:] if limit else []
    rendered = prompts.render(
        "chat",
        req.language,
        context=req.context.for_prompt(),
        history=history,
        user_message=req.message,
    )
    result = await ollama.chat_structured(
        rendered.messages, ChatModelOutput, schema=rendered.schema, model=model, task="chat"
    )
    return ChatResponse(
        status="ok",
        reply=result.data.reply,
        intent=result.data.intent,
        prompt_version=rendered.version,
        model=result.model,
        usage=usage_of(result),
    )


async def run_insights(
    req: InsightsRequest,
    *,
    ollama: OllamaClient,
    prompts: PromptRegistry,
    model: str,
) -> InsightsResponse:
    version = prompts.version("insights")
    if req.context.is_empty():
        return InsightsResponse(
            status="insufficient_data",
            insights=[],
            reason=prompts.text("insights", req.language, "insufficient_data"),
            prompt_version=version,
        )

    rendered = prompts.render("insights", req.language, context=req.context.for_prompt())
    try:
        result = await ollama.chat_structured(
            rendered.messages, InsightsModelOutput, schema=rendered.schema, model=model, task="insights"
        )
    except InvalidModelOutput:
        # Nunca se devuelven insights sin validar: lista vacía con el motivo.
        return InsightsResponse(
            status="model_error",
            insights=[],
            reason=prompts.text("insights", req.language, "invalid_model_output"),
            prompt_version=version,
            model=model,
        )
    return InsightsResponse(
        status="ok",
        insights=result.data.insights,
        prompt_version=version,
        model=result.model,
        usage=usage_of(result),
    )
