# Deployment produkcyjny

Trzy zalecane ścieżki wdrożenia. Wybór zależy od budżetu klienta i poziomu odpowiedzialności za utrzymanie.

## Ścieżka 1. Hetzner VPS plus Docker (rekomendowana dla większości)

Najlepszy stosunek cena/wydajność w EU. Zgodność z RODO out of the box (data center Falkenstein/Nürnberg).

### Specyfikacja

1. CX21 (2 vCPU, 4 GB RAM, 40 GB SSD): około 5,83 EUR miesięcznie. Wystarcza do 2 000 sesji dziennie.
2. CX31 (2 vCPU, 8 GB RAM, 80 GB SSD): około 10,52 EUR miesięcznie. Do 10 000 sesji dziennie.
3. CPX41 (8 vCPU, 16 GB RAM, 240 GB SSD): około 33,64 EUR miesięcznie. Skalowanie ponad 50 000 sesji dziennie.

### Instalacja

```bash
# Na świeżym Ubuntu 24.04 LTS
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg git ufw

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Klon repo
git clone https://github.com/grzybowski-it/wismo-agent.git
cd wismo-agent
make init
# Uzupełnij docker/.env swoimi kluczami
make up
```

### TLS z Let's Encrypt

Dodaj Caddy jako reverse proxy zamiast Nginx dla auto TLS:

```yaml
# docker-compose.override.yml
services:
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - n8n
      - wismo-api

volumes:
  caddy_data:
  caddy_config:
```

`docker/Caddyfile`:

```
agent.mojsklep.pl {
    reverse_proxy /webhook/* n8n:5678
    reverse_proxy /n8n/* n8n:5678
    reverse_proxy /api/* wismo-api:8000
    encode zstd gzip
    log {
        output file /data/access.log
    }
}
```

## Ścieżka 2. Coolify (self hosted PaaS)

Coolify to open source alternative dla Heroku, hostowana na twoim VPS. Zarządza Dockerem, TLS, backup, monitoring z UI.

1. Instalacja Coolify na Hetzner CX21: `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash`
2. UI na `https://vps.mojadomena.pl:8000`
3. Nowy projekt → Docker Compose → wskaż repo GitHub → deploy.
4. Auto TLS, auto backup, health checki, restart on failure.

Koszt: darmowy plus koszt VPS. Idealne dla freelancera obsługującego 5 do 20 klientów z osobnymi instancjami.

## Ścieżka 3. Railway (managed)

Bez DevOpsa, dla start-shipping-tomorrow.

1. railway.app → New Project → Deploy from GitHub → wskaż `wismo-agent`.
2. Postgres i Redis dodaj przez marketplace Railway (jeden klik).
3. Environment variables w Settings.
4. Custom domain w Networking.

Koszt: około 20 do 40 USD miesięcznie za usługę tej wielkości. Świetne na start, do refactoru na Ścieżkę 1 gdy ruch urośnie.

## Backup i disaster recovery

### Postgres backup do S3

```bash
# Codzienny cron backup, retention 30 dni
docker compose exec postgres pg_dump -U n8n -Fc n8n \
  | age -r "$AGE_PUBLIC_KEY" \
  | aws s3 cp - s3://wismo-backups/postgres/$(date +%F).sql.gz.age
```

### Test restore raz w miesiącu

```bash
aws s3 cp s3://wismo-backups/postgres/2026-09-01.sql.gz.age - \
  | age -d -i ~/.age/key.txt \
  | docker compose exec -T postgres pg_restore -U n8n -d n8n_test
```

## Monitoring

Grafana z Loki jest w docker compose. Kluczowe dashboardy do zbudowania w pierwszym tygodniu produkcji:

1. Deflection rate per dzień per kanał (widok `v_metrics_daily` z Postgres).
2. Latencja P50, P95, P99 per endpoint.
3. Koszt LLM per dzień per klient (tokens_in, tokens_out, cost_usd z `agent_conversations`).
4. Kolejka eskalacji (nierozwiązanych escalations z `escalations`).
5. Health checks (Uptime Kuma jako osobny kontener albo zewnętrzny UptimeRobot).

## Skalowanie

Kiedy potrzebujesz więcej wydajności:

1. **Poziomo n8n**. `EXECUTIONS_MODE=queue` (już włączone) plus 2 do 4 workerów n8n. Redis jako broker BullMQ.
2. **Postgres**. Do 100 000 sesji dziennie starczy jeden Postgres. Powyżej: read replica, connection pooling przez pgbouncer.
3. **LLM**. Anthropic ma tier limits. Powyżej 20 rps rozważ własne queue plus rate limiter, albo Bedrock/Vertex dla higher tier.
4. **CDN dla widgetu**. Statyczny plik JS widgetu z Cloudflare, żeby nie obciążać n8n.

## RODO / GDPR checklist

1. Umowa powierzenia danych z klientem końcowym (sklepem).
2. Podumowa z Anthropic (i OpenAI jako fallback). Zapisz w rejestrze przetwarzania.
3. Klauzula informacyjna w widget/e-mail: "Rozmawiasz z asystentem AI. Twoje dane są przetwarzane w celu obsługi zamówienia."
4. Endpoint `/gdpr/forget` który przy zapytaniu klienta usuwa jego dane z: Postgres `agent_conversations`, Redis wszystkie sesje z jego numerem, logi Loki (grep + shred), backup Postgres (kolejny snapshot bez tych danych po 24h).
5. Retention policy: usuwaj `agent_conversations` starsze niż 90 dni (cron n8n).
6. DPO wyznaczony w firmie klienta końcowego, twoje dane kontaktowe w regulaminie.
