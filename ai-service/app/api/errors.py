"""Traducción de errores a respuestas HTTP con cuerpo uniforme:

    {"error": {"code": "...", "message": "...", "retryable": false}}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import ErrorDetail, ErrorResponse
from app.services.exceptions import AIServiceError

logger = logging.getLogger("app.api")


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = ErrorDetail(code=code, message=message, retryable=retryable)


def error_response(status_code: int, code: str, message: str, retryable: bool = False) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message, retryable=retryable))
    return JSONResponse(status_code=status_code, content=body.model_dump())


# Respuestas documentadas en OpenAPI para los endpoints protegidos.
COMMON_ERROR_RESPONSES: dict[int | str, dict] = {
    401: {"model": ErrorResponse, "description": "Falta o es inválido X-AI-Service-Token"},
    422: {"model": ErrorResponse, "description": "Petición inválida"},
}
MODEL_ERROR_RESPONSES: dict[int | str, dict] = {
    **COMMON_ERROR_RESPONSES,
    400: {"model": ErrorResponse, "description": "Modelo no permitido (X-AI-Model)"},
    503: {"model": ErrorResponse, "description": "Modelo no disponible"},
    504: {"model": ErrorResponse, "description": "Timeout del modelo"},
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content={"error": exc.detail.model_dump()}
        )

    @app.exception_handler(AIServiceError)
    async def _service_error(request: Request, exc: AIServiceError) -> JSONResponse:
        logger.warning("request failed path=%s code=%s", request.url.path, exc.code)
        return error_response(exc.status_code, exc.code, exc.message, exc.retryable)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        # No devolvemos los valores recibidos ("input"): pueden ser datos financieros.
        fields = [".".join(str(p) for p in err["loc"]) + f": {err['msg']}" for err in exc.errors()]
        return error_response(422, "invalid_request", "; ".join(fields)[:1000])

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {404: "not_found", 405: "method_not_allowed"}.get(exc.status_code, "http_error")
        return error_response(exc.status_code, code, str(exc.detail))
