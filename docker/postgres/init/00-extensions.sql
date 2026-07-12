-- Runs once on first Postgres container init (empty data dir).
-- Makes pgvector available at the DB level; Django's first migration also
-- issues CREATE EXTENSION, so this is belt-and-suspenders (ADR-0004).
CREATE EXTENSION IF NOT EXISTS vector;
