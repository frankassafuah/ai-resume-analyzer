#!/usr/bin/env bash
# Create the resumes bucket in the local MinIO using a one-off mc container.
set -euo pipefail
cd "$(dirname "$0")/.."

BUCKET="${S3_BUCKET:-resumes}"

docker compose run --rm --entrypoint sh minio -c "
  mc alias set local http://minio:9000 minioadmin minioadmin &&
  mc mb --ignore-existing local/${BUCKET} &&
  echo 'Bucket ready: ${BUCKET}'
" 2>/dev/null || {
  # Fallback: use a standalone mc image on the compose network.
  docker run --rm --network ai-resume-analyzer_default minio/mc sh -c "
    mc alias set local http://minio:9000 minioadmin minioadmin &&
    mc mb --ignore-existing local/${BUCKET} &&
    echo 'Bucket ready: ${BUCKET}'
  "
}
