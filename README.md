# AI Resume Analyzer

Production-grade SaaS: users compare a resume against a job description and get
an AI analysis (ATS score, compatibility score, missing keywords/skills,
strengths, weaknesses, experience gaps, a rewritten summary, a cover letter, and
interview prep questions).

**Stack:** Django/DRF · PostgreSQL (+pgvector) · Redis · Celery · Docker ·
Nuxt 4 SPA / Vue 3 / TypeScript / Tailwind v4 / shadcn-vue · multi-provider LLM layer.

**▶ How to run it: [GETTING_STARTED.md](./GETTING_STARTED.md)** (Docker or native).

Design docs & decisions: [`docs/`](./docs/) (start with
[`docs/README.md`](./docs/README.md)).

---

## Milestone status
**M0 — Foundations: scaffolded.** Monorepo, Docker Compose (Postgres+pgvector,
Redis, MinIO, api, worker, web), Django+DRF+drf-spectacular skeleton, Celery
wired to Redis with a `ping` task, Nuxt 4 SPA + shadcn-nuxt skeleton, CI, and the first
migration that enables `pgvector`. LLM provider defaults to the offline
`FakeClient` (real adapters land in M3).

## Prerequisites
Docker + Docker Compose. (For running the apps outside containers you'd also
want Python 3.12 and Node 22, but the containers are the supported path.)

## Quick start
```bash
cd ai-resume-analyzer
make bootstrap     # env file + build + start + migrate + create bucket
# or, foreground with live logs:
make up            # ./scripts/dev.sh (copies backend/.env if missing)
```
- API:      http://localhost:8000/health/
- API docs: http://localhost:8000/api/docs/
- Web:      http://localhost:3000  (shows live API health)
- MinIO:    http://localhost:9001  (minioadmin / minioadmin)

`make help` lists all targets.

## Verify M0
```bash
make ping          # -> pong   (proves Celery + Redis round-trip)
make test          # -> pytest passes in the api container
```

## Layout
```
ai-resume-analyzer/
├── backend/    Django/DRF, Celery, config/ split settings, apps/, entrypoint.sh
├── frontend/   Nuxt 4 SPA + shadcn-nuxt (Tailwind v4)
├── docker/     Dockerfiles (backend, frontend) + postgres/init/ (pgvector)
├── docs/       architecture, ADRs, locked contracts
├── scripts/    bootstrap · dev · test · lint · create-bucket
├── docker-compose.yml
├── Makefile
└── .github/workflows/ci.yml
```

## Frontend UI components
shadcn-vue (shadcn-nuxt) is the only UI library; components are copied into
`frontend/app/components/ui/`. `button` and `card` are seeded. Add more with:
```bash
cd frontend && npm run ui:add -- <name>   # e.g. sonner dialog input form badge
```
