# Metaway Petshop Fullstack

Sistema de gestão de petshop com controle de clientes, pets, raças e atendimentos.
Monorepo fullstack construído com **FastAPI**, **Vue 3** e **PostgreSQL**.

## Estrutura do Projeto

```
├── apps/
│   ├── api/     # Backend — FastAPI + SQLAlchemy + Alembic
│   └── web/     # Frontend — Vue 3 + TypeScript + Pinia + TailwindCSS
├── infra/
│   ├── docker-compose.yml
│   └── nginx/   # Gateway reverso
├── docs/
│   └── PRD.md   # Documento de requisitos do produto
├── Makefile
└── .env.example
```

## Pré-requisitos

| Ferramenta         | Versão mínima |
| ------------------ | ------------- |
| Python             | 3.13+         |
| [uv](https://docs.astral.sh/uv/) | latest |
| Node.js            | 20+           |
| Docker + Compose   | latest        |

## Início Rápido

```bash
# 1. Copie e configure as variáveis de ambiente
cp .env.example .env

# 2. Suba todos os serviços (API, Web, PostgreSQL, Nginx)
make up

# 3. Execute as migrations do banco
make migrate

# 4. Acompanhe os logs
make logs
```

A aplicação estará disponível em `http://localhost` (via Nginx).

## Comandos Disponíveis

| Comando          | Descrição                              |
| ---------------- | -------------------------------------- |
| `make up`        | Build e start de todos os serviços     |
| `make down`      | Para e remove os containers            |
| `make logs`      | Acompanha os logs em tempo real        |
| `make build`     | Build de todas as imagens              |
| `make migrate`   | Executa as migrations (Alembic)        |
| `make api-lint`  | Lint do backend (Ruff)                 |
| `make api-format`| Formatação e auto-fix do backend       |
| `make api-test`  | Testes do backend (pytest)             |
| `make web-lint`  | Lint do frontend (ESLint)              |
| `make web-test`  | Testes do frontend (Vitest)            |
| `make lint`      | Lint completo (backend + frontend)     |
| `make test`      | Testes completos (backend + frontend)  |

## Stack Técnica

**Backend** — Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pydantic, JWT (python-jose), bcrypt (passlib), Ruff

**Frontend** — Vue 3, TypeScript, Pinia, Vue Router, TailwindCSS, Vite, Vitest

**Infraestrutura** — Docker Compose, PostgreSQL 16, Nginx

## Documentação

- [Documento de Requisitos do Produto (PRD)](docs/PRD.md)
