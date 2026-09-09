# Kolekcja Bruno

Testy API do WISMO Agent. Trzy grupy:

1. `n8n_webhooks/` testy dymne endpointów agenta w n8n.
2. `Shopify/` walidacja połączenia z Shopify Admin API.
3. `InPost/` walidacja połączenia z ShipX API.

## Uruchomienie

```bash
# CLI (zalecane w CI)
npm install -g @usebruno/cli
bru run --env local

# UI (rozwój, wygodne debugowanie)
# Otwórz Bruno app > Open Collection > wskaż ten katalog
```

## Sekrety

Sekrety (`SHOPIFY_ADMIN_TOKEN`, `INPOST_API_TOKEN`, `ANTHROPIC_API_KEY`) trzymaj w Bruno secret store, nigdy w `local.bru`. Bruno w UI ma osobny panel Secrets, w CLI wczytuje z env variables.
