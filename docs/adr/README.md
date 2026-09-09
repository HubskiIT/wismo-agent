# Architecture Decision Records

Ten katalog zawiera zapis kluczowych decyzji architektonicznych projektu, zgodnie z wzorcem [Michael Nygard ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Dlaczego ADRs

Kod pokazuje **co** system robi. ADRs pokazują **dlaczego**. Bez tego następny inżynier (albo ty za 6 miesięcy) będzie zgadywał dlaczego wybraliśmy Redis zamiast Postgres dla sesji, dlaczego Sonnet zamiast GPT-4, dlaczego guardrails po stronie serwera zamiast tylko w promptcie.

## Lista

| Nr | Tytuł | Status |
|----|-------|--------|
| [001](001-orchestration-n8n.md) | Wybór n8n jako orkiestratora workflowów | accepted |
| [002](002-llm-claude-sonnet.md) | Claude Sonnet jako główny LLM, GPT-4o mini jako fallback | accepted |
| [003](003-server-side-guardrails.md) | Guardrails po stronie serwera, nie tylko w promptcie | accepted |
| [004](004-redis-for-sessions.md) | Redis (nie PostgreSQL) dla pamięci sesji | accepted |
| [005](005-llm-cost-limits.md) | Twarde limity kosztowe LLM per klient | proposed |

## Jak dodać nowy ADR

```bash
cp docs/adr/000-template.md docs/adr/00N-tytul-decyzji.md
```

Kolejny numer to `printf "%03d" $(($(ls docs/adr/[0-9]*.md | wc -l)))`. Wypełnij template, dodaj wpis do tabeli powyżej, commit z prefixem `docs(adr):`.

## Kiedy pisać ADR

1. Nowa technologia dodana do stacku.
2. Zmiana wzorca architektonicznego (np. z sync na async).
3. Deprekacja komponentu.
4. Trade off między dwoma sensownymi opcjami gdzie wybór nie jest oczywisty.
5. Decyzja która wpłynie na wiele modułów projektu.

Nie pisz ADR dla:

1. Wyboru biblioteki utility (chyba że wpływa na cały projekt).
2. Refactoru w obrębie jednego modułu.
3. Fixu bugów.
