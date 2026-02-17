# Metaway Petshop API

API FastAPI do sistema Metaway Petshop, com autenticação JWT (CPF como username), RBAC (`ADMIN`/`CLIENTE`) e ownership validado no backend.

> Versionamento do monorepo: fonte única em `VERSION` (raiz).
> Para sincronizar esta API com a versão global: `make sync-version`.

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2 Async
- Alembic
- PostgreSQL
- passlib[bcrypt]
- PyJWT (JWT)
- Ruff + Pytest

## Estrutura

```text
apps/api/
├── alembic/
├── src/metaway_api/
│   ├── application/
│   ├── domain/
│   ├── infra/
│   ├── interfaces/
│   └── main.py
├── tests/
├── pyproject.toml
└── alembic.ini
```

## Execução local (sem Docker)

```bash
uv sync --dev
uv run alembic upgrade head
uv run python -m metaway_api.infra.seed_cli
uv run uvicorn metaway_api.main:app --reload --host 0.0.0.0 --port 8000
```

## Execução via Docker (raiz do monorepo)

```bash
make up
make migrate
make seed
```

## Swagger e autenticação

- Swagger UI: `http://localhost/docs`
- OpenAPI JSON: `http://localhost/openapi.json`
- Healthcheck: `http://localhost/api/v1/health`
- Métricas: `http://localhost/api/v1/metrics`

Fluxo:

1. `POST /api/v1/auth/login` (`username`=CPF, `password`=senha).
2. Copiar `access_token`.
3. `Authorize` no Swagger com `Bearer <access_token>`.

## Regras de acesso

- `ADMIN`: CRUD completo.
- `CLIENTE`:
  - CRUD de próprios endereços, contatos e pets.
  - leitura e atualização de `clients/me`.
  - somente leitura de atendimentos dos próprios pets.
- Ownership inválido retorna `403`.

## Seed de demonstração

Variáveis relevantes:

- `ADMIN_SEED_NAME`, `ADMIN_SEED_CPF`, `ADMIN_SEED_PASSWORD`
- `DEMO_CLIENT_NAME`, `DEMO_CLIENT_CPF`, `DEMO_CLIENT_PASSWORD`
- `RUN_SEED_ON_STARTUP`

O seed cria:

- 1 admin
- 1 cliente demo com:
  - 2 endereços
  - 2 contatos
  - 3 pets (raças diferentes)
  - 5 atendimentos distribuídos
- 4 clientes extras
- Raças populares iniciais

Com `RUN_SEED_ON_STARTUP=true`, o seed só executa automaticamente quando o banco está vazio.

## Qualidade

```bash
uv run ruff format .
uv run ruff check .
uv run pytest --cov=metaway_api --cov-report=term-missing
```
