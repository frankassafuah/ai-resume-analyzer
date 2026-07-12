#!/usr/bin/env bash
# Lint backend (ruff) and frontend (eslint).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "→ Backend: ruff"
docker compose exec api ruff check .

echo "→ Frontend: eslint"
docker compose exec web npm run lint
