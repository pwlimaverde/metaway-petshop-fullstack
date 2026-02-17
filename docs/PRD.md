# PRD — metaway-petshop-fullstack (Desafio Técnico Metaway)

> Documento de referência único (**source of truth**) para construção do sistema **Petshop** em **Monorepo** (Backend **FastAPI / Python 3.13.9** + Frontend **Vue 3 / TypeScript**) com **PostgreSQL** e **Docker Compose**.

---

## 1. Visão do Produto

Sistema web + API para gestão de **clientes**, **pets**, **raças** e **atendimentos** de um petshop, com autenticação e autorização por perfil (**RBAC**) e regra de propriedade (**ownership**):

- **Admin**: acesso total — pode **incluir, excluir, alterar e visualizar** qualquer cadastro.
- **Cliente**: acesso restrito aos seus próprios dados, com permissões granulares por recurso (ver seção 7.2).

---

## 2. Objetivos

### 2.1 Objetivos do desafio

- Demonstrar entrega end-to-end: **API + UI + DB + Docker**.
- Aplicar boas práticas (Clean Architecture leve, testes, documentação).
- Garantir segurança básica (hash de senha, JWT, RBAC + ownership).

### 2.2 Objetivos do produto (MVP)

- Autenticar usuários usando **CPF como username**.
- Permitir que Admin gerencie todo o cadastro (clientes, pets, raças, atendimentos, endereços, contatos).
- Permitir que Cliente gerencie (CRUD) seus endereços, contatos e pets, edite seu perfil, e consulte atendimentos (somente leitura).

---

## 3. Escopo (MVP)

### 3.1 Requisitos obrigatórios (conforme PDF)

- Banco de dados relacional (PostgreSQL).
- Testes unitários para demonstrar funcionamento da API.
- Autenticação por token JWT.
- Autorização role-based.
- Versionamento Git, público.
- Stack: Python + FastAPI.

### 3.2 Desejáveis (conforme PDF)

| Desejável | Status no projeto |
|-----------|-------------------|
| Documentação da API (Swagger/OpenAPI) | **Incluído** — FastAPI gera `/docs` automaticamente |
| Métricas de funcionamento (heartbeat, memória, CPU) | **Incluído** — endpoints `/health` e `/metrics` |
| Containerização (Docker) | **Incluído** — Docker Compose com Nginx gateway |
| Instruções de uso (`help.md`) | **Incluído** |
| Fotos no cadastro de Pets e Cliente | **Incluído** — upload com armazenamento local |
| CPF como nome de usuário | **Incluído** — login via CPF |

---

## 4. Stack Tecnológica (imutável)

### 4.1 Backend (API)

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python **3.13.9** |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (Async) |
| Migrations | Alembic |
| Banco de dados | PostgreSQL |
| Auth | JWT (stateless) via `python-jose[cryptography]` |
| Hash de senha | `passlib[bcrypt]` |
| Gerenciador | **uv** (Astral) — nunca pip/poetry |
| Lint/Format | Ruff (lint + format) |
| Type check | mypy (opcional) |

### 4.2 Frontend (Web)

| Componente | Tecnologia |
|------------|------------|
| Framework | Vue 3 (Composition API) |
| Linguagem | TypeScript |
| Estado | Pinia |
| Rotas | Vue Router |
| Estilização | TailwindCSS |
| HTTP Client | Axios |
| Testes | Vitest |
| Ícones | lucide-vue-next |
| Variantes CSS | class-variance-authority (cva) |
| Merge de classes | clsx + tailwind-merge |
| UI Headless | @headlessui/vue (Modais, Popovers) |

### 4.3 Infraestrutura

| Componente | Tecnologia |
|------------|------------|
| Orquestração | Docker Compose |
| Gateway | Nginx (reverse proxy, porta única) |

### 4.4 Dependências do backend (`apps/api/pyproject.toml`)

- `requires-python = ">=3.13,<4.0"`
- **Runtime**: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic`, `python-dotenv`, `passlib[bcrypt]`, `python-jose[cryptography]`
- **Dev**: `pytest`, `pytest-cov`, `pytest-asyncio`, `httpx`, `ruff`, `mypy` (opcional)

---

## 5. Arquitetura do Backend (Clean Architecture Leve)

Separação simples por camadas — sem overengineering.

```
src/metaway_api/
├── domain/         # Entidades e regras de negócio puras
├── application/    # Use cases (orquestração)
├── infra/          # Repositórios SQLAlchemy, sessão DB, auth/jwt, storage
└── interfaces/     # Routers FastAPI + DTOs (schemas Pydantic)
```

### 5.1 Convenções de arquitetura

- **Routers finos**: validam entrada e delegam ao use case.
- **Use cases testáveis**: com repositórios fake/mocks (sem dependência de DB nos testes).
- **Schemas Pydantic**: separados em `Create`, `Update`, `Response`.
- **Erros padronizados**: 400 (bad request), 401 (não autenticado), 403 (proibido), 404 (não encontrado), 422 (validação).
- **Paginação simples** em listagens (offset + limit).
- **Logs estruturados** (mínimo) para rastreabilidade.

---

## 6. Estrutura do Monorepo

```
metaway-petshop-fullstack/
├── apps/
│   ├── api/
│   │   ├── src/metaway_api/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   ├── infra/
│   │   │   ├── interfaces/
│   │   │   └── main.py
│   │   ├── alembic/
│   │   ├── alembic.ini
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   ├── uv.lock
│   │   └── Dockerfile
│   └── web/
│       └── (Vue 3 app)
├── infra/
│   ├── docker-compose.yml
│   └── nginx/
│       └── nginx.conf
├── docs/
│   └── PRD.md
├── .env.example
├── help.md
├── Makefile
└── README.md
```

---

## 7. Perfis, Permissões e Regras de Acesso

### 7.1 Perfis

| Perfil | Descrição | Operações permitidas |
|--------|-----------|----------------------|
| **Admin** | Acesso total ao sistema | **Incluir, excluir, alterar, visualizar** (CRUD completo) |
| **Cliente** | Acesso restrito (ownership) | Permissões granulares por recurso (ver matriz abaixo) |

### 7.2 Matriz de permissões por recurso

| Recurso | Admin | Cliente |
|---------|-------|---------|
| Users | CRUD completo | Sem acesso |
| Clients | CRUD completo | READ + UPDATE (apenas `/me`) |
| Addresses | CRUD completo (qualquer cliente) | **CRUD completo** (apenas próprios) |
| Contacts | CRUD completo (qualquer cliente) | **CRUD completo** (apenas próprios) |
| Breeds | CRUD completo | READ (listagem) |
| Pets | CRUD completo | **CRUD completo** (apenas próprios) |
| Appointments | CRUD completo | **READ only** (apenas de seus pets) |
| Fotos (Client/Pet) | Upload para qualquer um | Upload apenas para si/seus pets |

> **Resumo Cliente**: pode criar, visualizar, alterar e excluir endereços, contatos e pets próprios. Atendimentos são somente leitura. Não tem acesso a usuários nem raças (exceto listagem).

### 7.3 Regras de ownership (críticas)

- Cliente só acessa recurso se `resource.client_id == current_user.client_id`.
- Para **Pets**: validar `pet.client_id == current_user.client_id`.
- Para **Atendimentos**: validar que `appointment.pet.client_id == current_user.client_id`.
- Para **Endereços/Contatos**: validar `address.client_id == current_user.client_id` / `contact.client_id == current_user.client_id`.
- Tentativa de acessar recurso de outro cliente → **403 Forbidden**.

---

## 8. Modelo de Dados

### 8.1 Princípios de modelagem

- Modelo relacional em 3FN, com separação entre autenticação/autorização e dados de domínio.
- Fonte única para identidade de login: `users.cpf`.
- Fonte única para dados cadastrais do cliente: `clients`.
- Ownership derivado exclusivamente da cadeia de FKs (`user -> client -> pet -> appointment`).
- Evitar duplicidade de atributos entre tabelas para reduzir inconsistência e custo de manutenção.

### 8.2 Diagrama lógico de relacionamentos

```
User (role=ADMIN) (1)     -> (0)   Client
User (role=CLIENTE) (1)   -> (1)   Client
Client (0..1)             -> (1)   User(role=CLIENTE)

Client (1) -> (N) Address
Client (1) -> (N) Contact
Client (1) -> (N) Pet
Pet    (N) -> (1) Breed
Pet    (1) -> (N) Appointment
```

Observação: um `Client` pode existir sem `User` vinculado até o momento de criação da credencial de acesso.

### 8.3 Entidades e atributos

#### User

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `cpf` | string | **UNIQUE**, NOT NULL — username do login |
| `role` | enum | `ADMIN` \| `CLIENTE`, NOT NULL |
| `password_hash` | string | NOT NULL |
| `client_id` | FK → `clients.id` | UNIQUE, NULL para ADMIN, obrigatório para CLIENTE |
| `name` | string | obrigatório para ADMIN; nulo para CLIENTE (nome vem de `clients.name`) |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Client

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `name` | string | NOT NULL |
| `photo_url` | string | NULLABLE |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Address

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `client_id` | FK → `clients.id` | NOT NULL |
| `logradouro` | string | NOT NULL |
| `numero` | string | NOT NULL |
| `complemento` | string | NULLABLE |
| `bairro` | string | NOT NULL |
| `cidade` | string | NOT NULL |
| `estado` | string(2) | NOT NULL — UF (ex: SP, RJ) |
| `cep` | string | NOT NULL |
| `tag` | string | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Contact

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `client_id` | FK → `clients.id` | NOT NULL |
| `tag` | string | NOT NULL |
| `tipo` | enum | `EMAIL` \| `TELEFONE`, NOT NULL |
| `valor` | string | NOT NULL |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Breed

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `descricao` | string | NOT NULL, UNIQUE |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Pet

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `client_id` | FK → `clients.id` | NOT NULL |
| `breed_id` | FK → `breeds.id` | NOT NULL |
| `name` | string | NOT NULL |
| `birth_date` | date | NOT NULL |
| `photo_url` | string | NULLABLE |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

#### Appointment (Atendimento)

| Campo | Tipo | Restrições |
|-------|------|------------|
| `id` | UUID / int | PK |
| `pet_id` | FK → `pets.id` | NOT NULL |
| `descricao` | string | NOT NULL |
| `valor` | decimal | NOT NULL |
| `data` | datetime | NOT NULL |
| `status` | enum | `AGENDADO` \| `EM_ANDAMENTO` \| `CONCLUIDO` \| `CANCELADO`, NOT NULL, default `AGENDADO` |
| `created_at` | datetime | NOT NULL, default `now()` |
| `updated_at` | datetime | NOT NULL, default `now()`, atualizado automaticamente |

### 8.4 Regras de integridade e consistência

- `users.cpf` é único e obrigatório.
- `users.client_id` é único para garantir no máximo um usuário de login por cliente.
- `users.role = CLIENTE` exige `users.client_id` preenchido.
- `users.role = ADMIN` exige `users.client_id = NULL`.
- `users.role = CLIENTE` exige `users.name = NULL`.
- `users.role = ADMIN` exige `users.name` preenchido.
- `pets.client_id` e `appointments.pet_id` são obrigatórios para manter a cadeia de ownership.
- `appointments.status` padrão `AGENDADO`; valores válidos: `AGENDADO`, `EM_ANDAMENTO`, `CONCLUIDO`, `CANCELADO`.
- Todas as entidades possuem `created_at` (imutável) e `updated_at` (atualizado automaticamente a cada modificação).
- Ownership deve ser validado no backend; frontend não é controle de segurança.

---

## 9. Requisitos Funcionais (RF)

### RF-01 — Login (CPF como username)

- **Entrada**: CPF (apenas dígitos ou formato com máscara aceito) + senha.
- **Saída**: JWT (`access_token`) e `token_type=bearer`.
- **Falhas**: credenciais inválidas → **401**.

### RF-02 — Emissão e validação de JWT

- JWT deve conter no mínimo:
  - `sub`: id do usuário
  - `role`: ADMIN | CLIENTE
  - `client_id`: obrigatório para CLIENTE; null para ADMIN
  - `exp`: expiração
- API deve validar token em todas as rotas protegidas.
- Swagger com botão **Authorize** para facilitar testes.

### RF-03 — Gestão de Usuários (Admin)

- Admin pode: **criar, listar, visualizar, atualizar e excluir** usuários.
- CPF é único e serve como username.
- **Cliente não tem acesso** a nenhuma operação de usuários.

### RF-04 — Clientes (dados cadastrais)

- **Admin**: CRUD completo de clientes.
- **Cliente**:
  - `GET /clients/me` — consultar seus dados.
  - `PATCH /clients/me` — editar seus dados.
  - **Não pode** criar nem excluir clientes.

### RF-05 — Endereços do Cliente

- **Admin**: CRUD de endereços de qualquer cliente.
- **Cliente**:
  - **Criar** endereços para si (`POST /clients/me/addresses`).
  - **Visualizar** seus endereços (`GET /clients/me/addresses`).
  - **Alterar** seus endereços (`PATCH /addresses/{id}` com ownership).
  - **Excluir** seus endereços (`DELETE /addresses/{id}` com ownership).
- Campos: `logradouro`, `numero`, `complemento` (opcional), `bairro`, `cidade`, `estado` (UF), `cep`, `tag`.

### RF-06 — Contatos do Cliente

- **Admin**: CRUD de contatos de qualquer cliente.
- **Cliente**:
  - **Criar** contatos para si (`POST /clients/me/contacts`).
  - **Visualizar** seus contatos (`GET /clients/me/contacts`).
  - **Alterar** seus contatos (`PATCH /contacts/{id}` com ownership).
  - **Excluir** seus contatos (`DELETE /contacts/{id}` com ownership).
- Campos: `tag`, `tipo` (email/telefone), `valor`.

### RF-07 — Raças

- **Admin**: CRUD de raças.
- **Cliente**: apenas **leitura/listagem**.
- Campo: `descricao`.

### RF-08 — Pets

- **Admin**: CRUD total.
- **Cliente**:
  - **Criar** pets para si (`POST /pets` com ownership — `client_id` deve ser o próprio).
  - **Visualizar** seus pets (`GET /pets` filtra por ownership).
  - **Alterar** seus pets (`PATCH /pets/{id}` com ownership).
  - **Excluir** seus pets (`DELETE /pets/{id}` com ownership).
- Campos: `client_id`, `breed_id`, `birth_date`, `name`.

### RF-09 — Atendimentos

- **Admin**: CRUD total.
- **Cliente**:
  - **Visualizar** atendimentos dos seus pets (somente leitura).
  - **Não pode** criar, alterar nem excluir atendimentos.
- Campos: `pet_id`, `descricao`, `valor`, `data`, `status`.

### RF-10 — Upload de fotos (desejável)

- Permitir upload de foto para **Client** e **Pet**.
- Admin pode fazer upload para qualquer cliente/pet.
- Cliente pode fazer upload apenas para si e seus pets.
- Armazenamento em disco (volume Docker) com path salvo no campo `photo_url`.
- Formatos aceitos: JPEG, PNG.
- Tamanho máximo: 5 MB (configurável).

### RF-11 — Healthcheck e métricas (desejável)

- `GET /health` → `{ "status": "ok" }` — healthcheck para orquestração Docker.
- `GET /metrics` → métricas simples: uptime, uso de memória, CPU.

---

## 10. Contrato de API

**Prefixo global**: `/api/v1`

### 10.1 Health e Métricas (público)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/health` | Healthcheck | Público |
| GET | `/metrics` | Métricas (uptime, mem, cpu) | Público |

### 10.2 Auth

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/auth/login` | Login CPF + senha → JWT | Público |

### 10.3 Users (Admin)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/users` | Criar usuário | Admin |
| GET | `/users` | Listar usuários | Admin |
| GET | `/users/{id}` | Detalhe de um usuário | Admin |
| PATCH | `/users/{id}` | Atualizar usuário | Admin |
| DELETE | `/users/{id}` | Excluir usuário | Admin |

### 10.4 Clients

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/clients` | Criar cliente | Admin |
| GET | `/clients` | Listar clientes | Admin |
| GET | `/clients/{id}` | Detalhe de um cliente | Admin |
| PATCH | `/clients/{id}` | Atualizar cliente | Admin |
| DELETE | `/clients/{id}` | Excluir cliente | Admin |
| GET | `/clients/me` | Meus dados | Cliente |
| PATCH | `/clients/me` | Editar meus dados | Cliente |

### 10.5 Addresses

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/clients/{client_id}/addresses` | Criar endereço para cliente | Admin |
| POST | `/clients/me/addresses` | Criar meu endereço | Cliente |
| GET | `/clients/{client_id}/addresses` | Listar endereços do cliente | Admin |
| GET | `/clients/me/addresses` | Listar meus endereços | Cliente |
| PATCH | `/addresses/{id}` | Atualizar endereço | Admin ou dono |
| DELETE | `/addresses/{id}` | Excluir endereço | Admin ou dono |

### 10.6 Contacts

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/clients/{client_id}/contacts` | Criar contato para cliente | Admin |
| POST | `/clients/me/contacts` | Criar meu contato | Cliente |
| GET | `/clients/{client_id}/contacts` | Listar contatos do cliente | Admin |
| GET | `/clients/me/contacts` | Listar meus contatos | Cliente |
| PATCH | `/contacts/{id}` | Atualizar contato | Admin ou dono |
| DELETE | `/contacts/{id}` | Excluir contato | Admin ou dono |

### 10.7 Breeds

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/breeds` | Criar raça | Admin |
| GET | `/breeds` | Listar raças | Admin + Cliente |
| GET | `/breeds/{id}` | Detalhe de uma raça | Admin + Cliente |
| PATCH | `/breeds/{id}` | Atualizar raça | Admin |
| DELETE | `/breeds/{id}` | Excluir raça | Admin |

### 10.8 Pets

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/pets` | Criar pet | Admin + Cliente (ownership) |
| GET | `/pets` | Listar pets (Admin: todos; Cliente: próprios) | Admin + Cliente |
| GET | `/pets/{id}` | Detalhe de um pet | Admin + Cliente (ownership) |
| PATCH | `/pets/{id}` | Atualizar pet | Admin + Cliente (ownership) |
| DELETE | `/pets/{id}` | Excluir pet | Admin ou dono |

### 10.9 Appointments

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/appointments` | Criar atendimento | Admin |
| GET | `/appointments` | Listar (Admin: todos; Cliente: de seus pets) | Admin + Cliente |
| GET | `/appointments/{id}` | Detalhe de um atendimento | Admin + Cliente (ownership) |
| PATCH | `/appointments/{id}` | Atualizar atendimento | Admin |
| DELETE | `/appointments/{id}` | Excluir atendimento | Admin |

### 10.10 Upload de Fotos (desejável)

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/clients/{id}/photo` | Upload foto do cliente | Admin ou dono |
| POST | `/pets/{id}/photo` | Upload foto do pet | Admin ou dono do pet |

---

## 11. Autenticação e Segurança

### 11.1 Fluxo JWT

1. Cliente envia `POST /api/v1/auth/login` com CPF + senha.
2. Backend valida credenciais (bcrypt compare).
3. Retorna JWT com payload padronizado.
4. Requisições subsequentes incluem header `Authorization: Bearer <token>`.
5. Swagger disponibiliza botão **Authorize** para facilitar testes.

### 11.2 Payload do JWT

```json
{
  "sub": "<user_id>",
  "role": "ADMIN | CLIENTE",
  "client_id": "<client_id ou null>",
  "exp": "<timestamp>"
}
```

### 11.3 Guards (dependências FastAPI)

| Guard | Descrição |
|-------|-----------|
| `get_current_user` | Extrai e valida JWT do header Authorization |
| `require_roles("ADMIN")` | Restringe acesso apenas a Admin |
| `require_roles("ADMIN", "CLIENTE")` | Permite acesso a ambos os perfis |
| Ownership check | Valida `resource.client_id == current_user.client_id` |

### 11.4 Segurança de senha

- Hash com `passlib[bcrypt]` — nunca armazenar senha em texto.
- **Nunca** commitar `.env` com segredos reais.
- `.env.example` com valores placeholder para documentação.

---

## 12. Infraestrutura (Docker Compose + Nginx)

### 12.1 Serviços Docker

| Serviço | Imagem | Porta interna | Descrição |
|---------|--------|---------------|-----------|
| `db` | PostgreSQL | 5432 | Banco de dados |
| `api` | Build (Dockerfile) | 8000 | Backend FastAPI |
| `web` | Nginx + build Vue | 80 | Frontend estático |
| `nginx` | Nginx | 80 → host | Gateway / reverse proxy |

### 12.2 URLs com gateway Nginx

| URL | Destino |
|-----|---------|
| `http://localhost/` | Frontend Vue |
| `http://localhost/api/v1/...` | API FastAPI |
| `http://localhost/docs` | Swagger UI |
| `http://localhost/openapi.json` | OpenAPI JSON |

### 12.3 Comando único

```bash
docker compose -f infra/docker-compose.yml up --build
```

### 12.4 Critério de pronto (fundação)

- `http://localhost` abre o frontend.
- `http://localhost/api/v1/health` retorna `{ "status": "ok" }`.
- `http://localhost/docs` abre o Swagger.

---

## 13. Banco de Dados e Migrations (Alembic)

### 13.1 Configuração

- Engine async com `asyncpg`.
- Sessionmaker async.
- Alembic configurado para operação assíncrona.

### 13.2 Migration inicial

- Todas as tabelas com FKs e constraints.
- Índices em campos de busca frequente (`users.cpf` e FKs como `client_id`/`pet_id`).

### 13.3 Seed mínimo

- **Admin padrão**: CPF e senha definidos via variável de ambiente.
- **Raças iniciais**: breeds comuns para facilitar avaliação.

### 13.4 Critério de pronto

- `alembic upgrade head` roda dentro do container `api` sem erro.
- Constraints e FKs criadas corretamente.
- Seed popula admin e raças iniciais.

---

## 14. Upload de Fotos (desejável)

### 14.1 Estratégia de armazenamento

- Armazenamento em disco no container com volume Docker: `./storage:/app/storage`.
- Campo `photo_url` no banco (path relativo).
- Servir imagens via Nginx (static files) ou rota dedicada `GET /api/v1/files/{path}`.

### 14.2 Regras de acesso

- Admin pode fazer upload para qualquer cliente/pet.
- Cliente pode fazer upload apenas para si e seus pets (ownership).
- Formatos aceitos: JPEG, PNG.
- Tamanho máximo: 5 MB (configurável via env).

---

## 15. Requisitos de UI (Frontend) — MVP

### 15.1 Telas mínimas

| Tela | Perfil | Descrição |
|------|--------|-----------|
| Login | Público | CPF + senha |
| Dashboard | Ambos | Boas-vindas + perfil + atalhos |
| Meu Perfil | Cliente | Visualizar e editar dados pessoais, endereços e contatos (CRUD) |
| Meus Pets | Cliente | Listar, criar, editar e excluir pets |
| Meus Atendimentos | Cliente | Visualizar atendimentos dos seus pets (somente leitura) |
| Clientes | Admin | Listar, criar, editar, excluir |
| Pets | Admin | Listar, criar, editar, excluir |
| Raças | Admin | CRUD completo |
| Atendimentos | Admin | Listar, criar, editar, excluir |

### 15.2 Tarefas técnicas

- Axios interceptor: injeta token + trata 401 (redirect para login).
- Pinia `authStore` (token, user, perfil).
- Vue Router guard por auth e por role (Admin/Cliente).
- TailwindCSS para velocidade de desenvolvimento.

### 15.3 Regras de navegação

- Guard de rota exigindo token válido.
- Menus e rotas condicionados por `role`.
- Rotas de Admin inacessíveis para Cliente.
- Telas de Cliente exibem botões de criar/editar/excluir para endereços, contatos e pets; atendimentos são somente leitura.

### 15.4 Design System (Design Tokens)

#### Paleta de cores (Tailwind Config)

| Token | Cor Tailwind | Uso |
|-------|-------------|-----|
| **Primary (Brand)** | `indigo-600` | Botões principais, links, estados ativos, foco |
| **Secondary (Accent)** | `orange-500` | Badges de pets, CTAs secundários |
| **Neutral (Surface/Text)** | `slate-50` a `slate-900` | Backgrounds (`50`), títulos (`900`), textos secundários (`500`) |
| **Success** | `emerald-500` | Operações concluídas |
| **Error** | `rose-600` | Erros de validação, ações destrutivas |
| **Warning** | `amber-500` | Alertas de sistema |
| **Info** | `sky-500` | Status neutros |

#### Tipografia

- **Font Family**: `Inter` (Google Fonts).
- **Escala**: `text-xs`/`text-sm` (legendas, badges) → `text-base` (corpo, inputs) → `text-lg`/`text-xl` (títulos de card) → `text-2xl`/`text-3xl` (cabeçalhos de página).

#### Formas e espaçamento

- **Bordas**: `rounded-lg` (8px) para componentes padrão; `rounded-xl` (12px) para cards e modais.
- **Sombras**: `shadow-sm` (inputs, cards); `shadow-lg` (modais, dropdowns).
- **Espaçamento**: múltiplos de 4 (padrão Tailwind), layouts com respiro (`p-4` a `p-8`).

### 15.5 Biblioteca de Componentes (Atomic Design)

Componentes estilizados com `cva` (Class Variance Authority) para variantes consistentes.

#### Átomos

| Componente | Especificação |
|------------|---------------|
| **Button** | Variantes: `primary` (indigo), `secondary` (outline), `ghost`, `danger` (rose). Tamanhos: `sm`, `md`, `lg`. Estados: `loading`, `disabled`. |
| **Input / Textarea** | Borda `slate-300`, foco `ring-2 ring-indigo-500`. Suporte a ícones. Estado de erro com borda vermelha + texto de ajuda. |
| **Badge** | Pílulas `rounded-full`. Variantes: `outline`, `solid`, `subtle`. |
| **Avatar** | Imagem circular com fallback para iniciais do nome. |
| **Icon** | Wrapper para `lucide-vue-next`. |

#### Moléculas

| Componente | Especificação |
|------------|---------------|
| **FormGroup** | Label + Input + ErrorMessage (integrado a validação). |
| **SearchInput** | Input com ícone de lupa e botão de limpar. |
| **Toast / Alert** | Notificações flutuantes (sucesso/erro) com auto-dismiss. |
| **Dropdown Menu** | Ações contextuais por linha (editar, excluir). |

#### Organismos

| Componente | Especificação |
|------------|---------------|
| **DataTable** | Tabela responsiva com cabeçalho ordenável, paginação no rodapé, coluna de ações. |
| **Modal (Dialog)** | Overlay com `backdrop-blur-sm`. Cabeçalho, corpo scrollável, rodapé com ações. |
| **Sidebar Navigation** | Links com ícones. Estado ativo: `bg-indigo-50 text-indigo-600`. Responsivo (drawer no mobile). |

### 15.6 Estrutura de componentes

```
src/components/
├── ui/             # Átomos genéricos (Button, Input, Badge, Avatar)
├── shared/         # Moléculas globais (Navbar, Sidebar, Toast)
└── domain/         # Componentes de negócio
    ├── pets/       # PetCard, PetForm
    ├── clients/    # ClientList, ClientForm
    └── ...
```

---

## 16. Estratégia de Testes

### 16.1 Backend (pytest) — obrigatório

- **Unit tests** nos use cases com repositórios fake/mocks (sem DB).
- Cobertura mínima:
  - Login: sucesso + senha inválida + CPF inexistente.
  - RBAC: Admin acessa tudo; Cliente bloqueado em endpoints Admin-only.
  - Ownership: Cliente não acessa dados de outro cliente → 403.
  - Permissão: Cliente não pode criar/alterar/excluir atendimentos → 403.
  - CRUD: fluxos principais de cada entidade.

### 16.2 Frontend (Vitest)

- `authStore`: login, logout, persistência de token.
- Router guards: redirecionamento por auth e role.
- (Opcional) Teste de componente simples.

---

## 17. Documentação e DX

### 17.1 Swagger/OpenAPI

- FastAPI expõe `/docs` e `/openapi.json` automaticamente.
- Nginx encaminha `/docs` e `/openapi.json` para o backend.
- README deve explicar como usar o botão **Authorize** no Swagger.

### 17.2 `help.md` (desejável do PDF)

Conteúdo mínimo:

- Como subir o ambiente (`docker compose up --build` ou `make up`).
- URLs disponíveis: `/`, `/docs`, `/api/v1/health`.
- Credenciais do seed (admin padrão).
- Como rodar migrations.
- Como rodar testes.
- Como autenticar no Swagger.

### 17.3 Makefile (DX)

| Comando | Ação |
|---------|------|
| `make up` | Sobe todos os containers |
| `make down` | Derruba todos os containers |
| `make logs` | Mostra logs |
| `make migrate` | `alembic upgrade head` |
| `make api-format` | `ruff format . && ruff check . --fix` |
| `make api-lint` | `ruff check .` |
| `make api-test` | `pytest` |
| `make web-test` | `vitest` |
| `make test` | Roda todos os testes (backend + frontend) |

### 17.4 Comandos uv (local, dentro de `apps/api/`)

```bash
uv sync --dev              # Instala dependências
uv run ruff format .       # Formata código
uv run ruff check . --fix  # Lint com auto-fix
uv run pytest              # Testes
```

---

## 18. Plano de Execução (fases)

### Fase 1 — Bootstrap "clone & run"

**Objetivo**: `docker compose up --build` e tudo acessível.

- Criar estrutura do monorepo.
- Criar `.env.example` (DB + JWT).
- Criar `docker-compose.yml` (db + api + web + nginx).
- Criar `nginx.conf` com rotas `/`, `/api/v1`, `/docs`, `/openapi.json`.
- Backend: `GET /api/v1/health`.
- Frontend: build e servir.

**Commits**: `chore: bootstrap monorepo and compose stack`, `feat(api): add health endpoint`, `chore(infra): add nginx gateway routes`

### Fase 2 — Banco + Alembic + Models

- SQLAlchemy async (engine/session).
- Alembic async + migration inicial com todas as tabelas.
- Seed admin + breeds.

**Commits**: `feat(api): add db setup and alembic migrations`, `chore(api): seed admin and initial breeds`

### Fase 3 — Auth JWT + RBAC + Ownership

- Hash com bcrypt.
- `POST /api/v1/auth/login`.
- Guards por roles.
- Ownership checks.
- Testes de auth/RBAC/ownership.

**Commits**: `feat(api): implement jwt auth with cpf username`, `feat(api): add rbac and ownership guards`, `test(api): cover auth and rbac rules`

### Fase 4 — CRUDs essenciais

- Users (Admin: CRUD completo).
- Clients (Admin: CRUD completo + Cliente: GET/PATCH `/me`).
- Addresses (Admin: CRUD + Cliente: CRUD próprios).
- Contacts (Admin: CRUD + Cliente: CRUD próprios).
- Breeds (Admin: CRUD + Cliente: GET).
- Pets (Admin: CRUD + Cliente: CRUD próprios).
- Appointments (Admin: CRUD + Cliente: GET de seus pets).

**Commits**: `feat(api): implement users endpoints`, `feat(api): implement clients endpoints`, `feat(api): implement addresses and contacts endpoints`, `feat(api): implement breeds endpoints`, `feat(api): implement pets endpoints`, `feat(api): implement appointments endpoints`

### Fase 5 — Desejáveis

- Upload de foto (cliente/pet).
- `GET /api/v1/metrics`.

**Commits**: `feat(api): add photo upload for pets and clients`, `feat(api): add heartbeat and metrics endpoint`

### Fase 6 — Frontend

- Login + guards + telas.
- Fluxo Cliente (perfil, endereços, contatos, pets, atendimentos).
- Fluxo Admin (clientes, raças, pets, atendimentos).

**Commits**: `feat(web): implement auth flow`, `feat(web): add client screens`, `feat(web): add admin screens`

### Fase 7 — Entrega final

- README impecável.
- `help.md` completo.
- Checklist final + seed demo.

**Commits**: `docs: add readme and help usage guide`, `chore: polish docker and demo seed`

---

## 19. Critérios de Aceite (DoD)

### 19.1 Infraestrutura

- [ ] `docker compose up --build` sobe sem erro.
- [ ] `http://localhost` abre o frontend.
- [ ] `http://localhost/docs` abre o Swagger.
- [ ] `http://localhost/api/v1/health` retorna OK.

### 19.2 Segurança e acesso

- [ ] Login com CPF + senha gera JWT válido.
- [ ] JWT autoriza no Swagger (botão Authorize).
- [ ] Admin faz CRUD completo em todos os recursos.
- [ ] Cliente consegue CRUD de endereços, contatos e pets próprios.
- [ ] Cliente consegue apenas READ de atendimentos dos seus pets.
- [ ] Cliente **não** consegue criar/alterar/excluir atendimentos → 403.
- [ ] Cliente não acessa dados de outro cliente → 403.

### 19.3 Testes

- [ ] pytest: login ok/falha, RBAC, ownership, permissões, CRUD.
- [ ] Vitest: guard de rotas, authStore.

### 19.4 Documentação

- [ ] `help.md` presente e útil.
- [ ] README com instruções claras.
- [ ] Swagger navegável.

### 19.5 Desejáveis

- [ ] Métricas/heartbeat funcionando.
- [ ] Upload de fotos funcionando.

---

## 20. Riscos e Decisões

| # | Risco / Decisão | Posição adotada |
|---|-----------------|-----------------|
| 1 | **Fonte única de identidade (CPF)** | `users.cpf` é a única fonte de login; `clients` não armazena CPF para evitar redundância e inconsistência. |
| 2 | **Política de erro ownership** | Retornar **403 Forbidden** (mais didático para avaliação do desafio). |
| 3 | **ID surrogate vs CPF como PK de User** | Usar `id` surrogate (UUID/int) como PK + `cpf` como UNIQUE index. |
| 4 | **Escopo de permissões do Cliente** | Permissões granulares: CRUD completo para endereços, contatos e pets próprios; somente leitura para atendimentos. |
| 5 | **Prefixo de API** | `/api/v1` para demonstrar versionamento. |
| 6 | **Armazenamento de fotos** | Disco local com volume Docker (simples e adequado para desafio). |
| 7 | **Versão Python** | 3.13.9 fixa, conforme definição do projeto. |
