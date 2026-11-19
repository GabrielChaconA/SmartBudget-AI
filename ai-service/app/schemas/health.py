from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "ollama_unavailable", "model_not_downloaded"]
    service: Literal["up"] = "up"
    ollama: Literal["up", "down"]
    model: str = Field(description="Modelo configurado en OLLAMA_MODEL")
    model_downloaded: bool | None = Field(
        description="null cuando Ollama no responde y no se puede saber"
    )
    test_models: dict[str, bool | None] = Field(
        default_factory=dict,
        description="Modelos de AI_ALLOWED_MODELS y si están descargados",
    )
    version: str


class ModelInfo(BaseModel):
    name: str
    default: bool
    downloaded: bool


class ModelsResponse(BaseModel):
    default: str
    models: list[ModelInfo]
