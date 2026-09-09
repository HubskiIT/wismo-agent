<!--
Dzięki za PR. Zanim złożysz, upewnij się że wypełniłeś sekcje poniżej.
Konwencja tytułu PR: Conventional Commits.
-->

## Co ta zmiana robi

<!-- Zwięzły opis, 2 do 4 zdań. Co, dlaczego, jak. -->

## Powiązane issue

Closes #

## Typ zmiany

- [ ] Bug fix (non breaking change fixing an issue)
- [ ] New feature (non breaking change adding functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Refactor
- [ ] Performance improvement
- [ ] Test coverage

## Testowanie

<!-- Jak zweryfikowałeś że zmiana działa? Jakie scenariusze przeszły? -->

- [ ] `make test` przechodzi lokalnie
- [ ] `make lint` przechodzi lokalnie
- [ ] Dodałem nowe testy pokrywające zmianę
- [ ] Uruchomiłem `make demo` i wyniki są zgodne z oczekiwaniami
- [ ] Przetestowałem w n8n UI (jeśli dotyczy workflowów)

## Checklist

- [ ] Kod jest zgodny z konwencjami projektu (`CONTRIBUTING.md`)
- [ ] Uruchomiłem pre-commit hooks
- [ ] Zaktualizowałem `CHANGELOG.md` w sekcji `[Unreleased]`
- [ ] Jeśli zmiana architektoniczna, dodałem ADR w `docs/adr/`
- [ ] Jeśli dodałem workflow, zaktualizowałem `n8n-workflows/README.md`
- [ ] Jeśli dodałem endpoint API, zaktualizowałem OpenAPI (auto z FastAPI)
- [ ] Sprawdziłem że w diffie nie ma sekretów
- [ ] PR title zgodny z Conventional Commits

## Screenshots (jeśli dotyczy)

<!-- Dla zmian w UI n8n, dashboardach Grafana, output artifact wizualnego. -->

## Uwagi dodatkowe

<!-- Cokolwiek review'er powinien wiedzieć. Trade offs, alternatywy które rozważałeś, konteksty. -->
