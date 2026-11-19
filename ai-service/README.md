# SmartBudget AI Service

Microservicio interno en **Python (FastAPI)** que es la **única pieza del sistema que habla con Ollama**.

- **Interno**: no se expone a internet; solo Laravel lo llama, con el header `X-AI-Service-Token`.
- **Sin estado**: no accede a la base de datos ni guarda conversaciones. Laravel le envía
  el contexto financiero ya armado (SBI-10) y guarda lo que haga falta (SBI-11).

```
Frontend ──> Laravel (/api/ai/*, auth, caché, persistencia)
                │  AiServiceClient  (X-AI-Service-Token)
                ▼
           ai-service (FastAPI) ──> Ollama (modelo local)
```

## Requisitos de hardware

El servicio Python es ligero (< 200 MB de RAM). El peso lo pone el modelo que carga Ollama.
Tamaños aproximados con la cuantización por defecto de Ollama (verifícalos con `ollama list`):

| Modelo | Uso | Descarga aprox. | RAM / VRAM recomendada |
|---|---|---|---|
| `qwen3:8b` | principal por defecto | ~5 GB | 8 GB VRAM, o 16 GB RAM en CPU |
| `gemma4:e4b` | prueba (ligero) | ~5–10 GB | 8 GB VRAM, o 16 GB RAM en CPU |
| `gemma4:26b` | prueba (pesado) | ~17–20 GB | 24 GB VRAM, o 32 GB RAM en CPU |

- **Disco**: ~35 GB libres para tener los tres modelos.
- **CPU sin GPU** funciona, pero espera respuestas de 10–60 s; con GPU, 1–5 s.
- La primera llamada a un modelo tarda más (lo carga en memoria). `OLLAMA_KEEP_ALIVE`
  controla cuánto tiempo se queda cargado.

## Ejecutar localmente

### Opción A: Ollama instalado en tu máquina + Python (recomendada en Windows)

```powershell
# 1. Modelos
ollama pull qwen3:8b
ollama pull gemma4:e4b      # opcional, para comparar
ollama pull gemma4:26b      # opcional, pesado

# 2. Servicio
cd ai-service
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # y cambia AI_SERVICE_TOKEN
uvicorn app.main:create_app --factory --reload --port 8001
```

### Opción B: Docker Compose (servicio + Ollama)

```bash
cd ai-service
cp .env.example .env              # cambia AI_SERVICE_TOKEN
docker compose up --build
# Con GPU NVIDIA:
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

`ollama-pull` descarga `OLLAMA_MODEL` y los modelos de `AI_ALLOWED_MODELS`. Mientras
descarga, `/health` responde `model_not_downloaded`. El servicio queda en
`http://127.0.0.1:8001` (solo localhost).

### Comprobar

```bash
curl http://127.0.0.1:8001/health
curl -H "X-AI-Service-Token: <tu token>" http://127.0.0.1:8001/v1/models
```

Swagger UI: <http://127.0.0.1:8001/docs> (botón **Authorize** para poner el token).

## Configuración

Todas las variables están documentadas en [.env.example](.env.example). Las principales:

| Variable | Descripción |
|---|---|
| `OLLAMA_HOST` | URL de Ollama |
| `OLLAMA_MODEL` | Modelo principal. **Cambiar de modelo = cambiar esta variable**, sin tocar código |
| `AI_ALLOWED_MODELS` | Modelos de prueba que se pueden pedir con el header `X-AI-Model` |
| `AI_SERVICE_TOKEN` | Token interno compartido con Laravel (mínimo 16 caracteres) |
| `OLLAMA_TIMEOUT_SECONDS` | Timeout de cada inferencia |
| `OLLAMA_MAX_RETRIES` | Reintentos ante errores de conexión o 5xx de Ollama |

## Endpoints

| Método | Ruta | Token | Descripción |
|---|---|---|---|
| GET | `/health` | no | Estado: `ok`, `ollama_unavailable` o `model_not_downloaded` (503 en los dos últimos) |
| GET | `/v1/models` | sí | Modelo principal + modelos de prueba y si están descargados |
| POST | `/v1/chat` | sí | `{context, history, message, language}` → `{status, reply, intent, prompt_version, model, usage}` (SBI-11) |
| POST | `/v1/insights` | sí | `{context, language}` → `{status, insights[1..3], reason, prompt_version, model, usage}` (SBI-14) |

Request y response están definidos con Pydantic y documentados en `/docs`.

- **Contexto vacío** → `status: "insufficient_data"` con un mensaje fijo; no se llama al modelo.
- **Insights inválidos** → `status: "model_error"`, `insights: []` y `reason` (nunca se devuelve
  algo que no cumpla el schema). Si Ollama está caído o hay timeout → 503 / 504.
- `usage` trae duración y tokens de la llamada: útil para comparar modelos.

### Mini conversación con el modelo

El servicio no guarda estado, así que una conversación es reenviar el `history` en cada
mensaje (lo que hará Laravel en SBI-11). Para probarlo ya:

- **Terminal**: `python scripts/chat_cli.py` (o `--model gemma4:e4b`). Guarda el historial en
  memoria; `/model <nombre>` cambia de modelo, `/compare <texto>` manda el mismo mensaje a
  todos los modelos descargados, `/reset` borra el historial.
- **Postman**: importa `postman/SmartBudget-AI-Service.postman_collection.json`, pon tu token en
  la variable `token` y usa *Conversación → Enviar mensaje*: un script guarda el historial en
  la variable `history`.
- **Swagger**: `/docs` → Authorize → `POST /v1/chat` (historial a mano).

El contexto de ejemplo está en `scripts/sample_context.json` (datos ficticios).

### Probar otros modelos

Cualquier endpoint de inferencia acepta el header opcional `X-AI-Model` con un modelo de
`AI_ALLOWED_MODELS` (si no está en la lista: `400 model_not_allowed`). Así puedes comparar
`qwen3:8b`, `gemma4:e4b` y `gemma4:26b` con la misma petición sin reiniciar el servicio.

## Prompts versionados

```
prompts/
├── system/    persona y guardrails (tono amable y conciso; solo recomienda, nunca ejecuta)
├── tasks/     <tarea>.yaml (manifiesto + versión + textos) y <tarea>.<es|en>.j2
├── context/   financial_context.<es|en>.j2 — donde se inyecta el contexto de Laravel
├── output/    JSON Schemas de las respuestas estructuradas
└── examples/  ejemplos few-shot por tarea e idioma
```

- Cada tarea tiene un id `<tarea>@<versión>` (p. ej. `purchase_check@1.0`) que se devuelve
  como `prompt_version` en cada respuesta para que Laravel lo guarde (SBI-12).
  **Sube la versión** del manifiesto cada vez que cambies cualquier pieza de la tarea.
- El idioma (`es` / `en`) se elige por petición; cada plantilla tiene una variante por idioma.
- `app/services/prompt_loader.py` valida todo al iniciar: si falta una plantilla, un schema,
  una parte de `system/` o un texto, o si un ejemplo no cumple su schema, **el servicio no arranca**.
- Las plantillas actuales son mínimas; su redacción final es parte de SBI-12.

## Errores

Todos los errores tienen el mismo cuerpo:

```json
{ "error": { "code": "model_unavailable", "message": "...", "retryable": true } }
```

| HTTP | `code` | Cuándo |
|---|---|---|
| 401 | `unauthorized` | Falta o es inválido `X-AI-Service-Token` |
| 400 | `model_not_allowed` | `X-AI-Model` fuera de `AI_ALLOWED_MODELS` |
| 422 | `invalid_request` | Petición inválida (no se devuelven los valores recibidos) |
| 503 | `model_unavailable` | Ollama caído o modelo no descargado |
| 504 | `model_timeout` | La inferencia excedió `OLLAMA_TIMEOUT_SECONDS` |

## Pruebas

```bash
pytest -q
```

Ollama siempre está simulado (`httpx.MockTransport`), así que las pruebas no necesitan
GPU, modelos ni red. Se ejecutan en CI con `.github/workflows/ai-service.yml`.
