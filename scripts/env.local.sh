# Source this (don't execute) in a backend shell to run natively against the
# Dockerized Postgres/Redis published on localhost:
#   source scripts/env.local.sh
# Shell exports take precedence over backend/.env, so Docker mode keeps working.
# Host ports are 5433/6380 (see docker-compose.yml) to avoid colliding with
# other local Postgres/Redis instances. Containers still use 5432/6379 internally.
export DATABASE_URL="postgres://postgres:postgres@localhost:5433/resume_analyzer"
export REDIS_URL="redis://localhost:6380/0"
export CELERY_BROKER_URL="$REDIS_URL"
export CELERY_RESULT_BACKEND="$REDIS_URL"
export S3_ENDPOINT_URL="http://localhost:9000"
echo "Local env exported: DATABASE_URL->localhost:5433, REDIS_URL->localhost:6380"
