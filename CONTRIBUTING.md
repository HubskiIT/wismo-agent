# Contributing to WISMO Agent

Dzięki że chcesz kontrybuować. Ten dokument pokazuje jak wejść w projekt szybko i zgodnie z konwencjami.

## Zanim zaczniesz

1. Przeczytaj [`CLAUDE.md`](CLAUDE.md) który jest głównym kontekstem projektu.
2. Zajrzyj do [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) żeby zrozumieć układ.
3. Sprawdź [otwarte issues](https://github.com/grzybowski-it/wismo-agent/issues) i [dyskusje](https://github.com/grzybowski-it/wismo-agent/discussions).
4. Jeżeli planujesz duży PR, otwórz najpierw issue z propozycją. Uniknięcie sytuacji "napisałem 500 linii kodu, a właściciel projektu chce to zrobić inaczej".

## Środowisko dev

### Opcja 1: Codespaces (klik i klon)

Klik "Code" → "Codespaces" → "Create codespace on main". Devcontainer w `.devcontainer/` skonfiguruje wszystko automatycznie.

### Opcja 2: Lokalnie

Wymagane: Docker Desktop, Node 20+, Python 3.12, Git.

```bash
git clone https://github.com/grzybowski-it/wismo-agent.git
cd wismo-agent
make init          # tworzy docker/.env z wygenerowanym sekretem
# uzupełnij docker/.env swoimi kluczami API
make up            # startuje cały stack
make import        # importuje 8 workflowów do n8n
```

## Pre-commit hooks

Zainstaluj przed pierwszym commitem:

```bash
pip install pre-commit
pre-commit install
```

Od teraz każdy commit uruchamia: ruff (Python), gitleaks (sekrety), yamllint, prettier (JSON, YAML, MD).

## Struktura commitów

Konwencja: [Conventional Commits](https://www.conventionalcommits.org).

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Typy**:

1. `feat` nowa funkcjonalność
2. `fix` naprawa błędu
3. `docs` tylko dokumentacja
4. `refactor` refactor bez zmian funkcjonalnych
5. `test` dodanie/poprawa testów
6. `chore` maintenance (dependencies, config)
7. `perf` optymalizacja wydajności
8. `ci` zmiany w CI

**Scope** (opcjonalny):

`workflows`, `api`, `docker`, `docs`, `nginx`, `bruno`, `skills`.

**Przykłady**:

```
feat(workflows): add 09_tool_send_notification for SMS/email out-of-session
fix(api): correct Levenshtein tolerance for uppercase emails
docs(architecture): document why Redis instead of Postgres for sessions
refactor(guardrails): extract blacklist patterns to separate config file
test(guardrails): cover edge cases for Polish diacritics in blacklist
chore(deps): bump fastapi from 0.115.0 to 0.115.4
```

## Pull Request checklist

Przed otwarciem PR upewnij się że:

- [ ] Testy przechodzą lokalnie: `make test`
- [ ] Lint bez błędów: `make lint`
- [ ] Nowe funkcje mają testy jednostkowe
- [ ] Zaktualizowany `CHANGELOG.md` w sekcji `[Unreleased]`
- [ ] Jeżeli zmiana wpływa na architekturę, dodany ADR w `docs/adr/`
- [ ] Commit messages zgodne z Conventional Commits
- [ ] PR title również w formacie Conventional Commit
- [ ] Brak sekretów w diffie (gitleaks powinien złapać, ale sprawdź sam)
- [ ] Jeżeli zmienia się public API, zaktualizowany OpenAPI spec

## Code review

Każdy PR wymaga:

1. Co najmniej jednego review z approval.
2. Zielonego CI (wszystkie checks pass).
3. Aktualnej gałęzi main (rebase jeżeli main się ruszył).

## Standardy kodu

### Python (`src/api/`)

1. Formatowanie: `ruff format` (line length 110).
2. Linting: `ruff check` z zestawem `E, F, W, I, N, UP, B, C4, SIM`.
3. Type hints: obowiązkowe dla wszystkich funkcji publicznych.
4. Docstringi: dla wszystkich funkcji publicznych, format Google style.
5. Testy: pytest, arrange plus act plus assert, opisowe nazwy.

### n8n workflows

1. Kolejność węzłów zgodna z `skills/wismo-workflow-builder/SKILL.md`.
2. Function Node kod w JS ES2020, bez dependencies zewnętrznych.
3. Nazwy węzłów po polsku (dla czytelności w UI n8n).
4. Webhook paths w snake_case, prefix `/webhook/wismo/{channel}`.
5. Timeouts na HTTP Request obowiązkowe (5s default).
6. Retry z exponential backoff dla wszystkich zewnętrznych API.

### Docker

1. Multistage builds gdzie ma sens (redukcja rozmiaru obrazu).
2. Non root user.
3. HEALTHCHECK w każdym Dockerfile.
4. Piny wersji dla base images (`python:3.12-slim`, nie `python:latest`).

### Dokumentacja

1. Zmiany w architekturze wymagają ADR w `docs/adr/`.
2. Nowe workflowy wymagają aktualizacji `n8n-workflows/README.md`.
3. Nowe endpointy API wymagają aktualizacji OpenAPI spec (auto z FastAPI).
4. Nowe komendy Makefile wymagają dokumentacji w `make help`.

## ADR (Architecture Decision Records)

Kiedy podejmujesz istotną decyzję architektoniczną (nowa technologia, zmiana wzorca, deprekacja komponentu), utwórz ADR:

```bash
cp docs/adr/000-template.md docs/adr/00N-tytul-decyzji.md
# edytuj plik
git add docs/adr/00N-tytul-decyzji.md
git commit -m "docs(adr): 00N tytul decyzji"
```

Format wzorowany na [Michael Nygard ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Language

- Kod, komentarze w kodzie: **English**.
- Commit messages: **English**.
- Dokumentacja użytkownika (`README.md`, `docs/`): **Polski i angielski** (dwujęzycznie gdzie się da).
- Testy i błędy: **English**.
- Issues i PR descriptions: **Polski lub angielski**, zależy od kontekstu.

## Community

1. [Discussions](https://github.com/grzybowski-it/wismo-agent/discussions) dla pytań i propozycji.
2. [Issues](https://github.com/grzybowski-it/wismo-agent/issues) dla bugów i konkretnych feature requestów.
3. E-mail dla współprac komercyjnych: `grzybowski.it@gmail.com`.

## Licencja

Kontrybuując zgadzasz się że twój kod będzie na licencji MIT (patrz [LICENSE](LICENSE)).

Dzięki że pomagasz WISMO Agent rosnąć.
