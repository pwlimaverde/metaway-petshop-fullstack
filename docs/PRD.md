# PRD — metaway-petshop-fullstack (Desafio Técnico Metaway)

> Documento de requisitos para iniciar a construção do sistema **Petshop** em **Monorepo** (Backend **FastAPI/Python 3.11+** + Frontend **Vue 3/TypeScript**) com **PostgreSQL** e **Docker Compose** em execução com **um comando**.

---

## 1. Visão do Produto
Sistema web + API para gestão de **clientes**, **pets**, **raças** e **atendimentos** de um petshop, com autenticação e autorização por perfil (**RBAC**) e regra de propriedade (**ownership**), garantindo que:

- **Admin** tem acesso total (CRUD irrestrito).
- **Cliente** acessa/edita **somente seus dados** e **os de seus pets** (incluindo atendimentos vinculados aos seus pets).

---

## 2. Objetivos

### 2.1 Objetivos do desafio
- Demonstrar entrega end-to-end: **API + UI + DB + Docker**.
- Aplicar boas práticas (Clean Architecture leve, testes, documentação).
- Garantir segurança básica (hash de senha, JWT, RBAC).

### 2.2 Objetivos do produto (MVP)
- Autenticar usuários usando **CPF como username**.
- Permitir que Admin gerencie todo o cadastro (clientes, pets, raças, atendimentos).
- Permitir que Cliente gerencie seu perfil e seus pets, e consulte atendimentos relacionados.

---

## 3. Escopo (MVP — Apenas o necessário)

### 3.1 Funcionalidades obrigatórias
- Autenticação:
  - Login por **CPF + senha** e retorno de **JWT**.
- Autorização:
  - RBAC para **Admin** e **Cliente**.
  - Ownership: Cliente só acessa recursos vinculados ao seu cadastro.
- Cadastros e operações:
  - **Usuários** (Admin/Cliente) — criação e gestão por Admin.
  - **Clientes** — CRUD por Admin; Cliente acessa/edita apenas seus próprios dados.
  - **Endereços** do cliente — CRUD seguindo RBAC/ownership.
  - **Contatos** do cliente — CRUD seguindo RBAC/ownership.
  - **Raças** — CRUD por Admin; leitura por Cliente.
  - **Pets** — CRUD por Admin; Cliente CRUD apenas dos seus pets.
  - **Atendimentos** — CRUD por Admin; Cliente acessa atendimentos dos seus pets.
- Documentação:
  - Swagger/OpenAPI via FastAPI em `/docs`.
- Testes:
  - **pytest** no backend e **Vitest** no frontend.

### 3.2 Melhorias permitidas (apenas as necessárias para qualidade do desafio)
Estas melhorias **não alteram escopo de negócio**, mas aumentam qualidade/avaliação:
- Logs estruturados (mínimo) e tratamento consistente de erros (HTTP 400/401/403/404).
- Healthcheck (`GET /health`) para orquestração no Docker.
- Seed opcional de dados mínimos (Admin inicial) via variável de ambiente para facilitar avaliação.
- Padronização de lint/format (ex.: Ruff/Black no backend; ESLint/Prettier no frontend) **somente se não atrasar**.

---

## 4. Perfis, Permissões e Regras de Acesso

### 4.1 Perfis
- **Admin**
  - Acesso total ao sistema (CRUD irrestrito).
- **Cliente**
  - Acesso apenas aos próprios dados e dados relacionados aos próprios pets.

### 4.2 Regras de ownership (críticas)
- Cliente só pode:
  - Ler/editar **seu cadastro**.
  - CRUD em **endereços** e **contatos** **do seu client_id**.
  - CRUD em **pets** que pertencem ao seu `client_id`.
  - Acessar atendimentos vinculados aos seus pets.
- Validação obrigatória:
  - Em operações com `pet_id`, verificar que `pet.client_id == current_user.client_id`.
  - Em operações com `appointment_id`, verificar que o pet do atendimento pertence ao cliente.

---

## 5. Requisitos Funcionais (RF)

### RF-01 — Login (CPF como username)
- Entrada: CPF (apenas dígitos ou formato com máscara aceito) + senha.
- Saída: JWT (`access_token`) e `token_type=bearer`.
- Falhas:
  - Credenciais inválidas → 401.

### RF-02 — Emissão e validação de JWT
- JWT deve conter no mínimo:
  - `sub`: id do usuário
  - `role`: ADMIN | CLIENTE
  - `client_id`: se perfil CLIENTE, obrigatório; se ADMIN, pode ser null
  - `exp`: expiração
- API deve validar token em rotas protegidas.

### RF-03 — Gestão de Usuários (Admin)
- Admin pode:
  - Criar usuário (CPF único, senha, perfil).
  - Listar usuários.
  - Visualizar usuário específico.
  - Atualizar dados básicos e perfil (quando aplicável).
- Cliente **não** pode gerenciar usuários.

### RF-04 — Cliente (dados cadastrais)
- Admin:
  - CRUD completo de clientes.
- Cliente:
  - `GET /clients/me` para consultar seus dados.
  - `PATCH /clients/me` para editar seus dados.

### RF-05 — Endereços do Cliente
- Admin:
  - CRUD de endereços de qualquer cliente.
- Cliente:
  - CRUD apenas dos próprios endereços.
- Campos mínimos:
  - `logradouro`, `cidade`, `bairro`, `complemento` (opcional), `tag` (ex.: casa/trabalho).

### RF-06 — Contatos do Cliente
- Admin:
  - CRUD de contatos de qualquer cliente.
- Cliente:
  - CRUD apenas dos próprios contatos.
- Campos mínimos:
  - `tag`, `tipo` (email/telefone), `valor`.

### RF-07 — Raças
- Admin:
  - CRUD de raças.
- Cliente:
  - Apenas leitura/listagem.
- Campos mínimos:
  - `descricao`.

### RF-08 — Pets
- Admin:
  - CRUD total.
- Cliente:
  - CRUD apenas dos seus pets.
- Campos mínimos:
  - `client_id`, `breed_id`, `data_nascimento`, `nome`.

### RF-09 — Atendimentos
- Admin:
  - CRUD total.
- Cliente:
  - Acessa atendimentos **apenas dos seus pets** (ownership).
- Campos mínimos:
  - `pet_id`, `descricao`, `valor`, `data`.

---

## 6. Requisitos Não Funcionais (RNF)

### RNF-01 — Stack (imutável)
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 Async, Alembic.
- **DB**: PostgreSQL.
- **Frontend**: Vue 3 (Composition API) + TypeScript + Pinia + Vue Router + TailwindCSS.
- **Infra**: Docker Compose.
- **Gerenciamento Python**: **uv** (Astral) para dependências/venv e builds rápidos.

### RNF-02 — Arquitetura (Clean Architecture leve)
Separação obrigatória:
1. **Domain**: entidades/regras puras.
2. **Application**: casos de uso (orquestração).
3. **Infra**: repositórios SQLAlchemy, DB config, auth JWT, adapters.
4. **Interfaces**: routers FastAPI, schemas DTO.

### RNF-03 — Segurança básica
- Senhas armazenadas com hash (bcrypt via passlib).
- JWT com expiração.
- CPF como username obrigatório e **único**.
- Respostas de erro padronizadas.

### RNF-04 — Testabilidade
- Backend: pytest cobrindo autenticação, RBAC e ownership.
- Frontend: Vitest cobrindo stores e guard de rotas.

### RNF-05 — One command (DX)
- Subir ambiente com:
  - `docker compose up --build`
- Componentes devem se descobrir via network do Compose.
- Documentação de execução no README.

---

## 7. Modelo de Dados (alto nível)

### 7.1 Entidades e relacionamentos
- **User**
  - `id`
  - `cpf` (unique)
  - `name`
  - `role` (ADMIN | CLIENTE)
  - `password_hash`
  - `client_id` (nullable para ADMIN; obrigatório para CLIENTE)
- **Client**
  - `id`
  - `name`
  - `cpf` (opcional aqui; se existir, unique e consistente com user)
  - `created_at`
- **Address**
  - `id`
  - `client_id` (FK)
  - `logradouro`, `cidade`, `bairro`, `complemento`, `tag`
- **Contact**
  - `id`
  - `client_id` (FK)
  - `tag`, `tipo`, `valor`
- **Breed**
  - `id`
  - `descricao`
- **Pet**
  - `id`
  - `client_id` (FK)
  - `breed_id` (FK)
  - `data_nascimento`
  - `nome`
- **Appointment (Atendimento)**
  - `id`
  - `pet_id` (FK)
  - `descricao`
  - `valor`
  - `data`

### 7.2 Restrições importantes
- `User.cpf` deve ser único.
- Se `Client.cpf` existir, deve ser único e consistente com `User.cpf` do perfil CLIENTE.
- `Pet.client_id` obrigatório.
- `Appointment.pet_id` obrigatório.
- Ownership deve ser garantido no backend (não apenas no frontend).

---

## 8. Contrato de API (alto nível)

**Prefixo**: `/api/v1`

### 8.1 Auth
- `POST /auth/login`

### 8.2 Users (Admin)
- `POST /users`
- `GET /users`
- `GET /users/{id}`
- `PATCH /users/{id}`

### 8.3 Clients
- Admin:
  - `POST /clients`
  - `GET /clients`
  - `GET /clients/{id}`
  - `PATCH /clients/{id}`
  - `DELETE /clients/{id}`
- Cliente:
  - `GET /clients/me`
  - `PATCH /clients/me`

### 8.4 Addresses
- `GET /clients/{client_id}/addresses`
- `POST /clients/{client_id}/addresses`
- `PATCH /addresses/{id}`
- `DELETE /addresses/{id}`

### 8.5 Contacts
- `GET /clients/{client_id}/contacts`
- `POST /clients/{client_id}/contacts`
- `PATCH /contacts/{id}`
- `DELETE /contacts/{id}`

### 8.6 Breeds
- `GET /breeds`
- Admin:
  - `POST /breeds`
  - `PATCH /breeds/{id}`
  - `DELETE /breeds/{id}`

### 8.7 Pets
- `GET /pets` (admin vê tudo; cliente vê só os seus)
- `POST /pets`
- `GET /pets/{id}`
- `PATCH /pets/{id}`
- `DELETE /pets/{id}`

### 8.8 Appointments
- `GET /appointments` (admin: tudo; cliente: só dos seus pets)
- `POST /appointments`
- `GET /appointments/{id}`
- `PATCH /appointments/{id}`
- `DELETE /appointments/{id}`

### 8.9 Healthcheck (melhoria necessária)
- `GET /health`

---

## 9. Requisitos de UI (Frontend) — MVP

### 9.1 Telas mínimas
- Login (CPF + senha)
- Dashboard simples (boas-vindas + perfil)
- Pets:
  - Lista
  - Criar/editar/excluir (conforme permissões)
- Atendimentos:
  - Lista (filtrada por permissões)
  - Criar/editar/excluir (conforme permissões)
- Admin:
  - Clientes (lista + edição)
  - Raças (CRUD)

### 9.2 Regras de navegação
- Guard de rota exigindo token válido.
- Menus e rotas condicionados por `role`.

---

## 10. Critérios de Aceite (DoD)

### 10.1 Entrega
- `docker compose up --build` sobe:
  - PostgreSQL
  - Backend (API) com `/docs` e `/health`
  - Frontend (web) consumindo API

### 10.2 Segurança e acesso
- CPF usado como username no login.
- Admin consegue CRUD de todos os recursos.
- Cliente:
  - Consegue acessar e editar `clients/me`
  - Consegue CRUD apenas dos seus pets/endereços/contatos
  - Não consegue acessar recursos de outros clientes (retorno 403 ou 404 conforme política)
- JWT obrigatório em rotas protegidas.

### 10.3 Testes
- Backend (pytest):
  - teste de login (sucesso e falha)
  - teste RBAC (cliente bloqueado em endpoints admin)
  - teste ownership (cliente não acessa pet/atendimento de outro cliente)
- Frontend (Vitest):
  - guard de rotas
  - store de auth (login/logout)

### 10.4 Documentação
- README com:
  - comando único para rodar
  - variáveis de ambiente
  - como executar migrations
  - como rodar testes

---

## 11. Plano de Execução (MVP em marcos)
1. **Fundação**
   - Monorepo + Docker Compose + healthcheck + docs.
2. **Persistência**
   - Modelos SQLAlchemy async + Alembic + migration inicial.
3. **Auth**
   - login CPF + senha (hash) + JWT.
4. **RBAC + Ownership**
   - Guards/dependencies e validações nos casos de uso.
5. **CRUDs essenciais**
   - Breeds, Clients (me/admin), Addresses, Contacts, Pets, Appointments.
6. **Testes + README**
   - pytest + Vitest, documentação e comandos.

---

## 12. Riscos e decisões (registro)
- **Consistência CPF**: preferir fonte única em `User.cpf` (login). Se o desafio exigir CPF em `Client`, manter restrição e garantir consistência com o usuário cliente.
- **Política de erro ownership**: retornar 403 (mais claro para avaliação) ou 404 (evita enumeração). Para desafio, 403 costuma ser mais didático.
