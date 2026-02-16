include .env
export

COMPOSE_FILE = infra/docker-compose.yml

.PHONY: help up down logs build migrate api-format api-lint api-test web-lint web-format web-test test lint

help:
	@echo "Targets:"
	@echo "  up          - Build and start full stack"
	@echo "  down        - Stop and remove containers"
	@echo "  logs        - Follow compose logs"
	@echo "  build       - Build all services"
	@echo "  migrate     - Run Alembic migrations in api container"
	@echo "  api-format  - Format and auto-fix backend code"
	@echo "  api-lint    - Run backend lint"
	@echo "  api-test    - Run backend tests"
	@echo "  web-lint    - Run frontend lint"
	@echo "  web-format  - Check frontend formatting"
	@echo "  web-test    - Run frontend tests"
	@echo "  test        - Run backend + frontend tests"
	@echo "  lint        - Run backend + frontend lint"

up:
	docker compose -f $(COMPOSE_FILE) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

build:
	docker compose -f $(COMPOSE_FILE) build

migrate:
	docker compose -f $(COMPOSE_FILE) exec api alembic upgrade head

api-format:
	docker compose -f $(COMPOSE_FILE) exec api sh -c "ruff format . && ruff check . --fix"

api-lint:
	docker compose -f $(COMPOSE_FILE) exec api ruff check .

api-test:
	docker compose -f $(COMPOSE_FILE) exec api pytest

web-lint:
	docker compose -f $(COMPOSE_FILE) exec web npx eslint .

web-format:
	docker compose -f $(COMPOSE_FILE) exec web npx prettier --check .

web-test:
	docker compose -f $(COMPOSE_FILE) exec web npx vitest run

test: api-test web-test

lint: api-lint web-lint
