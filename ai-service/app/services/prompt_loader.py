"""Carga, valida y renderiza las plantillas versionadas de ai-service/prompts/.

Estructura:

    prompts/
    ├── system/    persona.<lang>.md, guardrails.<lang>.md ...
    ├── tasks/     <tarea>.yaml (manifiesto con versión) + <tarea>.<lang>.j2
    ├── context/   <nombre>.<lang>.j2 (contexto financiero recibido de Laravel)
    ├── output/    <nombre>.schema.json (JSON Schema de la respuesta)
    └── examples/  <nombre>.<lang>.yaml (few-shot)

Cada tarea tiene un identificador ``<tarea>@<versión>`` (p. ej. ``purchase_check@1.0``)
que el servicio devuelve en cada respuesta para que Laravel lo guarde.

``PromptRegistry.load`` revisa TODO al iniciar y lanza ``PromptConfigError`` si falta
una plantilla, un schema o un texto referenciado, para que el servicio no arranque
con prompts rotos.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Literal

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError as SchemaValidationError

SUPPORTED_LANGUAGES: tuple[str, ...] = ("es", "en")
_VERSION = re.compile(r"^\d+\.\d+(\.\d+)?$")
_NAME = re.compile(r"^[a-z][a-z0-9_]*$")

Message = dict[str, str]


class PromptConfigError(RuntimeError):
    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = list(problems)
        super().__init__("Configuración de prompts inválida:\n- " + "\n- ".join(self.problems))


@dataclass(frozen=True)
class PromptTask:
    name: str
    version: str
    system: tuple[str, ...]
    output: str
    templates: Mapping[str, str]
    instructions_in: Literal["system", "user"]
    context: str | None
    examples: str | None
    texts: Mapping[str, Mapping[str, Any]]

    @property
    def id(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class RenderedPrompt:
    messages: list[Message]
    schema: dict[str, Any]
    version: str


# ---------------------------------------------------------------- filtros Jinja
def money(value: Any, currency: str | None = None) -> str:
    """``8000`` -> ``8,000.00 MXN``. ``None`` -> ``—`` (dato no disponible)."""
    if value is None or value == "":
        return "—"
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return str(value)
    text = f"{amount:,.2f}"
    return f"{text} {currency}" if currency else text


def pct(value: Any) -> str:
    if value is None:
        return "—"
    return f"{Decimal(str(value)):.1f}%"


def _build_env(root: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(root)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=False,
    )
    env.filters["money"] = money
    env.filters["pct"] = pct
    return env


# --------------------------------------------------------------------- registro
class PromptRegistry:
    def __init__(
        self,
        root: Path,
        env: Environment,
        tasks: dict[str, PromptTask],
        system_texts: dict[tuple[str, str], str],
        schemas: dict[str, dict[str, Any]],
        examples: dict[tuple[str, str], list[dict[str, Any]]],
    ) -> None:
        self.root = root
        self._env = env
        self._tasks = tasks
        self._system = system_texts
        self._schemas = schemas
        self._examples = examples

    # -- carga --------------------------------------------------------------
    @classmethod
    def load(cls, root: Path, required_tasks: Iterable[str] = ()) -> PromptRegistry:
        root = Path(root)
        problems: list[str] = []
        if not root.is_dir():
            raise PromptConfigError([f"No existe el directorio de prompts: {root}"])

        env = _build_env(root)
        tasks: dict[str, PromptTask] = {}
        system_texts: dict[tuple[str, str], str] = {}
        schemas: dict[str, dict[str, Any]] = {}
        examples: dict[tuple[str, str], list[dict[str, Any]]] = {}

        for manifest in sorted((root / "tasks").glob("*.yaml")):
            task = _parse_manifest(manifest, problems)
            if task is None:
                continue
            if task.name in tasks:
                problems.append(f"{manifest.name}: tarea '{task.name}' duplicada")
                continue
            tasks[task.name] = task

            schema = schemas.get(task.output) or _load_schema(root, task, problems)
            if schema is not None:
                schemas[task.output] = schema

            for lang in SUPPORTED_LANGUAGES:
                for part in task.system:
                    key = (part, lang)
                    if key not in system_texts:
                        path = root / "system" / f"{part}.{lang}.md"
                        if path.is_file():
                            system_texts[key] = path.read_text(encoding="utf-8").strip()
                        else:
                            problems.append(f"{task.id}: falta system/{path.name}")

                _check_template(env, f"tasks/{task.templates.get(lang, '')}", task, problems)
                if task.context:
                    _check_template(env, f"context/{task.context}.{lang}.j2", task, problems)
                if task.examples and schema is not None:
                    loaded = _load_examples(root, task, lang, schema, problems)
                    if loaded is not None:
                        examples[(task.examples, lang)] = loaded

        for name in required_tasks:
            if name not in tasks:
                problems.append(f"falta la tarea requerida '{name}' (tasks/{name}.yaml)")

        if problems:
            raise PromptConfigError(problems)
        return cls(root, env, tasks, system_texts, schemas, examples)

    # -- consulta -------------------------------------------------------------
    def task(self, name: str) -> PromptTask:
        try:
            return self._tasks[name]
        except KeyError:
            raise KeyError(f"Tarea de prompt desconocida: {name}") from None

    def version(self, name: str) -> str:
        return self.task(name).id

    def schema(self, name: str) -> dict[str, Any]:
        return self._schemas[self.task(name).output]

    def text(self, name: str, language: str, key: str, **values: Any) -> str:
        """Texto estático de la tarea (``texts.<lang>.<key>``), con ``str.format(**values)``."""
        node: Any = self.task(name).texts[_lang(language)]
        for part in key.split("."):
            node = node[part]
        return str(node).format(**values) if values else str(node)

    # -- render ---------------------------------------------------------------
    def render(
        self,
        name: str,
        language: str,
        *,
        context: Mapping[str, Any] | None = None,
        variables: Mapping[str, Any] | None = None,
        history: Sequence[Message] = (),
        user_message: str | None = None,
    ) -> RenderedPrompt:
        task = self.task(name)
        lang = _lang(language)
        variables = dict(variables or {})

        instructions = self._env.get_template(f"tasks/{task.templates[lang]}").render(
            **variables, ctx=context, language=lang
        )
        system_parts = [self._system[(part, lang)] for part in task.system]
        if task.instructions_in == "system":
            system_parts.append(instructions)
        if task.context and context is not None:
            system_parts.append(
                self._env.get_template(f"context/{task.context}.{lang}.j2").render(ctx=context)
            )

        messages: list[Message] = [
            {"role": "system", "content": "\n\n".join(p.strip() for p in system_parts if p.strip())}
        ]
        for example in self._examples.get((task.examples or "", lang), []):
            messages.append({"role": "user", "content": example["user"]})
            messages.append(
                {"role": "assistant", "content": json.dumps(example["assistant"], ensure_ascii=False)}
            )
        messages.extend({"role": m["role"], "content": m["content"]} for m in history)
        if task.instructions_in == "user":
            messages.append({"role": "user", "content": instructions})
        if user_message is not None:
            messages.append({"role": "user", "content": user_message})

        return RenderedPrompt(messages=messages, schema=self.schema(name), version=task.id)


# --------------------------------------------------------------------- helpers
def _lang(language: str) -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Idioma no soportado: {language}")
    return language


def _parse_manifest(path: Path, problems: list[str]) -> PromptTask | None:
    where = f"tasks/{path.name}"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        problems.append(f"{where}: YAML inválido ({exc})")
        return None
    if not isinstance(raw, dict):
        problems.append(f"{where}: el manifiesto debe ser un objeto")
        return None

    name = raw.get("name")
    version = str(raw.get("version", ""))
    count = len(problems)
    if not isinstance(name, str) or not _NAME.match(name):
        problems.append(f"{where}: 'name' inválido")
    elif name != path.stem:
        problems.append(f"{where}: 'name' ({name}) debe coincidir con el nombre del archivo")
    if not _VERSION.match(version):
        problems.append(f"{where}: 'version' debe ser tipo 1.0 (recibido '{version}')")
    for key in ("system", "output", "templates"):
        if not raw.get(key):
            problems.append(f"{where}: falta '{key}'")
    instructions_in = raw.get("instructions_in", "system")
    if instructions_in not in ("system", "user"):
        problems.append(f"{where}: 'instructions_in' debe ser system o user")

    templates = raw.get("templates") or {}
    texts = raw.get("texts") or {}
    for lang in SUPPORTED_LANGUAGES:
        if lang not in templates:
            problems.append(f"{where}: falta la plantilla para el idioma '{lang}'")
        if texts and lang not in texts:
            problems.append(f"{where}: faltan los textos para el idioma '{lang}'")
    if texts and all(lang in texts for lang in SUPPORTED_LANGUAGES):
        base = _key_paths(texts[SUPPORTED_LANGUAGES[0]])
        for lang in SUPPORTED_LANGUAGES[1:]:
            diff = base ^ _key_paths(texts[lang])
            if diff:
                problems.append(f"{where}: los textos no tienen las mismas claves por idioma: {sorted(diff)}")

    if len(problems) > count:
        return None
    return PromptTask(
        name=name,
        version=version,
        system=tuple(raw["system"]),
        output=raw["output"],
        templates=dict(templates),
        instructions_in=instructions_in,
        context=raw.get("context"),
        examples=raw.get("examples"),
        texts=texts,
    )


def _key_paths(node: Any, prefix: str = "") -> set[str]:
    if not isinstance(node, dict):
        return {prefix}
    paths: set[str] = set()
    for key, value in node.items():
        paths |= _key_paths(value, f"{prefix}.{key}" if prefix else str(key))
    return paths


def _load_schema(root: Path, task: PromptTask, problems: list[str]) -> dict[str, Any] | None:
    path = root / "output" / f"{task.output}.schema.json"
    if not path.is_file():
        problems.append(f"{task.id}: falta output/{path.name}")
        return None
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (ValueError, SchemaError) as exc:
        problems.append(f"{task.id}: output/{path.name} no es un JSON Schema válido ({exc})")
        return None
    return schema


def _check_template(env: Environment, name: str, task: PromptTask, problems: list[str]) -> None:
    if not (Path(env.loader.searchpath[0]) / name).is_file():  # type: ignore[union-attr]
        problems.append(f"{task.id}: falta {name}")
        return
    try:
        env.get_template(name)
    except TemplateError as exc:
        problems.append(f"{task.id}: {name} no compila ({exc})")


def _load_examples(
    root: Path, task: PromptTask, lang: str, schema: dict[str, Any], problems: list[str]
) -> list[dict[str, Any]] | None:
    path = root / "examples" / f"{task.examples}.{lang}.yaml"
    if not path.is_file():
        problems.append(f"{task.id}: falta examples/{path.name}")
        return None
    try:
        items = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except yaml.YAMLError as exc:
        problems.append(f"{task.id}: examples/{path.name} YAML inválido ({exc})")
        return None
    validator = Draft202012Validator(schema)
    valid: list[dict[str, Any]] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("user"), str) or "assistant" not in item:
            problems.append(f"{task.id}: examples/{path.name}[{i}] necesita 'user' y 'assistant'")
            continue
        try:
            validator.validate(item["assistant"])
        except SchemaValidationError as exc:
            problems.append(
                f"{task.id}: examples/{path.name}[{i}] no cumple output/{task.output} ({exc.message})"
            )
            continue
        valid.append(item)
    return valid
