# 002. Claude Sonnet jako główny LLM, GPT-4o mini jako fallback

Data: 2026-09-09
Status: accepted
Deciders: Hubert Grzybowski

## Kontekst

Agent odpowiada klientowi w rozmowach dot. statusu paczek. Wymagania:

1. Naturalna polszczyzna z diakrytykami.
2. Bardzo dobre Tool Use (5 narzędzi, wywołania równoległe kiedy potrzeba).
3. Odporność na prompt injection ("zignoruj poprzednie instrukcje...").
4. Koszt per sesja poniżej 0,05 USD (celujemy w 30 procent marży przy koszcie 0,15 USD dla klienta).
5. Latencja P95 poniżej 3 sekund.

## Rozważane opcje

1. **Claude Sonnet** (Anthropic).
2. **GPT-4o** (OpenAI).
3. **GPT-4o mini** (OpenAI).
4. **Gemini Pro** (Google).
5. **Llama 3 self hostowana**.

## Decyzja

**Primary: Claude Sonnet**. **Fallback: GPT-4o mini**.

### Dlaczego Sonnet

1. Najlepsze Tool Use w benchmarkach 2025/2026 (Berkeley Function Calling Leaderboard).
2. Naturalna polszczyzna, tożsama z GPT-4 klasą, plus lepsze zachowanie polskich odmian gramatycznych.
3. Constitutional AI (Anthropic) daje lepsze zachowanie przy prompt injection w naszych testach wewnętrznych.
4. Sensowna cena Tier 2 (Sonnet, nie Opus).
5. Latencja stabilna, P95 około 2 do 4 sekund na naszym workloadzie.

### Dlaczego fallback

Anthropic ma outages (kilka razy w kwartale, każdy 10 do 60 minut). Bez fallbacku agent leży. Automatyczne przełączenie na GPT-4o mini utrzymuje 99+ procent uptime.

Fallback jest **downgrade'em**: mini ma słabsze Tool Use i bardziej zachowawcze odpowiedzi. Dlatego jest fallback, nie primary.

### Dlaczego nie inne

1. **GPT-4o full**. Świetne w konwersacji, ale droższe niż Sonnet plus słabsze w Tool Use w naszych testach.
2. **GPT-4o mini**. Za słabe w Tool Use dla naszej sekwencji 5 narzędzi. OK jako fallback, nie primary.
3. **Gemini Pro**. Dobry cenowo, słabszy w polskim, ekosystem tools mniej dojrzały.
4. **Llama 3 self hosted**. Największy koszt utrzymania (GPU host), latencja gorsza, quality poniżej progu.

## Konsekwencje

### Pozytywne

1. Klient dostaje najwyższą jakość odpowiedzi na rynku, z resilience przy outage.
2. Marża przy 0,05 USD kosztu i 0,15 USD ceny to około 66 procent (przed kosztami infrastruktury).

### Negatywne

1. Zależność od dwóch dostawców zamiast jednego. Więcej integracji, więcej monitoringu.
2. Prompt musi być kompatybilny z oboma modelami (lekki wspólny mianownik). Mitygacja: kanoniczny system prompt bez model specific tricks.
3. Koszty rosną liniowo z użyciem. Twardy cost cap per klient obowiązkowy (patrz ADR 005).

### Neutralne

1. W 2026/2027 prawdopodobnie pojawią się nowsze modele. Konfiguracja przez `LLM_MODEL` env variable pozwala na migrację bez zmiany kodu.
