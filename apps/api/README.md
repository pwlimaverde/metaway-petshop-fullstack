# Metaway Petshop API

API FastAPI para gestão de usuários, clientes, endereços, contatos, raças, pets e atendimentos com autenticação JWT, RBAC e ownership.

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 Async
- Alembic
- PostgreSQL (produção) / SQLite async (testes)
- Passlib + bcrypt
- JWT (`python-jose`)
- Ruff + Pytest + Pytest-Cov

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

## Como rodar localmente

1. Instale dependências:

```bash
uv sync --dev
```

2. Configure variáveis de ambiente (`.env` baseado em `.env.example`).

3. Rode migrations:

```bash
uv run alembic upgrade head
```

4. (Opcional) Seed inicial:

```bash
uv run python -m metaway_api.infra.seed_cli
```

5. Inicie a API:

```bash
uv run uvicorn metaway_api.main:app --reload --host 0.0.0.0 --port 8000
```

## Swagger e autenticação

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Healthcheck: `http://localhost:8000/api/v1/health`

### Login no Swagger (Authorize)

1. Execute `POST /api/v1/auth/login` com:
   - `username`: CPF (somente dígitos)
   - `password`: senha
2. Copie `access_token`.
3. Clique em `Authorize` e informe:
   - `Bearer <access_token>`

## Regras de acesso

### Perfis

- `ADMIN`: CRUD completo em todos os recursos.
- `CLIENTE`: apenas leitura e atualização de recursos próprios.

### Ownership

- `Address` / `Contact`: `resource.client_id == current_user.client_id`
- `Pet`: `pet.client_id == current_user.client_id`
- `Appointment`: `appointment.pet.client_id == current_user.client_id`
- Tentativa de acesso indevido retorna `403`.

## Endpoints principais (`/api/v1`)

### Público

- `GET /health`
- `GET /metrics`
- `POST /auth/login`

### Admin

- `POST|GET /users`
- `GET|PATCH|DELETE /users/{id}`
- `POST|GET /clients`
- `GET|PATCH|DELETE /clients/{id}`
- `POST|GET /clients/{client_id}/addresses`
- `POST|GET /clients/{client_id}/contacts`
- `POST|PATCH|DELETE /breeds` (GET também para cliente)
- `POST|GET|PATCH|DELETE /pets`
- `POST|GET|PATCH|DELETE /appointments`

### Cliente

- `GET|PATCH /clients/me`
- `GET /clients/me/addresses`
- `PATCH /addresses/{id}` (somente próprio)
- `GET /clients/me/contacts`
- `PATCH /contacts/{id}` (somente próprio)
- `GET /breeds`
- `GET /pets`
- `GET|PATCH /pets/{id}` (somente próprio)
- `GET /appointments`
- `GET|PATCH /appointments/{id}` (somente dos próprios pets)

### Upload e arquivos

- `POST /clients/{id}/photo` (admin ou dono)
- `POST /pets/{id}/photo` (admin ou dono)
- `GET /files/{path}`

## Qualidade

### Lint e formatação

```bash
uv run ruff format .
uv run ruff check .
```

### Testes e cobertura

```bash
uv run pytest --cov=metaway_api --cov-report=term-missing
```

## Seed inicial

O seed cria:

- Usuário admin usando:
  - `ADMIN_SEED_NAME`
  - `ADMIN_SEED_CPF`
  - `ADMIN_SEED_PASSWORD`
- Raças iniciais:
  - Labrador
  - Golden Retriever
  - Poodle
  - Bulldog
  - Shih Tzu
  - Pastor Alemão
  - Pinscher
  - Vira-lata

Se quiser executar seed automaticamente no startup:

```env
RUN_SEED_ON_STARTUP=true
```
