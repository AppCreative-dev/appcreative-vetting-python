#!/usr/bin/env bash
# Starts everything for the exercise. Safe to run again at any time.
cd "$(dirname "$0")" || exit 1
mkdir -p logs telemetry-output

export HOST_UID HOST_GID
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"
if [ -n "$CODESPACE_NAME" ]; then
  export GRAFANA_ROOT_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/"
fi

echo "Starting Grafana and the telemetry collector (the first time can take a few minutes)..."
if ! docker compose up -d; then
  echo "❌ Couldn't start Grafana. Wait a minute and run 'bash start.sh' again."
  exit 1
fi

bash stop.sh --app-only >/dev/null 2>&1

start_service() {
  local name=$1 port=$2 dir=$3 module=$4
  nohup python -m uvicorn "$module:app" --app-dir "$dir" --port "$port" \
    --reload --reload-dir "$dir" >"logs/$name.log" 2>&1 &
  echo $! >"logs/$name.pid"
}

echo "Starting the practice app..."
start_service fake-llm 8003 services/fake_llm fake_llm_app
start_service recommendations 8002 services/recommendations recommendations_app
start_service orders 8001 services/orders orders_app

all_ok=true
for entry in "orders:8001" "recommendations:8002" "fake-llm:8003" "Grafana:3000"; do
  name=${entry%%:*}
  port=${entry##*:}
  path="/health"
  [ "$name" = "Grafana" ] && path="/api/health"
  ok=false
  for _ in $(seq 1 60); do
    if curl -sf "http://localhost:$port$path" >/dev/null 2>&1; then ok=true; break; fi
    sleep 1
  done
  if $ok; then
    echo "✅ $name is running"
  else
    echo "❌ $name didn't start. Look in logs/$name.log for the reason."
    all_ok=false
  fi
done

echo
if $all_ok; then
  echo "Everything is running. Open the PORTS tab and click the globe next to 'Grafana' to see traces."
  echo "Code changes reload automatically; you don't need to restart."
else
  echo "Something didn't start. Try 'bash start.sh' once more."
fi
