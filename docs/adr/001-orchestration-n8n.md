# 001. Wybór n8n jako orkiestratora workflowów

Data: 2026-09-09
Status: accepted
Deciders: Hubert Grzybowski

## Kontekst

Rdzeń projektu to agent LLM obsługujący 3 kanały (widget, WhatsApp, e-mail), wywołujący 5 narzędzi (Shopify, kurierzy, Slack, SMTP, weryfikacja) plus proaktywny cron. Musimy wybrać warstwę orkiestracji która pozwoli klientowi końcowemu (sklepowi) na późniejszą modyfikację workflowu bez potrzeby zatrudniania inżyniera.

Klient docelowy: małe i średnie sklepy w Polsce, zwykle z zespołem 2 do 10 osób, bez własnego DevOpsa. Wymagania: audyt executions, retry, wizualizacja przepływu, możliwość włączenia/wyłączenia poszczególnych workflowów bez deploymentu.

## Rozważane opcje

1. **n8n**. Wizualny workflow builder, open source (Sustainable Use License), self hostowalny, ekosystem 400+ integracji, JSON export do wersjonowania w git, LangChain nodes dla LLM.
   - Plus: klient końcowy widzi i rozumie workflow. History executions w UI. Ekosystem integracji dojrzały.
   - Minus: Function Node w JS jest ograniczony, testy są trudniejsze niż w Pythonie. Community edition ma limity concurrent executions.
2. **LangChain plus FastAPI**. Cały workflow w Pythonie, agent jako klasa, tools jako funkcje.
   - Plus: pełna kontrola, testowalność, typing.
   - Minus: klient nie widzi tego wizualnie. Każda zmiana wymaga deploya. Nie ma out of the box UI dla history.
3. **CrewAI albo LangGraph**. Framework agentowy multi agent.
   - Plus: pattern multi agent gotowy.
   - Minus: overkill dla single agent CS. Klient nie ma jak zajrzeć. Ekosystem młodszy.
4. **Zapier albo Make**. SaaS platformy no code.
   - Plus: klient zna z reklam.
   - Minus: koszty per execution rosną szybko (500 zapytań dziennie w Zapierze to 20 000 execution miesięcznie plus). Dane klientów w cudzej chmurze. Lock in.

## Decyzja

Wybieramy **n8n**. Krytyczne czynniki:

1. **Ownership**. Self hostowanie u klienta lub u nas. Zero lock in.
2. **Auditability**. Klient końcowy widzi każdą execution, każdy input, każdy output. Kluczowe dla RODO i customer trust.
3. **Modyfikowalność**. Klient może sam zmienić prompt lub dodać krok, bez naszej ingerencji. Obniża koszty utrzymania.
4. **Wersjonowanie**. Workflow to JSON, żyje w git jak każdy inny kod.
5. **Ekosystem**. Ready made integracje ze Slackiem, Shopify, IMAP, Postgres, Redis. Nie trzeba ich pisać.

## Konsekwencje

### Pozytywne

1. Klient może obserwować pracę agenta w n8n UI (dowód działania dla stakeholderów).
2. Onboarding nowego dewelopera do projektu jest szybszy (workflow jest wizualny).
3. Można łatwo dodawać kanały (Instagram, Messenger, SMS) reużywając infrastrukturę.

### Negatywne

1. Function Nodes w JavaScript są mniej testowalne niż moduł Pythona. Mitygacja: cała logika krytyczna (guardrails, PII, walidacje) siedzi w wismo-api (FastAPI), nie w Function Node.
2. n8n Community Edition ma limity concurrent executions. Mitygacja: BullMQ queue mode plus workery (już w compose).
3. Migracja na inny orkiestrator w przyszłości będzie kosztowna. Mitygacja: wszystkie tools są sub workflowami z well defined JSON Schema, można je łatwo przenieść.

### Neutralne

1. Licencja Sustainable Use License wymaga zapoznania się. Dla self hostingu klienta końcowego bez odsprzedaży jako SaaS jest OK.
