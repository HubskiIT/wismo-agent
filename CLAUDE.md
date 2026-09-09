# CLAUDE.md

Ten plik ładuje się automatycznie przy każdej sesji Claude Code w tym repo. Trzymaj go zwięzły i aktualny, to on decyduje jak dobrze Claude rozumie projekt.

## Projekt

WISMO Agent. Moduł TIER 1 z matrycy usług "Automatyzacja e-commerce". Agent AI który obsługuje 35 do 50 procent zapytań "gdzie jest moja paczka" w sklepach e-commerce. Wdrożenie 14 dni. ROI 30 do 45 dni.

Autor: Hubert Grzybowski (grzybowski.it@gmail.com).
Firma: Automatyzacja e-commerce, usługi AI dla sklepów Shopify plus BaseLinker.

## Stack techniczny

1. **Orkiestracja**: n8n (workflowy JSON w `n8n-workflows/`).
2. **Konteneryzacja**: Docker Compose, wszystko w `docker/`.
3. **LLM**: Claude Sonnet primary, GPT-4o mini fallback.
4. **Mikroserwis**: FastAPI Python 3.12 w `src/api/` (guardrails plus PII redaction).
5. **Dane**: PostgreSQL 16, Redis 7.
6. **Proxy i TLS**: Nginx (prod: Caddy z auto Let's Encrypt).
7. **Observability**: Grafana plus Loki.
8. **Testy API**: Bruno collections w `bruno-collection/`.

## Struktura kluczowa

```
wismo-agent/
├── CLAUDE.md                     ← ten plik
├── README.md                     PL/EN produkcyjny README
├── Makefile                      make up, down, import, test, demo, logs
├── docker/                       compose, nginx conf, env template
├── n8n-workflows/                8 workflowów JSON gotowych do importu
├── src/api/                      FastAPI mikroserwis, 27 testów pytest zielonych
├── src/prompts/system_prompt.md  produkcyjny prompt agenta
├── bruno-collection/             testy API Shopify, InPost, n8n webhooks
├── skills/wismo-workflow-builder/ własny skill dla Claude Code
├── docs/                         SPECYFIKACJA, ARCHITECTURE, DEPLOYMENT, GITHUB_SETUP, RECORDING
└── .github/workflows/ci.yml      pytest, ruff, docker build, gitleaks
```

## Krytyczne pliki do przeczytania w pierwszej kolejności

Jeśli nie znasz jeszcze projektu, przeczytaj w tej kolejności:

1. `docs/ARCHITECTURE.md` big picture i decyzje architektoniczne.
2. `docs/SPECYFIKACJA.md` pełna spec (Część A, B, C, D plus załączniki).
3. `n8n-workflows/README.md` mapa zależności 8 workflowów.
4. `src/prompts/system_prompt.md` prompt agenta z guardrailami.
5. `skills/wismo-workflow-builder/SKILL.md` skill do generowania nowych workflowów.

## Zasady pracy

### Workflowy n8n

1. **Zawsze** czytaj `skills/wismo-workflow-builder/SKILL.md` zanim zbudujesz albo zmienisz workflow n8n. Tam są zasady nazewnictwa, kolejność węzłów, standardy Function Node.
2. Nowe workflowy: prefix numeryczny (`09_...`, `10_...`), zapisuj w `n8n-workflows/` jako JSON, commit do repo.
3. Sub workflowy dla Tool Calling zawsze mają: retry 3x, backoff 1s/2s/4s, timeout 5s per próba, structured error handler.
4. Nie łącz Agent LLM bezpośrednio z Respond bez guardraili pośrodku.

### Kod Pythona (mikroserwis wismo-api)

1. Przed każdą zmianą w `src/api/` uruchom testy: `cd src && python -m pytest api/tests/ -v`.
2. Po zmianach: `ruff format api/` i `ruff check api/`.
3. Nowe funkcje w `services/` mają mieć testy w `tests/`. 100 procent pokrycia to nie cel, ale kluczowe ścieżki (guardrails, PII redaction, normalizacja) muszą być testowane.
4. Nie dodawaj zależności bez uzasadnienia. Utrzymuj `requirements.txt` chudy.

### Bezpieczeństwo

1. Nigdy nie commituj `docker/.env` (jest w `.gitignore`, plus gitleaks w CI).
2. Wszystkie sekrety w `.env.example` jako placeholdery, nigdy realne wartości.
3. Przed pushem: `git diff --cached | grep -iE "sk-|shpat|whsec|api[_-]?key"` żeby sprawdzić że nic nie przecieka.
4. Guardrails to warstwa bezpieczeństwa, nie tylko UX. Nie osłabiaj ich bez rozmowy o konsekwencjach.

### Git i commits

1. Konwencja: [Conventional Commits](https://www.conventionalcommits.org).
   `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
2. Branch: `main` chroniony, wszystko idzie przez PR z zielonym CI.
3. Przed pushem: `make test` (pytest plus opcjonalnie Bruno).

### Komunikacja z Hubertem

1. **Odpowiadaj po polsku**, chyba że explicite proszę o angielski (np. dla dokumentacji dla klienta zagranicznego).
2. **Bez myślników, pauz i półpauz**. Zamiast nich: kropki, przecinki, numeracja, dwukropki.
3. **Konkret bez lania wody**. Zaczynaj od informacji, nie od "chętnie pomogę".
4. Kod pisz produkcyjnie od razu. Nie prototypuj, nie zostawiaj TODO bez uzasadnienia.
5. Jak coś nie działa, zaproponuj konkretny fix, nie generic checklist.

## Częste komendy

```bash
make init         # utworz .env z wygenerowanym N8N_ENCRYPTION_KEY
make up           # uruchom cały stack
make down         # zatrzymaj
make logs         # podglad logow wszystkich uslug
make logs-n8n     # tylko n8n
make logs-api     # tylko wismo-api
make import       # import 8 workflowow w poprawnej kolejnosci
make test         # pytest plus Bruno
make demo         # 3 scenariusze demo (widget webhook)
make shell-api    # bash w kontenerze wismo-api
make shell-db     # psql w kontenerze postgres
make nuke         # DESTROY: usuwa wolumeny (dane znikaja)
```

## Aktualny stan projektu

- [x] Szkielet repo (32 pliki, MIT license)
- [x] 8 workflowów n8n (main agent, sub workflowy narzędzi, eskalacje, kanały widget/WhatsApp/email)
- [x] Mikroserwis FastAPI z 27 testami pytest (zielone)
- [x] Docker Compose z 7 usługami plus healthchecki
- [x] Nginx conf z rate limitingiem plus security headers
- [x] Bruno collection dla Shopify, InPost, n8n webhooks
- [x] Skill `wismo-workflow-builder` dla Claude Code
- [x] Dokumentacja: SPECYFIKACJA, ARCHITECTURE, DEPLOYMENT, GITHUB_SETUP, RECORDING
- [x] CI: pytest, ruff, docker build, gitleaks
- [ ] Pierwszy deploy na Hetzner VPS
- [ ] Realne credentials Shopify plus Anthropic w produkcji
- [ ] Nagranie filmu na YouTube (scenariusz w `docs/RECORDING.md`)
- [ ] Pierwszy klient produkcyjny

## Cele biznesowe (żebyś rozumiał kontekst decyzji)

1. **Portfolio piece** dla mojej firmy Automatyzacja e-commerce. Repo publiczne na GitHubie.
2. **YouTube content** flagship film o budowie agenta w 15 minut plus 5 odcinkowy devlog.
3. **Base do sprzedaży** dla klientów TIER 1. Standardowy setup 8 do 15 tysięcy PLN netto, maintenance 1,5 do 3,5 tysiąca miesięcznie.
4. **Fundament pod kolejne moduły**: Odzyskiwanie koszyków AI, Generator opisów Vision AI, Portal Zwrotów. Wspólne komponenty (n8n, Docker, FastAPI, prompt architecture) będą reużywane.

## Anti patterns (nie rób tego)

1. Nie proponuj przejścia na inne frameworki (LangChain, LangGraph, CrewAI). Stack jest ustalony, klienci mają rozumieć że siedzą na n8n.
2. Nie dodawaj funkcjonalności "na wszelki wypadek". Zasada YAGNI, dodajemy kiedy klient zapyta.
3. Nie zmieniaj system promptu bez testu na 20 scenariuszach z `docs/RECORDING.md`. Prompt to serce systemu.
4. Nie usuwaj testów żeby "przyspieszyć". Testy trzymają guardrails w ryzach.
5. Nie łącz się z LLM w Function Node n8n. Wszystkie wywołania LLM idą przez Agent Node z Tool Calling.

## Kontakt i eskalacja (do Ciebie, Claude)

Jeśli w trakcie pracy zorientujesz się że:

1. Prosisz mnie o decyzję której nie umiesz podjąć sam, zapytaj konkretnie z propozycją 2 do 3 opcji.
2. Widzisz błąd projektowy w istniejącej specyfikacji, powiedz mi. Docs nie są święte.
3. Coś w Claude API zmieniło się od 2026, użyj web search zanim zaproponujesz rozwiązanie.
4. Musisz uruchomić długo działający proces (compose build od zera, testy integracyjne), poczekaj na wynik i pokaż mi output, nie strzelaj w ciemno.
