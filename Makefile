.PHONY: help bootstrap up down build logs ps migrate makemigrations shell \
        ping test lint fmt bucket

help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

bootstrap:      ## First-time setup: env, build, start, migrate, create bucket
	./scripts/bootstrap.sh

up:             ## Start the full stack in the foreground
	./scripts/dev.sh

down:           ## Stop and remove containers
	docker compose down

build:          ## Build all images
	docker compose build

logs:           ## Tail logs
	docker compose logs -f

ps:             ## Show container status
	docker compose ps

migrate:        ## Apply database migrations
	docker compose exec api python manage.py migrate

makemigrations: ## Generate new migrations
	docker compose exec api python manage.py makemigrations

shell:          ## Open a Django shell
	docker compose exec api python manage.py shell

# M0 smoke test: enqueue the ping task and read back the result.
ping:           ## Enqueue the Celery ping task (expect: pong)
	docker compose exec api python -c "from apps.common.tasks import ping; print(ping.delay().get(timeout=10))"

test:           ## Run backend tests
	./scripts/test.sh

lint:           ## Lint backend + frontend
	./scripts/lint.sh

fmt:            ## Auto-fix backend lint
	docker compose exec api ruff check --fix .

bucket:         ## Create the MinIO bucket
	./scripts/create-bucket.sh

seed:           ## Seed the database with demo data (idempotent)
	docker compose exec api python manage.py seed
