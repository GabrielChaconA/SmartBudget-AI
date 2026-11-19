"""Detección determinista de "quiero pagar X" y lectura de montos en texto.

Sin LLM: el monto que se evalúa sale del mensaje del usuario con reglas fijas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

_VERB = re.compile(
    r"\b(pagar|pagarle|comprar|comprarme|gastar|gastarme|adquirir|me alcanza|alcanzar[ií]a|"
    r"permitirme|pay|buy|purchase|spend|afford)\b",
    re.IGNORECASE,
)

_NUMBER = re.compile(
    r"(?<![\w.,])"
    r"(?P<cur>\$\s?)?"
    r"(?P<num>\d+(?:[.,]\d+)*)"
    r"(?P<mult>\s?(?:k|mil|thousand)\b)?"
    r"(?P<curword>\s?(?:pesos|mxn|usd|d[oó]lares|dollars|euros?|eur)\b)?"
    r"(?P<pct>\s?%)?",
    re.IGNORECASE,
)

_DESCRIPTION = re.compile(
    r"^\s*(?:de|en|para|por|for|on)\s+(?P<desc>[^?.!,;]{1,60})", re.IGNORECASE
)

MAX_AMOUNT = Decimal("10000000000")


@dataclass(frozen=True)
class PurchaseIntent:
    amount: Decimal
    description: str | None


@dataclass(frozen=True)
class NumberToken:
    value: Decimal
    has_currency: bool
    is_percent: bool
    end: int


def parse_number(raw: str) -> Decimal | None:
    """Interpreta separadores de miles/decimales en es/en: 8,000 · 8.000 · 8,000.50 · 8.000,50 · 8,5."""
    s = raw.strip()
    if not s:
        return None
    if "," in s and "." in s:
        decimal_sep = "," if s.rfind(",") > s.rfind(".") else "."
        thousands_sep = "." if decimal_sep == "," else ","
        s = s.replace(thousands_sep, "").replace(decimal_sep, ".")
    elif "," in s or "." in s:
        sep = "," if "," in s else "."
        parts = s.split(sep)
        is_grouping = len(parts) > 2 or (len(parts[0]) <= 3 and all(len(p) == 3 for p in parts[1:]))
        s = "".join(parts) if is_grouping else s.replace(sep, ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def find_numbers(text: str) -> list[NumberToken]:
    tokens: list[NumberToken] = []
    for match in _NUMBER.finditer(text):
        value = parse_number(match.group("num"))
        if value is None:
            continue
        if match.group("mult"):
            value *= 1000
        tokens.append(
            NumberToken(
                value=value,
                has_currency=bool(match.group("cur") or match.group("curword") or match.group("mult")),
                is_percent=bool(match.group("pct")),
                end=match.end(),
            )
        )
    return tokens


def detect_purchase_intent(message: str) -> PurchaseIntent | None:
    """Devuelve el monto si el mensaje expresa la intención de pagar/comprar algo con monto."""
    if not _VERB.search(message):
        return None
    candidates = [t for t in find_numbers(message) if not t.is_percent and 0 < t.value <= MAX_AMOUNT]
    if not candidates:
        return None
    with_currency = [t for t in candidates if t.has_currency]
    chosen = max(with_currency or candidates, key=lambda t: t.value)

    description = None
    match = _DESCRIPTION.match(message[chosen.end:])
    if match:
        description = match.group("desc").strip() or None
    return PurchaseIntent(amount=chosen.value, description=description)
