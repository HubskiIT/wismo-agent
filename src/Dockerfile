# =============================================================================
# WISMO Agent API. Multistage Dockerfile.
# Rozmiar końcowy: około 90 MB (vs 450 MB przy naiwnym pojedynczym stage).
# =============================================================================

# --- Stage 1: builder ---
FROM python:3.14-slim AS builder

WORKDIR /build

# Zależności do kompilacji (Levenshtein wymaga C compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalacja do izolowanego prefix (kopiujemy do finalnego obrazu)
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: runtime ---
FROM python:3.14-slim AS runtime

# Metadata (OCI standard labels)
LABEL org.opencontainers.image.title="WISMO Agent API"
LABEL org.opencontainers.image.description="Guardrails, PII redaction and identity normalization microservice"
LABEL org.opencontainers.image.authors="Hubert Grzybowski <grzybowski.it@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/grzybowski-it/wismo-agent"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Minimalne zależności runtime (curl do healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 wismo

# Kopiuj tylko potrzebne paczki z buildera
COPY --from=builder --chown=wismo:wismo /root/.local /home/wismo/.local
ENV PATH=/home/wismo/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Kod aplikacji
COPY --chown=wismo:wismo api/ ./api/

USER wismo
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
