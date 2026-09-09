# =============================================================================
# WISMO Agent. Wygodne komendy do codziennej pracy z projektem.
# Użycie: `make <target>`. Bez argumentów pokazuje help.
# =============================================================================

.DEFAULT_GOAL := help
SHELL := /bin/bash
DOCKER_DIR := docker
COMPOSE := docker compose -f $(DOCKER_DIR)/docker-compose.yml --env-file $(DOCKER_DIR)/.env

.PHONY: help
help: ## Pokaż tę pomoc
	@echo ""
	@echo "  WISMO Agent. Dostępne komendy:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

.PHONY: init
init: ## Inicjalizacja projektu, generuje .env z .env.example i sekretem N8N
	@if [ ! -f $(DOCKER_DIR)/.env ]; then \
		cp $(DOCKER_DIR)/.env.example $(DOCKER_DIR)/.env; \
		SECRET=$$(openssl rand -hex 32); \
		sed -i.bak "s/CHANGE_ME_openssl_rand_hex_32/$$SECRET/" $(DOCKER_DIR)/.env && rm $(DOCKER_DIR)/.env.bak; \
		echo "✓ Utworzono $(DOCKER_DIR)/.env z wygenerowanym N8N_ENCRYPTION_KEY."; \
		echo "→ Uzupełnij pozostałe klucze API w pliku."; \
	else \
		echo "→ Plik $(DOCKER_DIR)/.env już istnieje. Nie nadpisuję."; \
	fi

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

.PHONY: up
up: ## Uruchom cały stack (n8n, postgres, redis, api, nginx, grafana)
	$(COMPOSE) up -d
	@echo ""
	@echo "  n8n     : http://localhost:5678"
	@echo "  API     : http://localhost:8000/docs"
	@echo "  Grafana : http://localhost:3000"
	@echo ""

.PHONY: down
down: ## Zatrzymaj stack
	$(COMPOSE) down

.PHONY: restart
restart: down up ## Restart

.PHONY: nuke
nuke: ## Zatrzymaj i usuń wszystkie wolumeny (DANE ZOSTANĄ USUNIĘTE)
	$(COMPOSE) down -v
	@echo "→ Wszystkie wolumeny usunięte."

# ---------------------------------------------------------------------------
# Obserwacja
# ---------------------------------------------------------------------------

.PHONY: logs
logs: ## Podgląd logów wszystkich usług
	$(COMPOSE) logs -f --tail=200

.PHONY: logs-n8n
logs-n8n: ## Podgląd logów tylko n8n
	$(COMPOSE) logs -f --tail=200 n8n

.PHONY: logs-api
logs-api: ## Podgląd logów tylko wismo-api
	$(COMPOSE) logs -f --tail=200 wismo-api

.PHONY: ps
ps: ## Status usług
	$(COMPOSE) ps

# ---------------------------------------------------------------------------
# Import workflowów i testy
# ---------------------------------------------------------------------------

.PHONY: import
import: ## Import workflowów n8n w poprawnej kolejnosci (sub workflowy przed glownym)
	@echo "→ Import sub workflowów najpierw..."
	@for f in 05_tool_get_order.json 06_tool_get_tracking.json 02_verify_identity.json 03_escalation_handler.json 01_main_agent.json 04_proactive_delay_notifier.json 07_channel_whatsapp.json 08_channel_email.json; do \
		echo "  · $$f"; \
		$(COMPOSE) exec -T n8n n8n import:workflow --input=/workflows/$$f || exit 1; \
	done
	@echo "✓ Zaimportowano 8 workflowów. Ustaw credentials w UI n8n."

.PHONY: test
test: test-api test-bruno ## Uruchom wszystkie testy

.PHONY: test-api
test-api: ## Testy pytest dla mikroserwisu FastAPI
	cd src && python -m pytest api/tests/ -v --cov=api --cov-report=term-missing

.PHONY: test-bruno
test-bruno: ## Testy kolekcji Bruno (wymaga @usebruno/cli)
	@which bru > /dev/null || (echo "Zainstaluj Bruno CLI: npm install -g @usebruno/cli" && exit 1)
	cd bruno-collection && bru run --env local

# ---------------------------------------------------------------------------
# Jakość kodu
# ---------------------------------------------------------------------------

.PHONY: lint
lint: ## Lint Pythona (ruff) plus check formatu
	cd src && ruff check api/
	cd src && ruff format --check api/

.PHONY: format
format: ## Auto format Pythona
	cd src && ruff format api/
	cd src && ruff check --fix api/

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

.PHONY: build
build: ## Rebuild obrazu wismo-api
	$(COMPOSE) build wismo-api

.PHONY: shell-api
shell-api: ## Bash w kontenerze wismo-api
	$(COMPOSE) exec wismo-api bash

.PHONY: shell-db
shell-db: ## psql w kontenerze postgres
	$(COMPOSE) exec postgres psql -U n8n

# ---------------------------------------------------------------------------
# Demo / YouTube
# ---------------------------------------------------------------------------

.PHONY: demo
demo: ## Skrypt demo do nagrania filmu, wysyła 3 testowe zapytania do agenta
	@echo ""
	@echo "→ Demo: 3 zapytania do agenta (widget webhook)"
	@echo ""
	@bash scripts/demo.sh
