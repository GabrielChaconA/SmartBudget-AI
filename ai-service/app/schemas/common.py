from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(examples=["model_unavailable"])
    message: str
    retryable: bool = False


class ErrorResponse(BaseModel):
    """Cuerpo uniforme de todos los errores del servicio."""

    error: ErrorDetail


class Usage(BaseModel):
    """Métricas de la llamada al modelo (útiles para comparar modelos)."""

    duration_ms: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    attempts: int = 1

    @classmethod
    def from_result(cls, result) -> "Usage":
        """Desde un ``StructuredResult`` del cliente de Ollama."""
        return cls(
            duration_ms=result.duration_ms,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            attempts=result.attempts,
        )
