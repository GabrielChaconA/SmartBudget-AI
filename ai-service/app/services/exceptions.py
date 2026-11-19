"""Errores propios del servicio. Los handlers de app/api/errors.py los convierten
en respuestas HTTP con un cuerpo uniforme."""


class AIServiceError(Exception):
    status_code = 500
    code = "internal_error"
    retryable = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ModelUnavailable(AIServiceError):
    """Ollama no responde, rechazó la petición o el modelo no está descargado."""

    status_code = 503
    code = "model_unavailable"
    retryable = True


class ModelTimeout(AIServiceError):
    """La inferencia excedió el timeout configurado."""

    status_code = 504
    code = "model_timeout"
    retryable = True


class InvalidModelOutput(AIServiceError):
    """El modelo respondió algo que no cumple el JSON Schema, incluso tras reintentar.
    Nunca se devuelve texto sin validar."""

    status_code = 503
    code = "invalid_model_output"
    retryable = True
