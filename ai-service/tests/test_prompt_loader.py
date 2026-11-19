"""IAL-03: cargador de plantillas versionadas."""

import json
import shutil
from pathlib import Path

import pytest

from app.config import SERVICE_ROOT
from app.main import REQUIRED_PROMPT_TASKS, create_app
from app.schemas.context import FinancialContext
from app.services.prompt_loader import PromptConfigError, PromptRegistry, money
from tests.conftest import make_settings

PROMPTS = SERVICE_ROOT / "prompts"

CONTEXT = FinancialContext.model_validate(
    {
        "currency": "MXN",
        "monthly_income": "18217.65",
        "payday": 15,
        "accounts": [{"name": "Cartera", "type": "cash", "balance": 3500}],
        "subscriptions": [
            {"name": "Netflix", "amount": 219, "billing_cycle": "monthly", "next_billing_date": "2026-11-25"}
        ],
    }
).for_prompt()


@pytest.fixture
def prompts_copy(tmp_path: Path) -> Path:
    target = tmp_path / "prompts"
    shutil.copytree(PROMPTS, target)
    return target


def test_real_prompts_load_with_required_tasks():
    registry = PromptRegistry.load(PROMPTS, required_tasks=REQUIRED_PROMPT_TASKS)

    assert registry.version("chat") == "chat@1.0"
    assert registry.version("insights") == "insights@1.0"
    assert registry.version("purchase_check") == "purchase_check@1.0"


@pytest.mark.parametrize("language", ["es", "en"])
def test_render_chat_builds_system_examples_history_and_user(language: str):
    registry = PromptRegistry.load(PROMPTS)
    history = [{"role": "user", "content": "hola"}, {"role": "assistant", "content": "¡hola!"}]

    rendered = registry.render(
        "chat", language, context=CONTEXT, history=history, user_message="¿Cuánto pago de Netflix?"
    )

    assert rendered.version == "chat@1.0"
    assert rendered.schema["required"] == ["reply", "intent"]
    system = rendered.messages[0]
    assert system["role"] == "system"
    assert "SmartBudget AI" in system["content"]  # persona
    assert "Netflix" in system["content"] and "219.00 MXN" in system["content"]  # contexto
    assert "18,217.65 MXN" in system["content"]
    # ejemplos few-shot -> historial -> mensaje actual
    assert rendered.messages[-1] == {"role": "user", "content": "¿Cuánto pago de Netflix?"}
    assert rendered.messages[-3:-1] == history
    assert json.loads(rendered.messages[2]["content"])["intent"] == "general"


def test_language_selects_variant():
    registry = PromptRegistry.load(PROMPTS)

    es = registry.render("chat", "es", context=CONTEXT, user_message="x").messages[0]["content"]
    en = registry.render("chat", "en", context=CONTEXT, user_message="x").messages[0]["content"]

    assert "Hablas en español" in es and "Cuentas" in es
    assert "You speak English" in en and "Accounts" in en


def test_unsupported_language_is_rejected():
    with pytest.raises(ValueError):
        PromptRegistry.load(PROMPTS).render("chat", "fr", context=CONTEXT, user_message="x")


def test_instructions_in_user_message_for_insights():
    rendered = PromptRegistry.load(PROMPTS).render("insights", "es", context=CONTEXT)

    assert rendered.messages[-1]["role"] == "user"
    assert "Tarea: insights" in rendered.messages[-1]["content"]


def test_texts_are_formatted():
    registry = PromptRegistry.load(PROMPTS)

    text = registry.text("purchase_check", "es", "insufficient_data", missing="tu ingreso mensual")

    assert "tu ingreso mensual" in text


def test_empty_context_renders_placeholders():
    rendered = PromptRegistry.load(PROMPTS).render(
        "chat", "es", context=FinancialContext().for_prompt(), user_message="x"
    )
    assert "Sin cuentas registradas." in rendered.messages[0]["content"]


def test_service_fails_to_start_when_template_missing(prompts_copy: Path):
    (prompts_copy / "tasks" / "chat.en.j2").unlink()

    with pytest.raises(PromptConfigError, match="chat.en.j2"):
        create_app(make_settings(prompts_dir=prompts_copy))


def test_missing_schema_is_reported(prompts_copy: Path):
    (prompts_copy / "output" / "insights.schema.json").unlink()

    with pytest.raises(PromptConfigError, match="insights.schema.json"):
        PromptRegistry.load(prompts_copy)


def test_missing_required_task_is_reported(prompts_copy: Path):
    (prompts_copy / "tasks" / "purchase_check.yaml").unlink()

    with pytest.raises(PromptConfigError, match="purchase_check"):
        PromptRegistry.load(prompts_copy, required_tasks=REQUIRED_PROMPT_TASKS)


def test_missing_system_part_is_reported(prompts_copy: Path):
    (prompts_copy / "system" / "guardrails.es.md").unlink()

    with pytest.raises(PromptConfigError, match="guardrails.es.md"):
        PromptRegistry.load(prompts_copy)


def test_example_not_matching_schema_is_reported(prompts_copy: Path):
    path = prompts_copy / "examples" / "chat.es.yaml"
    path.write_text("- user: hola\n  assistant:\n    reply: hola\n    intent: inventado\n", encoding="utf-8")

    with pytest.raises(PromptConfigError, match="no cumple"):
        PromptRegistry.load(prompts_copy)


def test_invalid_version_is_reported(prompts_copy: Path):
    path = prompts_copy / "tasks" / "chat.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace('"1.0"', '"latest"'), encoding="utf-8")

    with pytest.raises(PromptConfigError, match="version"):
        PromptRegistry.load(prompts_copy)


def test_texts_must_have_same_keys_per_language(prompts_copy: Path):
    path = prompts_copy / "tasks" / "insights.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "    invalid_model_output: The model", "    other_key: The model"
        ),
        encoding="utf-8",
    )

    with pytest.raises(PromptConfigError, match="mismas claves"):
        PromptRegistry.load(prompts_copy)


def test_all_problems_reported_together(prompts_copy: Path):
    (prompts_copy / "tasks" / "chat.en.j2").unlink()
    (prompts_copy / "output" / "insights.schema.json").unlink()

    with pytest.raises(PromptConfigError) as exc:
        PromptRegistry.load(prompts_copy)

    assert len(exc.value.problems) >= 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [(8000, "8,000.00 MXN"), ("18217.65", "18,217.65 MXN"), (None, "—"), (-12.5, "-12.50 MXN")],
)
def test_money_filter(value, expected):
    assert money(value, "MXN") == expected
