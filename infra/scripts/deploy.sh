#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -f ".env" ]]; then
  echo "Missing .env in project root. Copy infra/env/server.env.example first."
  exit 1
fi

CURRENT_UID="$(id -u)"
if grep -q '^AIRFLOW_UID=' .env; then
  sed -i "s/^AIRFLOW_UID=.*/AIRFLOW_UID=${CURRENT_UID}/" .env
else
  printf '\nAIRFLOW_UID=%s\n' "${CURRENT_UID}" >> .env
fi
echo "[deploy] AIRFLOW_UID set to ${CURRENT_UID}"

echo "[deploy] pulling latest base images"
docker compose -f infra/docker-compose.server.yml --env-file .env pull || true

echo "[deploy] building project images"
docker compose -f infra/docker-compose.server.yml --env-file .env build

echo "[deploy] running stack"
docker compose -f infra/docker-compose.server.yml --env-file .env up -d

echo "[deploy] done"
echo "Airflow UI: http://<server-ip>:8080"
