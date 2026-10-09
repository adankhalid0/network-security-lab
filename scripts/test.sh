#!/usr/bin/env bash
# Checks that the zones are segmented the way the firewall rules say.
# Run from the repository root after "docker compose up --build -d":
#   bash scripts/test.sh
set -u
cd "$(dirname "$0")/.."

PASS=0
FAIL=0

dx() { docker compose exec -T "$@"; }

# retry <seconds> <command...>: run until it succeeds or time runs out
retry() {
  local timeout="$1"; shift
  local waited=0
  until "$@" >/dev/null 2>&1; do
    sleep 2
    waited=$((waited + 2))
    if [ "$waited" -ge "$timeout" ]; then return 1; fi
  done
}

# check <name> <command...>: command must succeed
check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "PASS  $name"; PASS=$((PASS + 1))
  else
    echo "FAIL  $name"; FAIL=$((FAIL + 1))
  fi
}

# check_blocked <name> <command...>: command must fail (traffic is blocked)
check_blocked() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "FAIL  $name"; FAIL=$((FAIL + 1))
  else
    echo "PASS  $name"; PASS=$((PASS + 1))
  fi
}

ping_from() { dx "$1" ping -c 1 -W 1 "$2"; }
port_from() { dx "$1" nc -z -w 2 "$2" "$3"; }

echo "Waiting for the firewall and the routes to be ready (up to 60 s)..."
retry 60 ping_from monitor 172.20.10.20 || echo "(monitor cannot reach corp-server yet, checks below will show why)"

echo
echo "== Management zone is allowed into the other zones =="
check "management -> corp (ping)"  ping_from monitor 172.20.10.20
check "management -> guest (ping)" ping_from monitor 172.20.20.10
check "management -> corp port 80 (port scanner)" \
  bash -c "docker compose exec -T monitor python port_scanner.py 172.20.10.20 --ports 80 --timeout 1 | grep -q 'OPEN ports: \[80\]'"

echo
echo "== Guest zone is isolated =="
check_blocked "guest -> corp (ping) is blocked"       ping_from guest-host 172.20.10.20
check_blocked "guest -> corp port 22 is blocked"      port_from guest-host 172.20.10.20 22
check_blocked "guest -> management (ping) is blocked" ping_from guest-host 172.20.99.10

echo
echo "== Corp and guest are separated =="
check_blocked "corp -> guest (ping) is blocked" ping_from corp-host 172.20.20.10
check "corp-host -> corp-server port 80 (same zone)" port_from corp-host 172.20.10.20 80

echo
echo "== Monitoring tools =="
check "port scanner finds ports 22 and 80 on corp-host" \
  bash -c "docker compose exec -T monitor python port_scanner.py 172.20.10.10 --timeout 1 | grep -q 'OPEN ports: \[22, 80\]'"

echo
echo "== Firewall counters (blocked packets were counted) =="
check "DENY guest->corp counter is above 0" \
  bash -c "docker compose exec -T firewall nft list ruleset | grep 'DENY guest->corp' | grep -qE 'packets [1-9]'"
check "DENY corp->guest counter is above 0" \
  bash -c "docker compose exec -T firewall nft list ruleset | grep 'DENY corp->guest' | grep -qE 'packets [1-9]'"

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
