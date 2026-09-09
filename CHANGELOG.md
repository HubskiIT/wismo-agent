# Changelog

Wszystkie znaczące zmiany w projekcie są dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/) i [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet.

### Changed
- Nothing yet.

### Deprecated
- Nothing yet.

### Removed
- Nothing yet.

### Fixed
- Nothing yet.

### Security
- Nothing yet.

## [0.1.0] - 2026-09-09

### Added
- Pierwsza wersja szkieletu WISMO Agent.
- 8 workflowów n8n w JSON:
  - `01_main_agent` główny workflow czatu z 9 węzłami.
  - `02_verify_identity` sub workflow weryfikacji tożsamości z fuzzy matchingiem e-maila.
  - `03_escalation_handler` HITL do Slacka z Block Kit i przyciskami akcji.
  - `04_proactive_delay_notifier` cron co godzinę wykrywający opóźnienia 36h+.
  - `05_tool_get_order` z routingiem Shopify vs BaseLinker.
  - `06_tool_get_tracking` z auto detekcją przewoźnika (InPost, DPD, DHL, Poczta Polska, FedEx, UPS).
  - `07_channel_whatsapp` z Twilio i Interactive Buttons.
  - `08_channel_email` IMAP polling z parserem cytatów i sygnatur.
- Mikroserwis FastAPI (`src/api/`) z guardrails, PII redaction i normalizacją identyfikacji.
- 27 testów pytest, wszystkie zielone.
- Docker Compose z 7 usługami: n8n, PostgreSQL 16, Redis 7, wismo-api, Nginx, Loki, Grafana.
- Nginx conf z rate limitingiem per IP plus security headers.
- Bruno collection z testami dla Shopify Admin API, InPost ShipX API, n8n webhooks.
- Skill `wismo-workflow-builder` dla Claude Code.
- Dokumentacja produkcyjna:
  - `README.md` dwujęzyczny PL/EN z badges i Mermaid.
  - `docs/SPECYFIKACJA.md` pełna spec (Część A, B, C, D plus załączniki).
  - `docs/ARCHITECTURE.md` warstwy, decyzje, trade offs.
  - `docs/DEPLOYMENT.md` trzy ścieżki: Hetzner, Coolify, Railway.
  - `docs/GITHUB_SETUP.md` krok po kroku setup repo.
  - `docs/RECORDING.md` scenariusz filmu YouTube.
- CI: pytest, ruff, docker build smoke, gitleaks secrets scan.
- Makefile z 15 komendami dla wygody developer experience.

### Security
- Guardrails po stronie serwera (blacklist zwrotów, PII redaction, walidacja halucynacji).
- Rate limiting per IP w Nginx (widget 30 rpm, api 120 rpm).
- Non root user w kontenerze wismo-api.
- Postgres z scram-sha-256 auth.
- Gitleaks w CI blokuje commity z sekretami.
- Automatyczne generowanie `N8N_ENCRYPTION_KEY` przez `make init`.

[Unreleased]: https://github.com/grzybowski-it/wismo-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/grzybowski-it/wismo-agent/releases/tag/v0.1.0
