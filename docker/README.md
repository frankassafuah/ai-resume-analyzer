# docker/

Container build definitions and container-only support files.

```
docker/
├── backend.Dockerfile     # api + worker image (build context: ../backend)
├── frontend.Dockerfile    # Nuxt SPA image (build context: ../frontend)
└── postgres/init/         # SQL run once on first DB init (enables pgvector)
```

`docker-compose.yml` (repo root) references these via `build.dockerfile`. Build
contexts stay scoped to each service directory, so:

- `backend.Dockerfile` COPYs from `backend/` (incl. `entrypoint.sh`, which lives
  in `backend/` because it must be inside that build context).
- `frontend.Dockerfile` COPYs from `frontend/`.

The Postgres init script is redundant with Django's first migration
(`CREATE EXTENSION vector`); both exist so the extension is present regardless of
how the DB is provisioned (ADR-0004).
