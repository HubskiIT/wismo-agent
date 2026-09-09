# 005. Twarde limity kosztowe LLM per klient

Data: 2026-09-09
Status: proposed
Deciders: Hubert Grzybowski

## Kontekst

Anthropic pay per use. Bot który spamuje agenta może wyczerpać budżet klienta w kilka godzin. Zaobserwowane w podobnych projektach: 500 USD budżet zjadany przez atak w noc. Klient rano widzi rachunek, dzwoni z gniewem.

## Rozważane opcje

1. **Bez limitów**. Zaufanie do rate limitów Anthropic i Nginx.
2. **Miękkie limity**. Alerty do klienta gdy dzienny koszt przekracza próg.
3. **Twarde limity**. Middleware w wismo-api liczy koszt per klient dziennie/miesięcznie. Powyżej progu: zwrot 429 do n8n, agent odmawia.
4. **Twarde limity plus alerty plus kill switch**.

## Decyzja

**Opcja 4: twarde limity plus alerty plus kill switch**.

## Implementacja (planowana)

Middleware w `src/api/services/cost_limits.py`:

1. Śledzenie `cost_usd` per klient (tenant_id) w Redis (key `cost:{tenant_id}:{yyyy_mm_dd}`, TTL 32 dni).
2. Progi konfigurowalne per tenant (`daily_soft`, `daily_hard`, `monthly_hard`).
3. Przy każdym wywołaniu LLM w n8n workflow: pre check wismo-api endpoint `/costs/check?tenant_id=X`. Jeżeli soft, alert Slack. Jeżeli hard, blokada.
4. Blokada: agent zwraca fallback message "Chwilowo mam ograniczoną dostępność, przekazuję do konsultanta" plus `create_escalation` z priorytetem Medium.
5. Klient dostaje daily report o kosztach w Slacku (integracja).

## Konsekwencje

### Pozytywne

1. Klient nigdy nie dostanie faktury 10x większej od oczekiwanej.
2. Atakujący nie zniszczy budżetu.
3. Można sprzedawać klientowi plan "do X zapytań miesięcznie" z jasnym cap.

### Negatywne

1. Extra middleware, extra overhead per request (dodatkowe 10 ms).
2. Fałszywy alarm dla legitymatecznej fali ruchu (Black Friday). Mitygacja: konfiguracja daily_hard elastycznie plus możliwość szybkiego podniesienia przez ops.
3. Redis jako źródło prawdy o kosztach. Reconciliation z Anthropic invoice miesięcznie.

### Neutralne

1. Design działa też dla per-użytkownikowych limitów (nie tylko per tenant), gdyby klient chciał.
