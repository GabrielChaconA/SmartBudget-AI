from fastapi import APIRouter, Depends, Response

from app import __version__
from app.api.deps import get_ollama, get_settings
from app.config import Settings
from app.schemas.health import HealthResponse
from app.services.exceptions import ModelUnavailable
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Ollama caído o modelo no descargado"}},
    summary="Estado del servicio, de Ollama y del modelo configurado",
)
async def health(
    response: Response,
    settings: Settings = Depends(get_settings),
    ollama: OllamaClient = Depends(get_ollama),
) -> HealthResponse:
    model = settings.default_model
    test_models = [m for m in settings.allowed_models if m != model]

    try:
        local = await ollama.list_local_models()
    except ModelUnavailable:
        response.status_code = 503
        return HealthResponse(
            status="ollama_unavailable",
            ollama="down",
            model=model,
            model_downloaded=None,
            test_models={m: None for m in test_models},
            version=__version__,
        )

    downloaded = model in local
    if not downloaded:
        response.status_code = 503
    return HealthResponse(
        status="ok" if downloaded else "model_not_downloaded",
        ollama="up",
        model=model,
        model_downloaded=downloaded,
        test_models={m: m in local for m in test_models},
        version=__version__,
    )
