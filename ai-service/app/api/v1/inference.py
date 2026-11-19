from fastapi import APIRouter, Depends

from app.api.deps import get_ollama, get_prompts, get_settings, resolve_model
from app.api.errors import MODEL_ERROR_RESPONSES
from app.config import Settings
from app.schemas.inference import ChatRequest, ChatResponse, InsightsRequest, InsightsResponse
from app.services import inference
from app.services.ollama_client import OllamaClient
from app.services.prompt_loader import PromptRegistry

router = APIRouter(tags=["inference"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses=MODEL_ERROR_RESPONSES,
    summary="Respuesta del asistente (usado por AiChatController, SBI-11)",
    description=(
        "Recibe el contexto financiero, el historial y el mensaje actual; devuelve la "
        "respuesta, la intención detectada y la versión del prompt. Con un contexto vacío "
        "responde `status=insufficient_data` sin llamar al modelo."
    ),
)
async def chat(
    req: ChatRequest,
    ollama: OllamaClient = Depends(get_ollama),
    prompts: PromptRegistry = Depends(get_prompts),
    settings: Settings = Depends(get_settings),
    model: str = Depends(resolve_model),
) -> ChatResponse:
    return await inference.run_chat(req, ollama=ollama, prompts=prompts, settings=settings, model=model)


@router.post(
    "/insights",
    response_model=InsightsResponse,
    responses=MODEL_ERROR_RESPONSES,
    summary="De 1 a 3 insights financieros (usado por FinancialInsightService, SBI-14)",
    description=(
        "Las respuestas siempre cumplen el JSON Schema. Si el modelo devuelve algo inválido, "
        "`status=model_error` con lista vacía y `reason`. Si el modelo no está disponible o "
        "excede el timeout: 503 / 504."
    ),
)
async def insights(
    req: InsightsRequest,
    ollama: OllamaClient = Depends(get_ollama),
    prompts: PromptRegistry = Depends(get_prompts),
    model: str = Depends(resolve_model),
) -> InsightsResponse:
    return await inference.run_insights(req, ollama=ollama, prompts=prompts, model=model)
