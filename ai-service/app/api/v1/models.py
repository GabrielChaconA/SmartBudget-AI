from fastapi import APIRouter, Depends

from app.api.deps import get_ollama, get_settings
from app.api.errors import COMMON_ERROR_RESPONSES, ErrorResponse
from app.config import Settings
from app.schemas.health import ModelInfo, ModelsResponse
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["models"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    responses={**COMMON_ERROR_RESPONSES, 503: {"model": ErrorResponse}},
    summary="Modelos permitidos (OLLAMA_MODEL + AI_ALLOWED_MODELS) y si están descargados",
)
async def list_models(
    settings: Settings = Depends(get_settings),
    ollama: OllamaClient = Depends(get_ollama),
) -> ModelsResponse:
    local = await ollama.list_local_models()
    return ModelsResponse(
        default=settings.default_model,
        models=[
            ModelInfo(name=m, default=m == settings.default_model, downloaded=m in local)
            for m in settings.allowed_models
        ],
    )
