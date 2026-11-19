"""Configuración del servicio, leída de variables de entorno (o de ai-service/.env)."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parent.parent

MIN_TOKEN_LENGTH = 16


def normalize_model_name(name: str) -> str:
    """Ollama guarda los modelos sin etiqueta como ``<nombre>:latest``."""
    name = name.strip()
    return name if ":" in name else f"{name}:latest"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=SERVICE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Ollama -------------------------------------------------------------
    ollama_host: str = "http://localhost:11434"
    # Modelo principal (SBI-1). Cambiar de modelo = cambiar esta variable.
    ollama_model: str = "qwen3:8b"
    # Modelos extra que se pueden elegir por petición con el header X-AI-Model
    # (pensado para comparar modelos en pruebas). Lista separada por comas.
    ai_allowed_models: str = ""

    ollama_timeout_seconds: float = Field(120.0, gt=0)
    ollama_connect_timeout_seconds: float = Field(5.0, gt=0)
    ollama_health_timeout_seconds: float = Field(3.0, gt=0)
    ollama_max_retries: int = Field(1, ge=0, le=3)
    ollama_retry_backoff_seconds: float = Field(0.5, ge=0)
    ollama_keep_alive: str = "10m"
    ollama_num_ctx: int = Field(8192, ge=512)
    ollama_temperature: float = Field(0.2, ge=0, le=2)

    # --- Seguridad ----------------------------------------------------------
    ai_service_token: SecretStr

    # --- Comportamiento -----------------------------------------------------
    ai_max_history_messages: int = Field(12, ge=0, le=50)
    ai_docs_enabled: bool = True
    prompts_dir: Path = SERVICE_ROOT / "prompts"
    log_level: str = "INFO"

    @field_validator("ai_service_token")
    @classmethod
    def _token_not_trivial(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().strip()) < MIN_TOKEN_LENGTH:
            raise ValueError(f"AI_SERVICE_TOKEN debe tener al menos {MIN_TOKEN_LENGTH} caracteres")
        return value

    @property
    def default_model(self) -> str:
        return normalize_model_name(self.ollama_model)

    @property
    def allowed_models(self) -> list[str]:
        """Modelo principal + modelos de prueba, normalizados y sin duplicados."""
        models = [self.default_model]
        for raw in self.ai_allowed_models.split(","):
            if raw.strip():
                name = normalize_model_name(raw)
                if name not in models:
                    models.append(name)
        return models


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
