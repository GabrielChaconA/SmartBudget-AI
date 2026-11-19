"""Punto de entrada del servicio de IA local de SmartBudget.

Ejecutar con:  uvicorn app.main:create_app --factory --port 8001
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app import __version__
from app.api import health
from app.api.deps import require_service_token
from app.api.errors import register_exception_handlers
from app.api.v1 import models
from app.config import Settings, get_settings
from app.logging_config import configure_logging
from app.services.ollama_client import OllamaClient

DESCRIPTION = """
Servicio **interno y sin estado** que es la única pieza que habla con Ollama.
No accede a la base de datos ni guarda conversaciones: Laravel le envía el
contexto ya armado y recibe inferencias.

Todas las rutas excepto `/health` exigen el header `X-AI-Service-Token`
(botón **Authorize**).
"""


def create_app(
    settings: Settings | None = None,
    *,
    ollama: OllamaClient | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        client = ollama or OllamaClient(settings)
        app.state.ollama = client
        try:
            yield
        finally:
            await client.aclose()

    docs = settings.ai_docs_enabled
    app = FastAPI(
        title="SmartBudget AI Service",
        description=DESCRIPTION,
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs else None,
    )
    app.state.settings = settings

    register_exception_handlers(app)

    protected = [Depends(require_service_token)]
    app.include_router(health.router)
    app.include_router(models.router, prefix="/v1", dependencies=protected)
    return app
