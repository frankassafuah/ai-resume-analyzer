# Getting Started — Running the Project

Two ways to run. **Option A (Docker)** is the supported, zero-config path.
**Option B (Native)** runs Django/Celery/Nuxt on your host using the Python
venv, with Docker providing only Postgres + Redis.

> Ports used: API `8000`, Web `3000`, Postgres `5432`, Redis `6379`,
> MinIO `9000` (API) / `9001` (console).

---

## Option A — Docker (recommended)

Everything runs in containers, wired together automatically.

```bash
cd ai-resume-analyzer

# First time: create .env, build images, start, migrate, create storage bucket
make bootstrap

# Day-to-day: start in the foreground with live logs
make up
```

Then open / verify:
- API health → http://localhost:8000/health/  → `{"status":"ok"}`
- API docs   → http://localhost:8000/api/docs/
- Web app    → http://localhost:3000
- MinIO UI   → http://localhost:9001  (minioadmin / minioadmin)
- Celery     → `make ping`  → prints `pong`

Stop everything:
```bash
make down
```

`make help` lists every target.

---

## Option B — Native (Python venv + host Node)

Run the servers on your machine; let Docker provide just the databases.

### One-time setup (already done if you followed the install)
```bash
cd ai-resume-analyzer/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # Django, DRF, Celery, etc.
```

### 1. Start infrastructure only (Postgres + Redis + MinIO)
These publish to `localhost`:
```bash
cd ai-resume-analyzer
docker compose up -d db redis minio
```

### 2. Point the app at localhost
`backend/.env` uses Docker hostnames (`db`, `redis`), which don't resolve on the
host. Shell exports take precedence over `.env`, so set these **without editing
the file** (keeps Docker mode working too). Run in every backend terminal:
```bash
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/resume_analyzer"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="$REDIS_URL"
export CELERY_RESULT_BACKEND="$REDIS_URL"
```
Tip: `source ../scripts/env.local.sh` does exactly this (see below).

### 3. Backend API  (terminal 1 — venv active)
```bash
cd ai-resume-analyzer/backend
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 4. Celery worker  (terminal 2 — venv active, same exports)
```bash
cd ai-resume-analyzer/backend
source .venv/bin/activate && source ../scripts/env.local.sh
celery -A config worker -l info -Q default,parsing,analysis,generation
```

### 5. Frontend  (terminal 3)
```bash
cd ai-resume-analyzer/frontend
npm install          # first time only; also generates .nuxt/ (fixes IDE type errors)
npm run dev
```

Verify the same URLs as Option A.

> ⚠️ Don't mix modes: if running native (B), do **not** also start the `api` /
> `worker` containers — they'd fight over port 8000 and the database.

---

## Which should I use?
- **Just want it running / demoing** → Option A.
- **Actively editing backend code with debugger/breakpoints** → Option B (the
  venv also powers IDE autocomplete, `pytest`, and `ruff`).

## Troubleshooting
- **`make: command not found`** → run the underlying `docker compose ...` shown
  in the Makefile, or install `make`.
- **Port already in use** → something else holds 8000/3000/5432/6379; stop it or
  change the host port mapping in `docker-compose.yml`.
- **Frontend shows "Cannot reach API"** → the API isn't up yet, or CORS; confirm
  http://localhost:8000/health/ responds and `CORS_ALLOWED_ORIGINS` includes
  `http://localhost:3000`.
- **IDE red errors under `frontend/.nuxt/...`** → run `npm install` in
  `frontend/` (its `postinstall` runs `nuxt prepare`, generating `.nuxt/`).
