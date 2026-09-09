# Security Policy

## Wspierane wersje

Bezpieczeństwo utrzymywane jest wyłącznie na najnowszej gałęzi `main` oraz najnowszym wydaniu z tagu SemVer.

| Wersja | Wsparcie |
| ------ | -------- |
| 0.1.x  | :white_check_mark: |
| < 0.1  | :x: |

## Zgłaszanie luk bezpieczeństwa

Znalazłeś podatność? Dzięki. Zgłoś ją odpowiedzialnie.

**Nie otwieraj publicznego issue** dla podatności. Zamiast tego:

1. Napisz e-mail na `grzybowski.it+security@gmail.com` z prefixem `[SECURITY] WISMO Agent`.
2. W treści opisz podatność, warunki reprodukcji, wpływ i propozycję fixu jeśli masz.
3. Otrzymasz potwierdzenie w ciągu 48 godzin.
4. Fix zostanie przygotowany w prywatnej gałęzi, wydany jako patch release.
5. Publiczny disclosure po wydaniu fixu, z uznaniem dla znalazcy jeśli sobie tego życzy.

## SLA reakcji

| Severity | Potwierdzenie | Fix wydany |
|----------|---------------|------------|
| Critical (RCE, auth bypass, PII leak) | 48h | 7 dni |
| High (privilege escalation, DoS) | 5 dni | 30 dni |
| Medium (XSS, CSRF) | 14 dni | 90 dni |
| Low | 30 dni | best effort |

## Zakres

W scope tego repo są:

1. Kod w `src/api/` (mikroserwis FastAPI).
2. Konfiguracja `docker/` (compose, Nginx, init db).
3. Workflowy n8n w `n8n-workflows/` (walidacja Function Node, brak injection).
4. Skille w `skills/`.

Poza scope (zgłaszaj do właściciela projektu):

1. Podatności w n8n samym w sobie (n8n.io).
2. Podatności w Anthropic Claude API.
3. Podatności w Docker, PostgreSQL, Redis, Nginx (upstream).

## Threat model (skrócony)

Główne wektory ataku które mieliśmy na uwadze:

1. **Prompt injection**. Klient próbuje zmanipulować agenta ("zignoruj poprzednie instrukcje..."). Mitygacja: guardrails po stronie serwera walidują output przed wysyłką, twarde separatory w promptcie, blacklist zwrotów. Zalecenie produkcyjne: dodać LLM Guard lub Rebuff jako klasyfikator wejścia.
2. **PII leak przez LLM**. Klient wysyła numer karty w wiadomości. Mitygacja: PII Redactor przed wywołaniem LLM (`redact_pii()`), guardrails walidują też output.
3. **Ujawnienie bazy klientów**. Agent po weryfikacji ujawnia że e-mail istnieje. Mitygacja: `verify_identity` nigdy nie zwraca zawartości bazy, tylko `verified: bool` plus `reason_code`.
4. **Halucynacje numerów zamówień**. Agent zmyśla ID. Mitygacja: `validate_response` weryfikuje że każdy numer w odpowiedzi był w outputach narzędzi.
5. **Nieautoryzowany dostęp do panelu n8n**. Mitygacja: Basic Auth plus rate limit plus zalecenie VPN/IP allowlist w produkcji.
6. **Webhook spoofing**. Ktoś podszywa się pod Twilio/Shopify. Mitygacja: TODO, dodać weryfikację HMAC dla Shopify i X-Twilio-Signature.
7. **Wyczerpanie budżetu LLM**. Bot spamuje agenta. Mitygacja: rate limit per IP w Nginx, TODO per session w Redis, TODO twarde limity kosztowe per klient.

Pełny threat model: `docs/SECURITY_THREAT_MODEL.md` (todo).

## Practices

1. Wszystkie sekrety w `.env`, nigdy w kodzie ani w commitach.
2. `gitleaks` w CI blokuje commit z detected secretami.
3. Dependabot włączony na `.github/dependabot.yml`.
4. Trivy skanuje obrazy Docker w CI.
5. `bandit` skanuje Python pod SAST.
6. Non root user w kontenerach.
7. Rate limiting per IP i per session (planowane).
8. Immutable audit log (planowane, S3 Object Lock).

## Contact

E-mail: `grzybowski.it+security@gmail.com`
Author: Hubert Grzybowski
Response time: 48h potwierdzenie, patch zależny od severity.
