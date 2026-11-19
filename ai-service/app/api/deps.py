import secrets

from fastapi import Header, Request, Security
from fastapi.security import APIKeyHeader

from app.api.errors import ApiError
from app.config import Settings, normalize_model_name
from app.services.ollama_client import OllamaClient
from app.services.prompt_loader import PromptRegistry

TOKEN_HEADER = "X-AI-Service-Token"

_token_header = APIKeyHeader(
    name=TOKEN_HEADER,
    auto_error=False,
    description="Token interno compartido con Laravel (AI_SERVICE_TOKEN).",
)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_ollama(request: Request) -> OllamaClient:
    return request.app.state.ollama


def get_prompts(request: Request) -> PromptRegistry:
    return request.app.state.prompts


async def require_service_token(
    request: Request, token: str | None = Security(_token_header)
) -> None:
    expected = get_settings(request).ai_service_token.get_secret_value()
    if not token or not secrets.compare_digest(token.encode(), expected.encode()):
        raise ApiError(401, "unauthorized", f"Falta o es inválido el header {TOKEN_HEADER}.")


async def resolve_model(
    request: Request,
    x_ai_model: str | None = Header(
        default=None,
        description="Opcional. Usa otro modelo de AI_ALLOWED_MODELS (solo para pruebas).",
    ),
) -> str:
    settings = get_settings(request)
    if not x_ai_model:
        return settings.default_model
    model = normalize_model_name(x_ai_model)
    if model not in settings.allowed_models:
        raise ApiError(
            400,
            "model_not_allowed",
            f"El modelo '{x_ai_model}' no está en AI_ALLOWED_MODELS.",
        )
    return model
