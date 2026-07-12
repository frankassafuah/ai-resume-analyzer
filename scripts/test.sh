#!/usr/bin/env bash
# Run the backend test suite inside the api container.
set -euo pipefail
cd "$(dirname "$0")/.."
exec docker compose exec api pytest -q "$@"
