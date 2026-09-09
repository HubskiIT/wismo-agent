# Scenariusz nagrania na YouTube

Playbook do nagrania filmu z uruchomienia projektu WISMO Agent. Zaplanowany na dwa formaty do wyboru.

## Format A: Speedrun (15 do 20 minut)

Format flagshipowy. Jeden odcinek, pełny walkthrough od zera do działającego agenta. Trafia lepiej w organic reach.

### Struktura filmu

| Min | Segment | Co pokazujesz | Co mówisz (kluczowe punkty) |
|-----|---------|---------------|-------------------------------|
| 0:00 | Hook | Live tracking card z artifact, agent odpowiada w widget | "Sklepy tracą 3 500 EUR miesięcznie na pytaniach o paczki. Za 15 minut zbudujesz agenta który to obsłuży" |
| 0:30 | Kim jestem, dla kogo film | Twarz, może slide z ofertą | Krótki intro, target: właściciele sklepów, freelancerzy AI |
| 1:00 | Co dziś budujemy | Screen z artifact wizualnym (mission control) | Metryki, deflekcja, ROI |
| 2:00 | Terminal, klon repo | `git clone`, `cd wismo-agent`, `code .` w VS Code | Repo publiczne na moim GitHubie, link w opisie |
| 2:30 | Setup env | `make init`, pokazujesz `.env`, uzupełniasz Anthropic key i test Shopify | Klucz podstawiasz z zaślepionej wersji na kamerze |
| 3:30 | `make up` | Docker Compose leci, pokazujesz `make ps` | 5 usług, healthchecki, wszystko zielone |
| 4:30 | Panel n8n | `http://localhost:5678`, login, import workflowu | `make import` importuje `01_main_agent.json` |
| 6:00 | Credentials n8n | Anthropic, Postgres, Redis w UI | Pokazujesz jak podłączyć, bez pokazywania kluczy |
| 7:30 | Pierwszy test Bruno | `bru run --env local` na chat_webhook.bru | 200 OK, agent odpowiada |
| 8:30 | Demo z terminalem | `make demo` odpala skrypt z 3 scenariuszami | Happy path, brak weryfikacji, uszkodzenie |
| 10:30 | Guardrails w akcji | Zmieniasz prompt tak żeby agent obiecał zwrot, guardrails odrzuca | Pokazujesz walidację w wismo-api |
| 12:00 | Eskalacja do Slacka | Wysyłasz zapytanie E05 "doręczono ale nie mam paczki", pokazujesz brief w Slacku | "Tak wygląda HITL w praktyce" |
| 13:30 | Grafana dashboard | `http://localhost:3000`, deflection rate, latencja | Pokazujesz jak monitorujemy |
| 14:30 | Push na GitHub | `git push`, CI leci, badges się zapalają | Repo produkcyjne, forkuj i uruchamiaj |
| 15:30 | Podsumowanie i CTA | Twarz | "Chcesz taki w swoim sklepie, link w opisie. Zostaw łapkę, do zobaczenia" |

### Rekwizyty

1. Terminal z ładnym promptem (Starship, kolory pod motyw filmu).
2. VS Code z ciemnym motywem (Aura, Dracula, One Dark Pro).
3. Bruno UI zamiast tylko CLI (wygląda lepiej niż tekst).
4. Grafana wcześniej wypełniona sensownymi danymi (uruchom projekt dzień wcześniej żeby coś się nazbierało).
5. Slack z zaślepionym workspace do demo eskalacji.

### Miniatura filmu

Trzy elementy w kadrze:
1. Twarz w prawym rogu.
2. Duża liczba "35 do 50 procent" (styl z artifact).
3. Tekst "AI agent w 15 minut" w Fraunces italic.
4. Pod tekstem: "n8n · Claude · Docker".

## Format B: Devlog (5 odcinków po 8 do 12 minut)

Format serial. Każdy odcinek pokazuje jedną fazę. Lepsze do budowania subów.

1. **Odcinek 1: Setup i architektura**. Od zera do docker compose up i pierwszego webhooka.
2. **Odcinek 2: Agent i Tool Calling**. Prompt, narzędzia, integracja z Shopify.
3. **Odcinek 3: Guardrails i bezpieczeństwo**. FastAPI, PII, blacklist, testy pytest.
4. **Odcinek 4: HITL i eskalacje**. Brief JSON, Slack, 10 edge cases w akcji.
5. **Odcinek 5: Produkcja i observability**. Nginx, TLS, Grafana, deployment na Hetzner.

## Uwagi produkcyjne

1. Nagrywaj OBS w 1080p 60 fps, upload do YouTube w 1440p (algorytm wyżej ranking).
2. Terminal font `JetBrains Mono` 16 do 18 pt (żeby widoczny na mobile).
3. Zoomer w OBS na fragmenty terminala kiedy typujesz komendy.
4. B roll: krótkie ujęcia z artifact wizualnego kiedy tłumaczysz architekturę.
5. Muzyka: bez wokali, tempo 90 do 110 BPM, licencje z Epidemic Sound.
6. Napisy PL i EN. YouTube auto captions plus poprawki ręczne.
7. Tytuł: konkret plus liczba. "AI Agent CS w 15 minut. Redukcja tikietów o 50 procent." albo "Budujemy agenta AI dla e-commerce od zera. 14 dni w jednym filmie."

## Checklist na dzień nagrania

1. Repo na czystej gałęzi, ostatni commit działa.
2. `.env` przygotowany, klucze na osobnej karteczce.
3. Docker stopped przed startem (żeby pokazać `make up` od zera).
4. Slack workspace demo otwarty.
5. Grafana z danymi z dnia poprzedniego (przez cały dzień symuluj ruch).
6. Kamera, mikrofon, oświetlenie sprawdzone 30 minut wcześniej.
7. Woda, chusteczki, komórka na cichym.
