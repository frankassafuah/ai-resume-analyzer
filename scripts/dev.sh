#!/usr/bin/env bash
# Start the full stack in the foreground with live logs.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f backend/.env ] || cp backend/.env.example backend/.env
exec docker compose up --build
