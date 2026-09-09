#!/usr/bin/env bash
# =============================================================================
# WISMO Agent. Skrypt demo do nagrania filmu.
# Wysyła 3 przykładowe zapytania do agenta i pokazuje odpowiedzi.
# Uruchom: make demo (lub bezpośrednio ./scripts/demo.sh).
# =============================================================================

set -euo pipefail

N8N_URL="${N8N_URL:-http://localhost:5678}"
ENDPOINT="$N8N_URL/webhook/wismo/chat"

BOLD='\033[1m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; RESET='\033[0m'

send() {
  local scenario=$1
  local session=$2
  local message=$3

  echo ""
  echo -e "${CYAN}▸ SCENARIUSZ:${RESET} $scenario"
  echo -e "${BOLD}Klient:${RESET} $message"
  echo -e "${BOLD}Agent :${RESET}"

  curl -sS -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$(printf '{"channel":"widget","session_id":"%s","message":"%s"}' "$session" "$message")" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('  '+d.get('reply','(brak odpowiedzi)'))"

  echo ""
  sleep 1.5
}

echo -e "${BOLD}=== WISMO Agent Demo ===${RESET}"
echo "Endpoint: $ENDPOINT"

send "Happy path" "demo_001" "Gdzie jest moja paczka? Zamowienie 12345, a.kowalska@example.com"
send "Brak weryfikacji" "demo_002" "Kiedy dostanę zamówienie?"
send "Uszkodzenie paczki" "demo_003" "Odebrałam paczkę i jest uszkodzona. Co robić? Zamowienie 12345, a.kowalska@example.com"

echo -e "${GREEN}✓ Demo zakończone.${RESET}"
