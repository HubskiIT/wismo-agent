# GitHub setup

Krok po kroku od lokalnego repo do publicznego z zielonym CI. Wszystko z terminala plus kilka klików w UI GitHuba.

## 1. Utworzenie repo na GitHubie

Dwie opcje. Wybierz jedną.

### Opcja A: przez GitHub CLI (polecane)

```bash
# Sprawdź czy masz gh
gh --version || brew install gh   # macOS

# Zaloguj się
gh auth login

# Utwórz repo z lokalnego katalogu
cd wismo-agent-starter
gh repo create wismo-agent \
  --public \
  --source=. \
  --description "AI Customer Service Automation for E-commerce. WISMO deflection 35 to 50 percent." \
  --homepage "https://github.com/grzybowski-it/wismo-agent" \
  --add-readme=false
```

### Opcja B: przez UI

1. github.com → New repository
2. Name: `wismo-agent`
3. Description: `AI Customer Service Automation for E-commerce. WISMO deflection 35 to 50 percent.`
4. Public
5. Bez README, bez .gitignore, bez license (mamy swoje)
6. Create repository

Potem lokalnie:

```bash
cd wismo-agent-starter
git init
git remote add origin git@github.com:grzybowski-it/wismo-agent.git
```

## 2. Pierwszy commit i push

```bash
# Sprawdz co idzie do commita, upewnij sie ze nie ma sekretow
git status
git diff --cached  # jesli cos juz zestagowane

# Zastaguj wszystko
git add .

# Sprawdz jeszcze raz przed commitem, szczegolnie:
# - czy nie ma docker/.env
# - czy .env.example ma tylko placeholdery
# - czy nie ma .n8n/ ani grafana_data/
git status

# Pierwszy commit
git commit -m "feat: initial WISMO Agent scaffold

- 8 workflowow n8n (main agent, sub workflowy narzedzi, eskalacje, kanaly)
- Docker compose stack (n8n, postgres, redis, wismo-api, nginx, grafana, loki)
- Mikroserwis FastAPI z guardrailami i PII redaction
- 27 testow pytest zielonych
- Bruno collection dla Shopify, InPost, n8n webhooks
- Skill wismo-workflow-builder dla Claude Code
- Dokumentacja: SPECYFIKACJA, RECORDING (scenariusz YouTube), GITHUB_SETUP"

# Utworz galaz main (domyslna w nowym GitHubie)
git branch -M main

# Push
git push -u origin main
```

## 3. Ustawienia repo (branch protection, secrets)

### Branch protection

```bash
gh api repos/grzybowski-it/wismo-agent/branches/main/protection \
  --method PUT \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["FastAPI tests", "Docker build (smoke)", "Secrets scan"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

Albo przez UI: Settings → Branches → Add rule → Branch name pattern `main` → zaznacz Require status checks, Require pull request reviews.

### GitHub Secrets (dla CI)

Sekrety których CI potrzebuje. Ustaw przez CLI:

```bash
gh secret set ANTHROPIC_API_KEY --repo grzybowski-it/wismo-agent
gh secret set SHOPIFY_ADMIN_TOKEN --repo grzybowski-it/wismo-agent
gh secret set INPOST_API_TOKEN --repo grzybowski-it/wismo-agent
```

Albo w UI: Settings → Secrets and variables → Actions → New repository secret.

Uwaga: podstawowe CI z tego repo nie potrzebuje tych kluczy (pytest testuje tylko guardrails offline, docker build to smoke). Klucze będą potrzebne dopiero gdy dodasz testy integracyjne z realnymi API.

### Discussions i Issues templates

```bash
# Wlacz Discussions
gh api repos/grzybowski-it/wismo-agent \
  --method PATCH \
  --field has_discussions=true

# Issue templates masz juz w .github/ISSUE_TEMPLATE/
```

## 4. README badges (aktualizacja linków)

W `README.md` badges CI wskazują na twój login. Podmień `grzybowski-it` na własny github username jeśli inny, oraz aktywuj GitHub Actions badge automatycznie po pierwszym uruchomieniu CI:

```markdown
[![CI](https://github.com/grzybowski-it/wismo-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/grzybowski-it/wismo-agent/actions/workflows/ci.yml)
```

Wklej ten badge do sekcji nagłówka README.md.

## 5. Publikacja repo (topics, homepage, social preview)

```bash
# Topics (do wyszukiwania na GitHubie)
gh api repos/grzybowski-it/wismo-agent/topics \
  --method PUT \
  --input - <<EOF
{
  "names": ["ai", "customer-service", "ecommerce", "n8n", "docker", "shopify", "inpost", "claude", "polish-startup", "automation", "wismo"]
}
EOF
```

Social preview (obrazek 1280x640 pokazywany kiedy linkujesz repo na LinkedIn/Twitter):

1. Wygeneruj z artifact wizualnego który mamy (screenshot hero section).
2. Settings → General → Social preview → Upload image.

## 6. GitHub Pages dla dokumentacji (opcjonalne)

Możesz zbudować statyczną dokumentację z `docs/`:

```bash
# W repo utworz galaz gh-pages
git checkout --orphan gh-pages
git rm -rf .
cp ../docs/* .
git add .
git commit -m "docs: initial GitHub Pages"
git push origin gh-pages

# W UI: Settings → Pages → Source: Deploy from branch → gh-pages
```

Twoja dokumentacja będzie na `https://grzybowski-it.github.io/wismo-agent/`.

## 7. Release i tagi

Po każdej stabilnej wersji:

```bash
# Utworz tag
git tag -a v0.1.0 -m "v0.1.0 - Initial scaffold with 8 workflows"
git push origin v0.1.0

# Wygeneruj release notes
gh release create v0.1.0 \
  --title "WISMO Agent v0.1.0" \
  --notes "First public release. 8 n8n workflows, guardrails, HITL, 27 tests passing."
```

## 8. Ostatnia checklista przed push

1. `docker/.env` w `.gitignore`? tak
2. Klucze API nigdzie hardcoded? sprawdź `git diff --cached | grep -iE "sk-|shpat|whsec|api[_-]?key"`
3. `LICENSE` obecne? tak
4. `README.md` z badges i sekcjami PL/EN? tak
5. `.github/workflows/ci.yml` obecne? tak
6. Gitleaks pre commit hook zainstalowany?

```bash
# Instalacja gitleaks pre commit hook (raz per repo)
brew install gitleaks
gitleaks protect --staged  # test przed pierwszym pushem
```

## Po pierwszym push, co powiesz w opisie repo

Krótko, ekstrakt z README:

> Autonomiczny agent AI CS dla e-commerce. Automatyzuje 35 do 50 procent zapytań "gdzie jest moja paczka" (WISMO). Integruje Shopify i BaseLinker z InPost, DPD, DHL, Pocztą Polską. Wdrożenie 14 dni. Stack: n8n plus Claude Sonnet plus Docker plus FastAPI. Produkcyjne guardrails, HITL, RODO ready. MIT.

## Twoim następnym krokiem

Po zielonych badges w README, nagraj film wg `docs/RECORDING.md`. Repo publiczne to twój portfolio piece dla klientów TIER 1.
