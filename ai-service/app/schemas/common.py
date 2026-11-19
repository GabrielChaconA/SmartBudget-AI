from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(examples=["model_unavailable"])
    message: str
    retryable: bool = False


class ErrorResponse(BaseModel):
    """Cuerpo uniforme de todos los errores del servicio."""

    error: ErrorDetail
