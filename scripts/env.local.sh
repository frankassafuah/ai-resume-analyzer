# Source this (don't execute) in a backend shell to run natively against the
# Dockerized Postgres/Redis published on localhost:
#   source scripts/env.local.sh
# Shell exports take precedence over backend/.env, so Docker mode keeps working.
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/resume_analyzer"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="$REDIS_URL"
export CELERY_RESULT_BACKEND="$REDIS_URL"
export S3_ENDPOINT_URL="http://localhost:9000"
echo "Local env exported: DATABASE_URL/REDIS_URL -> localhost"
