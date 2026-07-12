#!/usr/bin/env bash
# First-time local setup: env file, build, start, migrate, create storage bucket.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f backend/.env ]; then
  echo "→ Creating backend/.env from example"
  cp backend/.env.example backend/.env
else
  echo "→ backend/.env already exists, leaving it untouched"
fi

echo "→ Building images"
docker compose build

echo "→ Starting infrastructure (db, redis, minio)"
docker compose up -d db redis minio

echo "→ Starting api (runs migrations on boot) and worker"
docker compose up -d api worker

echo "→ Creating the MinIO bucket"
./scripts/create-bucket.sh || echo "  (bucket step skipped/failed — not fatal for M0)"

echo "→ Starting web"
docker compose up -d web

echo
echo "✅ Bootstrap complete."
echo "   API health : http://localhost:8000/health/"
echo "   API docs   : http://localhost:8000/api/docs/"
echo "   Web app    : http://localhost:3000"
echo "   MinIO UI   : http://localhost:9001 (minioadmin/minioadmin)"
echo
echo "   Verify Celery:  make ping   (expect: pong)"
