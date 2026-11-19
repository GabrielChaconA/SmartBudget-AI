"""Mini conversación con el modelo desde la terminal, contra POST /v1/chat.

El servicio no guarda estado: este script mantiene el historial en memoria y lo
reenvía en cada mensaje, igual que hará Laravel (SBI-11).

Uso (con el servicio corriendo):
    python scripts/chat_cli.py
    python scripts/chat_cli.py --model gemma4:e4b --lang en
    python scripts/chat_cli.py --context mi_contexto.json

Comandos dentro del chat:
    /model <nombre>   cambia de modelo (debe estar en AI_ALLOWED_MODELS)
    /compare <texto>  envía el mismo mensaje a todos los modelos permitidos
    /reset            borra el historial
    /exit             sale
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent


def read_token() -> str:
    token = os.environ.get("AI_SERVICE_TOKEN")
    env_file = ROOT / ".env"
    if not token and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("AI_SERVICE_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"')
    if not token:
        sys.exit("Define AI_SERVICE_TOKEN (variable de entorno o ai-service/.env)")
    return token


def send(client: httpx.Client, body: dict, model: str | None) -> dict:
    headers = {"X-AI-Model": model} if model else {}
    response = client.post("/v1/chat", json=body, headers=headers)
    data = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"{response.status_code} {data.get('error', data)}")
    return data


def describe(data: dict) -> str:
    usage = data.get("usage") or {}
    meta = f"[{data.get('model') or 'sin modelo'} · intent={data['intent']} · {data['prompt_version']}"
    if usage:
        meta += f" · {usage['duration_ms']} ms · {usage.get('completion_tokens')} tokens"
    meta += "]"
    text = f"{data['reply']}\n  {meta}"
    purchase = data.get("purchase")
    if purchase:
        text += f"\n  veredicto={purchase.get('verdict')} motivos={[r['code'] for r in purchase.get('reasons', [])]}"
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=os.environ.get("AI_SERVICE_URL", "http://127.0.0.1:8001"))
    parser.add_argument("--model", default=None, help="Modelo de AI_ALLOWED_MODELS (por defecto OLLAMA_MODEL)")
    parser.add_argument("--lang", default="es", choices=["es", "en"])
    parser.add_argument("--context", type=Path, default=ROOT / "scripts" / "sample_context.json")
    args = parser.parse_args()

    context = json.loads(args.context.read_text(encoding="utf-8"))
    history: list[dict] = []
    model = args.model

    with httpx.Client(base_url=args.url, headers={"X-AI-Service-Token": read_token()}, timeout=300) as client:
        print(f"Conectado a {args.url}. Contexto: {args.context.name}. Escribe /exit para salir.\n")
        while True:
            try:
                message = input("tú> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not message:
                continue
            if message == "/exit":
                break
            if message == "/reset":
                history.clear()
                print("(historial borrado)\n")
                continue
            if message.startswith("/model "):
                model = message.split(maxsplit=1)[1]
                print(f"(modelo: {model})\n")
                continue
            if message.startswith("/compare "):
                text = message.split(maxsplit=1)[1]
                models = [m["name"] for m in client.get("/v1/models").json()["models"] if m["downloaded"]]
                for name in models:
                    body = {"context": context, "history": history, "message": text, "language": args.lang}
                    try:
                        print(f"--- {name}\n{describe(send(client, body, name))}\n")
                    except RuntimeError as exc:
                        print(f"--- {name}\nerror: {exc}\n")
                continue

            body = {"context": context, "history": history, "message": message, "language": args.lang}
            try:
                data = send(client, body, model)
            except (RuntimeError, httpx.HTTPError) as exc:
                print(f"error: {exc}\n")
                continue
            print(f"ia> {describe(data)}\n")
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": data["reply"]})


if __name__ == "__main__":
    main()
