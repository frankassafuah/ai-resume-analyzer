#!/usr/bin/env bash
set -euo pipefail

# Wait for Postgres and Redis before starting.
wait_for() {
  local host="$1" port="$2" name="$3"
  echo "Waiting for ${name} at ${host}:${port}..."
  until nc -z "$host" "$port"; do sleep 1; done
  echo "${name} is up."
}

DB_HOST="${DB_HOST:-db}"; DB_PORT="${DB_PORT:-5432}"
REDIS_HOST="${REDIS_HOST:-redis}"; REDIS_PORT="${REDIS_PORT:-6379}"

case "${1:-api}" in
  api)
    wait_for "$DB_HOST" "$DB_PORT" "Postgres"
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput || true
    if [ "${DJANGO_DEBUG:-true}" = "true" ]; then
      exec python manage.py runserver 0.0.0.0:8000
    else
      exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}"
    fi
    ;;
  worker)
    wait_for "$DB_HOST" "$DB_PORT" "Postgres"
    wait_for "$REDIS_HOST" "$REDIS_PORT" "Redis"
    exec celery -A config worker -l "${LOG_LEVEL:-info}" -E \
      -Q default,parsing,analysis,generation,notifications
    ;;
  beat)
    exec celery -A config beat -l "${LOG_LEVEL:-info}"
    ;;
  *)
    exec "$@"
    ;;
esac
