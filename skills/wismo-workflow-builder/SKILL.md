---
name: wismo-workflow-builder
description: Generuje i modyfikuje workflowy n8n dla agenta CS w e-commerce (WISMO). Użyj gdy chcesz stworzyć nowy workflow do obsługi zapytań o status paczek, dodać integrację z przewoźnikiem, dopisać sub workflow narzędzia Tool Calling albo wygenerować skeleton eskalacji do Slacka.
---

# WISMO Workflow Builder

Skill do produkcji workflowów n8n dla projektu WISMO Agent. Zna standardową strukturę: webhook, normalizer, PII redact, session load, agent LLM, guardrails, session save, audit log, respond.

## Kiedy używać

1. Użytkownik prosi "dodaj workflow n8n dla WhatsApp" albo "stwórz sub workflow dla InPost".
2. Klient dołącza do projektu z inną platformą e-commerce (WooCommerce, PrestaShop) i potrzebna jest adaptacja workflowu.
3. Trzeba wygenerować sub workflow dla nowego narzędzia Tool Calling (np. `get_return_status`, `create_ticket`).
4. Refactor istniejącego workflowu (zmiana kolejności węzłów, dodanie węzła guardraili).

## Baseline: struktura workflowu głównego

Każdy workflow czatu WISMO ma tę samą kolejność 9 węzłów. Trzymaj się jej.

1. **Webhook Trigger** POST na `/webhook/wismo/{channel}`.
2. **Normalize Payload** function node, normalizuje kanał, session_id, user_message.
3. **PII Redact** HTTP POST na wismo-api `/guardrails/redact`.
4. **Load Session** Redis GET `session:{session_id}`.
5. **Agent LLM** langchain agent, model claude-sonnet-5, temp 0.2, max 1024 tokens.
6. **Guardrails Validate** HTTP POST na wismo-api `/guardrails/validate`.
7. **Save Session** Redis SET z TTL 86400.
8. **Audit Log** Postgres INSERT do `agent_conversations`.
9. **Respond** respond to webhook JSON.

## Standardy kodu Function Node

1. Zawsze normalizuj `body` przez `$input.first().json.body || $input.first().json`.
2. Zawsze generuj fallback `session_id` gdy nie ma: `${channel}_${Date.now()}`.
3. Zawsze zwracaj `[{ json: ... }]` (n8n wymaga tablicy).
4. Zwrot błędu z `{ error: 'error_code' }` (nigdy nie throw, żeby workflow nie umarł niekontrolowanie).

## Standardy nazewnictwa

1. Węzły PL po polsku (dla czytelności w UI), snake_case dla webhook path.
2. Kanały: `widget`, `whatsapp`, `email`, `sms`.
3. Reason codes eskalacji: `E01_identity_failed`, `E05_delivered_not_received`, itd. (patrz specyfikacja Część A.4).

## Sub workflow narzędzia (Tool Calling)

Każde narzędzie to osobny workflow z:

1. **Execute Workflow Trigger** przyjmuje input JSON matching JSON Schema.
2. **HTTP Request** wywołanie zewnętrznego API (Shopify, InPost).
3. **Retry logic** 3 próby z exponential backoff 1s, 2s, 4s.
4. **Timeout** 5s per próba.
5. **Response formatter** normalizacja do standardu wewnętrznego przed zwrotem do agenta.
6. **Error handler** przy 4xx/5xx zwracaj strukturalny error `{ error: 'code', retriable: bool }`.

## Praktyczne kroki działania

Kiedy użytkownik prosi o workflow:

1. Zapytaj o: kanał wejściowy (widget/whatsapp/email/inny), integracje (Shopify/BaseLinker/inne), przewoźnika (InPost/DPD/DHL/PL), specyficzne wymagania klienta.
2. Wygeneruj plik JSON w katalogu `n8n-workflows/` z inkrementowanym prefixem (`02_`, `03_`, ...).
3. Zapisz `meta.description` w JSON opisujący cel workflowu.
4. Zaproponuj test Bruno w `bruno-collection/n8n_webhooks/` dla nowego endpointu.
5. Zaktualizuj `n8n-workflows/README.md` żeby lista była kompletna.

## Referencje

1. Pełna specyfikacja: `docs/SPECYFIKACJA.md` (Część B.4 i C.1 to sercem tego skilla).
2. Wzorcowy workflow: `n8n-workflows/01_main_agent.json`.
3. System prompt agenta: `src/prompts/system_prompt.md`.
4. JSON Schemas narzędzi: sekcja C.2 specyfikacji.

## Anti patterns (nie rób tego)

1. Nie łącz Agent LLM bezpośrednio z Respond bez guardraili pośrednio.
2. Nie zapisuj sesji przed walidacją guardraili (nieudana odpowiedź nie powinna trafić do pamięci sesji jako reprezentatywna).
3. Nie loguj do Postgres pełnego user_message bez PII redaction dla kanałów gdzie klient wpisuje wolny tekst.
4. Nie pomijaj `timeout` na HTTP nodes, kurierzy potrafią wisieć.
