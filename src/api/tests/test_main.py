"""Testy endpointów FastAPI. Weryfikują kontrakt HTTP, licznikami Prometheus i integrację z warstwą guardraili."""

from fastapi.testclient import TestClient

from api.main import app, metrics

client = TestClient(app)


def _reset_metrics() -> None:
    for k in metrics:
        metrics[k] = 0


class TestHealth:
    def test_health_returns_200_and_status_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["service"] == "wismo-api"
        assert body["version"] == "0.1.0"

    def test_ready_returns_200_and_uptime(self):
        r = client.get("/ready")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"
        assert isinstance(body["uptime_s"], int)
        assert body["checks"]["self"] == "ok"


class TestMetrics:
    def test_metrics_prometheus_exposition_format(self):
        r = client.get("/metrics")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/plain")
        text = r.text
        assert "# HELP wismo_requests_total" in text
        assert "# TYPE wismo_requests_total counter" in text
        assert "wismo_requests_total " in text
        assert "wismo_uptime_seconds " in text

    def test_metrics_increment_on_traffic(self):
        _reset_metrics()
        client.get("/health")
        client.get("/health")
        r = client.get("/metrics")
        assert "wismo_requests_total 3" in r.text


class TestGuardrailsValidate:
    def test_valid_short_response(self):
        _reset_metrics()
        r = client.post(
            "/guardrails/validate",
            json={
                "text": "Twoje zamowienie 12345 jest w drodze.",
                "channel": "widget",
                "known_ids": ["12345"],
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["is_valid"] is True
        assert body["reason"] == "ok"
        assert metrics["validate_ok_total"] == 1

    def test_blacklist_phrase_rejected_and_counter_incremented(self):
        _reset_metrics()
        r = client.post(
            "/guardrails/validate",
            json={
                "text": "Gwarantuje ze paczka bedzie jutro.",
                "channel": "widget",
                "known_ids": [],
            },
        )
        body = r.json()
        assert body["is_valid"] is False
        assert "blacklist_phrase" in body["reason"]
        assert metrics["validate_rejected_total"] == 1
        assert metrics["blacklist_hits_total"] == 1

    def test_hallucinated_order_id_increments_counter(self):
        _reset_metrics()
        r = client.post(
            "/guardrails/validate",
            json={
                "text": "Twoje zamowienie 99999 jest w drodze.",
                "channel": "widget",
                "known_ids": ["12345"],
            },
        )
        body = r.json()
        assert body["is_valid"] is False
        assert "hallucinated_ids" in body["reason"]
        assert metrics["hallucinations_blocked_total"] == 1

    def test_channel_whatsapp_length_limit(self):
        r = client.post(
            "/guardrails/validate",
            json={"text": "a" * 1200, "channel": "whatsapp", "known_ids": []},
        )
        assert r.json()["is_valid"] is False


class TestGuardrailsRedact:
    def test_redact_card_number_and_increment_counter(self):
        _reset_metrics()
        r = client.post(
            "/guardrails/redact",
            json={"text": "Numer karty to 4532015112830366."},
        )
        assert r.status_code == 200
        body = r.json()
        assert "4532015112830366" not in body["redacted"]
        assert "[CARD_REDACTED]" in body["redacted"]
        assert metrics["pii_redacted_total"] == 1

    def test_no_pii_does_not_increment_counter(self):
        _reset_metrics()
        r = client.post(
            "/guardrails/redact",
            json={"text": "Zamowienie 12345 jest w drodze."},
        )
        assert r.json()["redacted"] == "Zamowienie 12345 jest w drodze."
        assert metrics["pii_redacted_total"] == 0


class TestIdentityNormalize:
    def test_full_input_normalized(self):
        r = client.post(
            "/identity/normalize",
            json={
                "order_id": "#12345",
                "email": "Anna@Example.COM",
                "phone_last_4": "1234",
            },
        )
        assert r.status_code == 200
        assert r.json() == {
            "order_id": "12345",
            "email": "anna@example.com",
            "phone_last_4": "1234",
        }

    def test_minimal_input(self):
        r = client.post(
            "/identity/normalize",
            json={"order_id": "ord 999999"},
        )
        body = r.json()
        assert body["order_id"] == "999999"
        assert body["email"] is None
        assert body["phone_last_4"] is None
