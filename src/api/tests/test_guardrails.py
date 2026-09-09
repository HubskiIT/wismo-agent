"""Testy jednostkowe warstwy guardraili."""

import pytest

from api.services.guardrails import (
    normalize_email,
    normalize_order_id,
    redact_pii,
    validate_response,
    verify_identity_input,
)


class TestValidateResponse:
    def test_ok_short_widget_response(self):
        ok, reason = validate_response(
            "Twoje zamowienie 12345 jest w drodze.",
            channel="widget",
            known_ids={"12345"},
        )
        assert ok is True
        assert reason == "ok"

    def test_empty_response_rejected(self):
        ok, reason = validate_response("", channel="widget", known_ids=set())
        assert ok is False
        assert reason == "empty_response"

    def test_too_long_widget_response_rejected(self):
        ok, reason = validate_response("a" * 900, channel="widget", known_ids=set())
        assert ok is False
        assert "response_too_long" in reason

    def test_blacklist_phrase_gwarantuje(self):
        ok, reason = validate_response(
            "Gwarantuję że paczka będzie jutro.",
            channel="widget",
            known_ids=set(),
        )
        assert ok is False
        assert "blacklist_phrase" in reason

    def test_blacklist_phrase_zwrot_pieniedzy(self):
        ok, reason = validate_response(
            "Otrzymasz zwrot pieniędzy w ciągu 3 dni.",
            channel="widget",
            known_ids=set(),
        )
        assert ok is False
        assert "blacklist_phrase" in reason

    def test_pii_card_number_rejected(self):
        ok, reason = validate_response(
            "Zapisałem kartę 4532015112830366.",
            channel="widget",
            known_ids=set(),
        )
        assert ok is False
        assert reason == "pii_leak:card_number"

    def test_pii_pesel_rejected(self):
        ok, reason = validate_response(
            "Twoj PESEL to 92042812345 zgadza sie.",
            channel="widget",
            known_ids=set(),
        )
        assert ok is False
        assert reason == "pii_leak:pesel"

    def test_hallucinated_order_id_rejected(self):
        ok, reason = validate_response(
            "Twoje zamowienie 99999 jest w drodze.",
            channel="widget",
            known_ids={"12345"},
        )
        assert ok is False
        assert "hallucinated_ids" in reason

    def test_multiple_known_ids_ok(self):
        ok, reason = validate_response(
            "Twoje zamowienia 12345 i 67890 zostana wyslane.",
            channel="widget",
            known_ids={"12345", "67890"},
        )
        assert ok is True


class TestRedactPii:
    def test_redact_card(self):
        result = redact_pii("Numer karty to 4532015112830366 i to wszystko.")
        assert "4532015112830366" not in result
        assert "[CARD_REDACTED]" in result

    def test_redact_pesel(self):
        result = redact_pii("Mój PESEL to 92042812345.")
        assert "92042812345" not in result
        assert "[PESEL_REDACTED]" in result

    def test_redact_iban(self):
        result = redact_pii("Konto PL61109010140000071219812874")
        assert "PL61109010140000071219812874" not in result
        assert "[IBAN_REDACTED]" in result

    def test_no_pii_unchanged(self):
        text = "Twoje zamowienie 12345 jest w drodze."
        assert redact_pii(text) == text


class TestNormalizeOrderId:
    @pytest.mark.parametrize("raw,expected", [
        ("12345", "12345"),
        ("#12345", "12345"),
        ("Order #12345", "12345"),
        ("zamowienie 12345", "12345"),
        ("Zamowienie #67890", "67890"),
        ("ord 999999", "999999"),
    ])
    def test_valid_formats(self, raw, expected):
        assert normalize_order_id(raw) == expected

    def test_empty_returns_none(self):
        assert normalize_order_id("") is None

    def test_no_digits_returns_none(self):
        assert normalize_order_id("brak numeru") is None


class TestNormalizeEmail:
    def test_lowercase_and_trim(self):
        assert normalize_email("  Anna.Kowalska@Example.COM  ") == "anna.kowalska@example.com"

    def test_invalid_returns_none(self):
        assert normalize_email("nie-email") is None

    def test_empty_returns_none(self):
        assert normalize_email("") is None


class TestVerifyIdentityInput:
    def test_full_input(self):
        result = verify_identity_input(
            order_id="#12345",
            email="Anna@example.com",
            phone_last_4="1234",
        )
        assert result == {
            "order_id": "12345",
            "email": "anna@example.com",
            "phone_last_4": "1234",
        }

    def test_only_order(self):
        result = verify_identity_input(order_id="12345")
        assert result["order_id"] == "12345"
        assert result["email"] is None
        assert result["phone_last_4"] is None

    def test_invalid_phone(self):
        result = verify_identity_input(order_id="12345", phone_last_4="abcd")
        assert result["phone_last_4"] is None
