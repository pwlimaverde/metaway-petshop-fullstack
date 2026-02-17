-include .env
export

COMPOSE_FILE = infra/docker-compose.yml
COMPOSE_CMD  = docker compose --env-file .env -f $(COMPOSE_FILE)
AUTO_MIGRATION_MSG = auto_$(shell uv run --directory $(API_DIR) python -c "from datetime import datetime as d; n=d.now(); print(f'{n.year:04d}{n.month:02d}{n.day:02d}_{n.hour:02d}{n.minute:02d}{n.second:02d}')")
MIGRATION_MSG ?= $(AUTO_MIGRATION_MSG)
DOCKER_HOST_NO_SCHEME := $(patsubst ssh://%,%,$(DOCKER_HOST))
DOCKER_HOST_NAME := $(lastword $(subst @, ,$(DOCKER_HOST_NO_SCHEME)))
ALEMBIC_DB_HOST ?= $(if $(DOCKER_HOST),$(DOCKER_HOST_NAME),localhost)
ALEMBIC_DATABASE_URL ?= $(if $(DATABASE_URL),$(subst @db:,@$(ALEMBIC_DB_HOST):,$(DATABASE_URL)),postgresql+asyncpg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(ALEMBIC_DB_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB))

# Caminhos dos sub-projetos
API_DIR = apps/api
WEB_DIR = apps/web

.PHONY: help up down logs build rebuild-web rebuild-api rebuild-front rebuild-back migrate makemigrations seed sync-version \
        api-format api-lint api-test \
        web-lint web-format web-test \
        test lint format

help:
	@echo "=== Comandos Docker ==="
	@echo "  up          - Build and start full stack"
	@echo "  down        - Stop and remove containers"
	@echo "  logs        - Follow compose logs"
	@echo "  build       - Build all services"
	@echo "  rebuild-web - Rebuild and start only web service"
	@echo "  rebuild-api - Rebuild and start only api service"
	@echo "  rebuild-front - Alias for rebuild-web"
	@echo "  rebuild-back  - Alias for rebuild-api"
	@echo "  migrate         - Run Alembic migrations (upgrade head)"
	@echo "  seed            - Run demo seed data in api container"
	@echo "  sync-version    - Sync monorepo version from VERSION file"
	@echo "  makemigrations  - Generate new Alembic revision (autogenerate)"
	@echo ""
	@echo "=== Backend (local via uv) ==="
	@echo "  api-format  - Format and auto-fix backend code"
	@echo "  api-lint    - Run backend lint"
	@echo "  api-test    - Run backend tests"
	@echo ""
	@echo "=== Frontend (local via npm) ==="
	@echo "  web-lint    - Run frontend lint"
	@echo "  web-format  - Check frontend formatting"
	@echo "  web-test    - Run frontend tests"
	@echo ""
	@echo "=== Atalhos ==="
	@echo "  test        - Run backend + frontend tests"
	@echo "  lint        - Run backend + frontend lint"
	@echo "  format      - Format backend + frontend code"

# --------------------------------------------------
# Docker
# --------------------------------------------------
up:
	$(COMPOSE_CMD) up -d --build

down:
	$(COMPOSE_CMD) down

logs:
	$(COMPOSE_CMD) logs -f

build:
	$(COMPOSE_CMD) build

rebuild-web:
	$(COMPOSE_CMD) up -d --build web

rebuild-api:
	$(COMPOSE_CMD) up -d --build api

rebuild-front: rebuild-web

rebuild-back: rebuild-api

migrate:
	$(COMPOSE_CMD) exec api alembic upgrade head

seed:
	$(COMPOSE_CMD) exec api python -m metaway_api.infra.seed_cli

sync-version:
	python scripts/sync_version.py

makemigrations:
ifeq ($(OS),Windows_NT)
	set "DATABASE_URL=$(ALEMBIC_DATABASE_URL)" && uv run --directory $(API_DIR) alembic revision --autogenerate -m "$(or $(msg),$(MIGRATION_MSG))"
else
	DATABASE_URL="$(ALEMBIC_DATABASE_URL)" uv run --directory $(API_DIR) alembic revision --autogenerate -m "$(or $(msg),$(MIGRATION_MSG))"
endif

# --------------------------------------------------
# Backend — executado localmente com uv
# --------------------------------------------------
api-format:
	cd $(API_DIR) && uv run ruff format .
	cd $(API_DIR) && uv run ruff check . --fix

api-lint:
	cd $(API_DIR) && uv run ruff check .

api-test:
	cd $(API_DIR) && uv run pytest

# --------------------------------------------------
# Frontend — executado localmente com npm
# --------------------------------------------------
web-lint:
	npm run --prefix $(WEB_DIR) lint

web-format:
	npm run --prefix $(WEB_DIR) format

web-test:
	npm run --prefix $(WEB_DIR) test

# --------------------------------------------------
# Atalhos combinados
# --------------------------------------------------
test: api-test web-test

lint: api-lint web-lint

format: api-format web-format
