"""WISMO Agent mikroserwis. FastAPI plus warstwa guardraili."""

import logging
import sys
import time
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from api.services.guardrails import (
    redact_pii,
    validate_response,
    verify_identity_input,
)

# ---------------------------------------------------------------------------
# Logging (structured, JSON friendly)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger("wismo-api")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="WISMO Agent API",
    description="Guardrails, PII redaction and identity normalization microservice.",
    version="0.1.0",
    contact={"name": "Hubert Grzybowski", "email": "grzybowski.it@gmail.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

START_TIME = time.time()

# ---------------------------------------------------------------------------
# In memory Prometheus style counters (podstawa; produkcyjnie: prometheus_client)
# ---------------------------------------------------------------------------
metrics = {
    "requests_total": 0,
    "validate_ok_total": 0,
    "validate_rejected_total": 0,
    "pii_redacted_total": 0,
    "hallucinations_blocked_total": 0,
    "blacklist_hits_total": 0,
}


@app.middleware("http")
async def count_requests(request: Request, call_next):
    metrics["requests_total"] += 1
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    log.info(
        f"{request.method} {request.url.path} status={response.status_code} duration_ms={duration_ms:.2f}"
    )
    return response


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ValidateRequest(BaseModel):
    text: str = Field(..., description="Odpowiedź agenta do walidacji.")
    channel: Literal["widget", "whatsapp", "email"] = "widget"
    known_ids: list[str] = Field(default_factory=list)


class ValidateResponse(BaseModel):
    is_valid: bool
    reason: str
    redacted_text: str


class RedactRequest(BaseModel):
    text: str


class VerifyRequest(BaseModel):
    order_id: str
    email: str | None = None
    phone_last_4: str | None = None


# ---------------------------------------------------------------------------
# Health, readiness, metrics
# ---------------------------------------------------------------------------


@app.get("/health", tags=["ops"], summary="Liveness probe")
def health() -> dict:
    """Zwraca 200 dopóki proces żyje. Do Docker HEALTHCHECK i k8s liveness."""
    return {"status": "ok", "service": "wismo-api", "version": app.version}


@app.get("/ready", tags=["ops"], summary="Readiness probe")
def ready() -> JSONResponse:
    """Zwraca 200 kiedy serwis może przyjmować ruch. W przyszłości: check Redis i Postgres."""
    # TODO: dodaj sprawdzenie połączenia z Redis i Postgres
    ready_state = {
        "status": "ready",
        "uptime_s": int(time.time() - START_TIME),
        "checks": {
            "self": "ok",
            # "redis": "ok",  # planowane
            # "postgres": "ok",  # planowane
        },
    }
    return JSONResponse(content=ready_state, status_code=200)


@app.get("/metrics", tags=["ops"], summary="Prometheus metrics", response_class=PlainTextResponse)
def prometheus_metrics() -> str:
    """Prometheus text exposition format."""
    lines = [
        "# HELP wismo_requests_total Total HTTP requests received",
        "# TYPE wismo_requests_total counter",
        f"wismo_requests_total {metrics['requests_total']}",
        "# HELP wismo_validate_ok_total Guardrails validations that passed",
        "# TYPE wismo_validate_ok_total counter",
        f"wismo_validate_ok_total {metrics['validate_ok_total']}",
        "# HELP wismo_validate_rejected_total Guardrails validations that rejected the response",
        "# TYPE wismo_validate_rejected_total counter",
        f"wismo_validate_rejected_total {metrics['validate_rejected_total']}",
        "# HELP wismo_hallucinations_blocked_total Hallucinated order IDs blocked",
        "# TYPE wismo_hallucinations_blocked_total counter",
        f"wismo_hallucinations_blocked_total {metrics['hallucinations_blocked_total']}",
        "# HELP wismo_blacklist_hits_total Blacklisted phrases caught",
        "# TYPE wismo_blacklist_hits_total counter",
        f"wismo_blacklist_hits_total {metrics['blacklist_hits_total']}",
        "# HELP wismo_uptime_seconds Uptime in seconds",
        "# TYPE wismo_uptime_seconds gauge",
        f"wismo_uptime_seconds {int(time.time() - START_TIME)}",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Guardrails endpoints
# ---------------------------------------------------------------------------


@app.post("/guardrails/validate", response_model=ValidateResponse, tags=["guardrails"])
def validate(req: ValidateRequest) -> ValidateResponse:
    """Waliduje odpowiedź agenta przed wysłaniem do klienta."""
    redacted = redact_pii(req.text)
    ok, reason = validate_response(text=req.text, channel=req.channel, known_ids=set(req.known_ids))
    if ok:
        metrics["validate_ok_total"] += 1
    else:
        metrics["validate_rejected_total"] += 1
        if "hallucinated_ids" in reason:
            metrics["hallucinations_blocked_total"] += 1
        if "blacklist_phrase" in reason:
            metrics["blacklist_hits_total"] += 1
        log.warning(f"guardrails_reject reason={reason} channel={req.channel}")
    return ValidateResponse(is_valid=ok, reason=reason, redacted_text=redacted)


@app.post("/guardrails/redact", tags=["guardrails"])
def redact(req: RedactRequest) -> dict:
    """Usuwa PII (numery kart, PESEL, IBAN) z tekstu."""
    redacted = redact_pii(req.text)
    if redacted != req.text:
        metrics["pii_redacted_total"] += 1
    return {"redacted": redacted}


@app.post("/identity/normalize", tags=["identity"])
def normalize_identity(req: VerifyRequest) -> dict:
    """Normalizuje dane wejściowe do weryfikacji tożsamości."""
    return verify_identity_input(
        order_id=req.order_id,
        email=req.email,
        phone_last_4=req.phone_last_4,
    )
