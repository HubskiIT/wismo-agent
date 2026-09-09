"""Guardrails i walidacje. Uruchamiane przed wysłaniem odpowiedzi agenta."""

import re

# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------

MAX_LEN: dict[str, int] = {
    "widget": 800,
    "whatsapp": 1000,
    "email": 2000,
}

# Zwroty które nie mogą pojawić się w odpowiedzi agenta bez explicite podstawy.
BLACKLIST_PHRASES: list[str] = [
    r"\bgwarantuj[eę]\b",
    r"\bna pewno\b",
    r"\bobiecuj[eę]\b",
    r"\bzwrot pieni[eę]dzy\b",
    r"\brefundacja\b",
    r"\brekompensat[aęy]\b",
]

# Regexy PII
CARD_NUMBER_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
PESEL_RE = re.compile(r"\b\d{11}\b")
IBAN_PL_RE = re.compile(r"\bPL\d{26}\b", re.IGNORECASE)

# Regexy identyfikatorów (do detekcji halucynacji)
POTENTIAL_ORDER_ID_RE = re.compile(r"\b\d{4,10}\b")
POTENTIAL_TRACKING_RE = re.compile(r"\b\d{10,20}\b")

# Normalizacja numeru zamówienia
ORDER_ID_NORMALIZE_RE = re.compile(r"(?:zam[oó]wieni[ea]|order|ord)?[ #]*([0-9]{4,10})", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Walidacja
# ---------------------------------------------------------------------------


def validate_response(text: str, channel: str, known_ids: set[str]) -> tuple[bool, str]:
    """
    Waliduje odpowiedź agenta.
    Zwraca (is_valid, reason). Jeżeli False, agent musi wygenerować odpowiedź ponownie.
    """
    if not text or not text.strip():
        return False, "empty_response"

    max_len = MAX_LEN.get(channel, 1500)
    if len(text) > max_len:
        return False, f"response_too_long:{len(text)}>{max_len}"

    lower = text.lower()
    for pattern in BLACKLIST_PHRASES:
        if re.search(pattern, lower):
            return False, f"blacklist_phrase:{pattern}"

    if CARD_NUMBER_RE.search(text):
        return False, "pii_leak:card_number"
    if PESEL_RE.search(text):
        return False, "pii_leak:pesel"
    if IBAN_PL_RE.search(text):
        return False, "pii_leak:iban"

    # Walidacja że numery zamówień w odpowiedzi są tymi które zwróciły narzędzia
    quoted = set(POTENTIAL_ORDER_ID_RE.findall(text))
    if quoted and known_ids:
        hallucinated = quoted - known_ids
        if hallucinated:
            return False, f"hallucinated_ids:{','.join(sorted(hallucinated))}"

    return True, "ok"


# ---------------------------------------------------------------------------
# PII redaction
# ---------------------------------------------------------------------------


def redact_pii(text: str) -> str:
    """Zastępuje PII (karty, PESEL, IBAN) placeholderami. Do logów i przed wysłaniem do LLM."""
    text = CARD_NUMBER_RE.sub("[CARD_REDACTED]", text)
    text = PESEL_RE.sub("[PESEL_REDACTED]", text)
    text = IBAN_PL_RE.sub("[IBAN_REDACTED]", text)
    return text


# ---------------------------------------------------------------------------
# Normalizacja danych identyfikacji
# ---------------------------------------------------------------------------


def normalize_order_id(raw: str) -> str | None:
    """Wyciąga numer zamówienia z dowolnego formatu (#12345, zamowienie 12345, itp.)."""
    if not raw:
        return None
    m = ORDER_ID_NORMALIZE_RE.search(raw.strip())
    return m.group(1) if m else None


def normalize_email(raw: str) -> str | None:
    """Normalizuje e-mail (lowercase, trim)."""
    if not raw:
        return None
    e = raw.strip().lower()
    return e if "@" in e and "." in e.split("@")[-1] else None


def verify_identity_input(
    order_id: str,
    email: str | None = None,
    phone_last_4: str | None = None,
) -> dict:
    """Zwraca znormalizowane dane wejściowe do dalszej weryfikacji w Shopify/BaseLinker."""
    return {
        "order_id": normalize_order_id(order_id),
        "email": normalize_email(email) if email else None,
        "phone_last_4": phone_last_4.strip() if phone_last_4 and phone_last_4.strip().isdigit() else None,
    }
