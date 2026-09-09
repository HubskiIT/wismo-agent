# 004. Redis (nie PostgreSQL) dla pamięci sesji

Data: 2026-09-09
Status: accepted
Deciders: Hubert Grzybowski

## Kontekst

Agent musi pamiętać kontekst rozmowy między turami (historia wiadomości, stan weryfikacji tożsamości, kontekst zamówienia). Postgres już mamy dla audit log. Dorzucanie Redis to koszt operacyjny (drugi kontener, drugi backup).

## Rozważane opcje

1. **Postgres jako storage sesji** (tabela `sessions` z JSONB payload).
2. **Redis z TTL**.
3. **In memory dict w wismo-api**.
4. **SQLite plikowe**.

## Decyzja

**Redis 7 z TTL 24 godziny**.

## Rationale

1. **Latencja**. Redis P99 pod milisekundę dla GET/SET. Postgres z indexem to 5 do 15 ms. Multiplikuje się bo load session jest w każdym turze rozmowy.
2. **TTL out of the box**. Redis expire po 24h automatycznie. W Postgresie potrzebowałbym crona.
3. **Memory pressure**. LRU eviction w Redis kiedy przekroczymy limit (`maxmemory 512mb`). Postgres wymagałby manual cleanup.
4. **Queue broker**. Redis obsługuje też BullMQ dla n8n queue mode (`EXECUTIONS_MODE=queue`). Dwa w jednym.
5. **Volatile with design**. Session w Redis jest wolatylna świadomie. Utrata (restart, wyczyszczenie) oznacza że klient zaczyna nową rozmowę. To akceptowalne, bo kontekst zamówienia da się odbudować z audit log Postgres.

Odrzucone opcje:

1. **In memory dict**: nie przetrwa restartu, nie da się skalować horyzontalnie n8n.
2. **SQLite plikowe**: gorzej skaluje niż Postgres, brak natywnego TTL.
3. **Postgres**: użylibyśmy do sesji, ale latencja i overhead nie warte oszczędności jednego kontenera.

## Konsekwencje

### Pozytywne

1. Sub-millisekundowa latencja load session.
2. Session expiruje sama. Zero maintenance.
3. Redis też jako broker dla n8n queue.

### Negatywne

1. Extra kontener w compose (koszt operacyjny: monitoring, backup, restart).
2. Session traci się przy restarcie Redis. Klient może odczuwać "amnezję" agenta jeżeli restart w środku rozmowy.
3. Redis jako single point of failure jeżeli nie ma HA. Mitygacja: dla pierwszych klientów akceptowalne, dla enterprise dodać Redis Sentinel lub Cluster.

### Neutralne

1. Można łatwo migrować dane sesji do Postgres jeżeli zmienimy zdanie (session_id jako klucz plus JSONB payload).
