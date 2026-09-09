# 003. Guardrails po stronie serwera, nie tylko w promptcie

Data: 2026-09-09
Status: accepted
Deciders: Hubert Grzybowski

## Kontekst

Agent LLM ma nie:

1. Obiecywać zwrotów, rekompensat, gwarancji.
2. Ujawniać zawartości bazy klientów (fishing e-maili).
3. Zwracać halucynowanych numerów zamówień lub tracking numbers.
4. Przepuszczać PII (numery kart, PESEL) w output.

Pytanie: gdzie egzekwować te zasady?

## Rozważane opcje

1. **Tylko w system prompcie**. Instrukcja w tekście: "nie obiecuj X, nie ujawniaj Y".
2. **Tylko w post processing**. Regex plus reguły w kodzie, po odpowiedzi LLM ale przed wysłaniem.
3. **Hybrid: prompt plus post processing (guardrails w wismo-api)**.
4. **Framework typu LLM Guard albo Rebuff**.

## Decyzja

**Hybrid**. System prompt zawiera instrukcje (jasność intencji dla LLM), plus **twarda warstwa guardraili w wismo-api** która waliduje każdą odpowiedź przed wysłaniem.

## Rationale

Prompt sam z siebie **nie wystarcza**. Prompt injection to udowodniona kategoria ataków (Simon Willison, OWASP LLM Top 10). Instrukcja "nie obiecuj rekompensat" może zostać obalona przez kreatywnie sformułowany input klienta.

Post processing daje **twarde blokady**:

1. Blacklist zwrotów (regex): "gwarantuj\[eę\]", "zwrot pieni\[eę\]dzy", "obiecuj\[eę\]".
2. Walidacja że każdy numer 4 do 10 cyfr w odpowiedzi był w outputach narzędzi (`known_ids`). Halucynacja idzie do bin.
3. PII regex: numery kart (13 do 19 cyfr), PESEL (11 cyfr), IBAN PL.
4. Limit długości per kanał (800 znaków widget, 1000 WhatsApp, 2000 e-mail).

Jeżeli walidacja się wywala, agent generuje odpowiedź ponownie (max 2 próby, potem eskalacja).

## Konsekwencje

### Pozytywne

1. Defense in depth. Nawet jeżeli prompt injection przebije system prompt, guardrails serwerowe łapią.
2. Testowalne. 27 testów pytest pokrywa scenariusze (test_guardrails.py).
3. Auditowalne. Każde odrzucenie loguje się z `reason_code` do Postgres, widać w Grafanie.

### Negatywne

1. Overhead per odpowiedź (P95 dodane 50 do 100 ms).
2. Fałszywe pozytywy możliwe (klient używający słowa "gwarancja" w normalnym kontekście). Mitygacja: whitelisting per kontekst, iteracja regex na produkcji.
3. Utrzymanie dwóch miejsc (prompt plus regex). Zmiana wymaga aktualizacji obu.

### Neutralne

1. Można doklejenie LLM Guard albo Rebuff do wejścia (nie wyjścia), żeby dodatkowo klasyfikować prompt injection. Planowane, patrz roadmap.
