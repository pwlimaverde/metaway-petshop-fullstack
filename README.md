# Metaway Petshop Fullstack

Aplicação fullstack para gestão de petshop com FastAPI + Vue 3, autenticação JWT, RBAC (Admin/Cliente) e validação de ownership no backend.

![Preview da interface](apps/web/src/assets/hero-pets.png)

## Versionamento

A versão oficial do monorepo é definida em um único local: `VERSION`.

- Versão de release atual: `v1.0.0` (valor em `VERSION` = `1.0.0`)
- Para futuras versões:
  1. atualize apenas o arquivo `VERSION`;
  2. execute `make sync-version` para propagar a versão para os manifests do monorepo.

## O que o sistema faz

O sistema centraliza a operação de um petshop com controle de acesso por perfil:

- Login com CPF e autenticação JWT.
- Gestão de clientes, pets, raças e atendimentos.
- Upload de foto para cliente e pet.
- Métricas básicas de saúde da API (`/api/v1/health` e `/api/v1/metrics`).

Funcionalidades por perfil:

- Admin: CRUD completo de usuários, clientes, endereços, contatos, raças, pets e atendimentos.
- Cliente: consulta e atualização do próprio perfil, CRUD dos próprios endereços/contatos/pets e consulta dos atendimentos dos próprios pets.

## Stack

| Camada    | Tecnologias                                                                   |
| --------- | ----------------------------------------------------------------------------- |
| Backend   | Python 3.13, FastAPI, SQLAlchemy Async, Alembic, passlib[bcrypt], python-jose |
| Frontend  | Vue 3, TypeScript, Pinia, Vue Router, TailwindCSS, Vitest                     |
| Banco     | PostgreSQL 16                                                                 |
| Infra     | Docker Compose, Nginx                                                         |
| Qualidade | Ruff, ESLint, Prettier, Pytest, Vitest                                        |

## Pré-requisitos

- Docker + Docker Compose
- GNU Make (recomendado)
- Opcional para execução local sem Docker: `uv` e Node.js 20+

## Quickstart

1. Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Suba todo o ambiente com 1 comando:

```bash
docker compose --env-file .env -f infra/docker-compose.yml up --build -d
```

Com `RUN_SEED_ON_STARTUP=true`, o seed completo roda automaticamente no primeiro startup (quando o banco está vazio).

## URLs

- Frontend: `http://localhost/`
- Swagger: `http://localhost/docs`
- Healthcheck: `http://localhost/api/v1/health`

## Credenciais de demonstração (seed)

| Perfil       | CPF                                       | Senha                                         |
| ------------ | ----------------------------------------- | --------------------------------------------- |
| Admin        | `ADMIN_SEED_CPF` (default `52998224725`)  | `ADMIN_SEED_PASSWORD` (default `Admin123`)    |
| Cliente demo | `DEMO_CLIENT_CPF` (default `12345678909`) | `DEMO_CLIENT_PASSWORD` (default `Cliente123`) |

## Estrutura do monorepo

```text
apps/
  api/      # Backend FastAPI (Clean Architecture leve)
  web/      # Frontend Vue 3 + TypeScript
infra/
  docker-compose.yml
  nginx/
docs/
  PRD.md
```

## Comandos úteis (Makefile)

| Comando        | Descrição                               |
| -------------- | --------------------------------------- |
| `make up`      | Build + start dos serviços              |
| `make down`    | Derruba o ambiente                      |
| `make logs`    | Logs do compose                         |
| `make migrate` | Aplica migrations no container da API   |
| `make seed`    | Executa seed manual no container da API |
| `make lint`    | Ruff + ESLint                           |
| `make test`    | Pytest + Vitest                         |

## Testes

```bash
make test
```

Execução local (sem Docker):

```bash
uv run --directory apps/api pytest
npm --prefix apps/web run test
```

## Documentação complementar

- PRD: [`docs/PRD.md`](docs/PRD.md)
- Guia operacional: [`help.md`](help.md)
- Backend: [`apps/api/README.md`](apps/api/README.md)
- Frontend: [`apps/web/README.md`](apps/web/README.md)

## Licença

MIT. Veja [`LICENSE`](LICENSE).
