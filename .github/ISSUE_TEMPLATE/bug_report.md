---
name: Bug report
about: Zgłoś błąd w WISMO Agent
title: '[BUG] '
labels: bug
assignees: ''
---

## Opis błędu

Zwięzły opis co poszło nie tak.

## Kroki do odtworzenia

1. Uruchom `make up`
2. Wyślij POST na `/webhook/wismo/chat` z payloadem: `{...}`
3. Zobacz błąd w odpowiedzi/logach

## Oczekiwane zachowanie

Co powinno się stać.

## Rzeczywiste zachowanie

Co się dzieje.

## Środowisko

- OS: [np. Ubuntu 24.04, macOS 15]
- Docker: [wersja]
- Wersja WISMO Agent: [commit lub tag]
- Kanał: [widget/whatsapp/email]

## Logi

```
docker compose logs --tail=200 n8n wismo-api
```

## Dodatkowy kontekst

Screenshoty, propozycja rozwiązania, powiązane issues.
