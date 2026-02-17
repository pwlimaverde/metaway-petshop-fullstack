# Help — Metaway Petshop Fullstack

## 0. Versionamento (fonte única)

A versão do monorepo é centralizada no arquivo `VERSION` (raiz do projeto).

- Release atual: `v1.0.0` (`VERSION=1.0.0`).
- Formato esperado no arquivo `VERSION`: `MAJOR.MINOR.PATCH` (sem prefixo `v`).
- Não altere versão manualmente em `pyproject.toml`, `package.json`, `package-lock.json` ou `main.py`.
- Esses arquivos são sincronizados automaticamente por `scripts/sync_version.py`.

Fluxo recomendado para nova release:

```bash
# 1) editar somente o arquivo VERSION (ex.: 1.1.0)
make sync-version
# 2) revisar alterações geradas
git diff
# 3) commitar e criar tag da release
git tag -a v<versao> -m "release v<versao>"
```

## 1. Configuração Inicial (Faça isso primeiro!) 🛠️

Antes de rodar qualquer automação, você precisa preparar o ambiente.

### Passo 1: Criar o arquivo `.env`

Na raiz do projeto, crie uma cópia do arquivo de exemplo `.env.example` e renomeie para `.env`.

**Via terminal:**

- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / Mac (Bash):**
  ```bash
  cp .env.example .env
  ```

_(Ou copie e cole manualmente se preferir)_

### Passo 2: Escolher o Modo de Execução (Local vs Remoto)

Abra o arquivo `.env` recém-criado e verifique a variável `DOCKER_HOST`.

- **Opção A: Rodar Localmente (Padrão)** 🏠
  Se você quer rodar o projeto na sua própria máquina.
  **Ação:** Mantenha a linha `DOCKER_HOST` **comentada (#)** ou vazia.

  ```ini
  # DOCKER_HOST=ssh://...
  ```

- **Opção B: Rodar em Servidor Remoto (VPS)** ☁️
  Se você quer comandar o deploy da sua máquina, mas rodar os containers em um servidor.
  **Ação:** Descomente e aponte para seu alias SSH configurado.
  ```ini
  DOCKER_HOST=ssh://seu-alias-ssh
  ```
  > _Precisa de ajuda para configurar o SSH? Veja a seção [Guia Avançado: Deploy Remoto](#guia-avancado-deploy-remoto-via-ssh) no final deste arquivo._

---

## 2. Setup Automatizado (Start!) 🚀

Com o `.env` configurado, inicialize o projeto. O script abaixo cuida de tudo: verifica ferramentas, instala o que falta e sobe os containers.

> **Ferramentas que serão verificadas e instaladas automaticamente:**
>
> | Ferramenta  | Finalidade                                | Instalador usado                                             |
> | :---------- | :---------------------------------------- | :----------------------------------------------------------- |
> | **Docker**  | Rodar os containers (obrigatório)         | Verificação apenas — deve ser instalado antes                |
> | **uv**      | Gerenciador Python (lint, testes backend) | Script oficial da Astral                                     |
> | **Node.js** | Testes e lint do frontend                 | winget (Windows) / brew (Mac) / apt (Linux)                  |
> | **make**    | Atalhos de Makefile                       | winget ou choco (Windows) / xcode-select (Mac) / apt (Linux) |
>
> Se alguma instalação falhar (ex: sem permissão de admin), o script exibe o comando manual e continua normalmente. Pode ser necessário **reiniciar o terminal** após instalações.

### 🪟 Windows (PowerShell)

```powershell
.\infra\scripts\setup.ps1
```

### 🐧 Linux / 🍎 Mac (Bash)

```bash
chmod +x infra/scripts/setup.sh
./infra/scripts/setup.sh
```

**O que este comando faz?**

1. **Ferramentas de Dev:** Verifica `uv`, `Node.js` e `make` — instala automaticamente o que estiver faltando.
2. **Configuração (`.env`):** Cria o arquivo `.env` (se não existir) a partir de `.env.example` e carrega as variáveis.
3. **Docker Remoto:** Se `DOCKER_HOST` estiver definido, configura a conexão SSH.
4. **Verificação de Saúde:** Confere se o Docker está rodando e acessível.
5. **Deploy:** Constrói as imagens (`docker compose build`) e sobe os containers (`docker compose up -d`).

---

## 3. Comandos do Dia a Dia

Todos os comandos abaixo devem ser executados **a partir da raiz do projeto**.

### 📋 Makefile (Atalhos Rápidos)

O jeito mais simples de rodar qualquer operação. Requer `make` instalado.

| Comando               | Descrição                                       |
| :-------------------- | :---------------------------------------------- |
| `make up`             | Build e start de todos os serviços (Docker)     |
| `make down`           | Para e remove os containers                     |
| `make logs`           | Acompanha os logs em tempo real                 |
| `make build`          | Build de todas as imagens Docker                |
| `make rebuild-web`    | Rebuild e start apenas do serviço `web`         |
| `make rebuild-api`    | Rebuild e start apenas do serviço `api`         |
| `make rebuild-front`  | Alias para `make rebuild-web`                   |
| `make rebuild-back`   | Alias para `make rebuild-api`                   |
| `make migrate`        | Executa as migrations (Alembic upgrade head)    |
| `make seed`           | Executa seed de demonstração no container da API |
| `make sync-version`   | Propaga versão do arquivo `VERSION` para manifests |
| `make makemigrations` | Gera nova revision Alembic com nome automático (`auto_YYYYMMDD_HHMMSS`) |
| `make api-lint`       | Lint do backend (Ruff, local via uv)            |
| `make api-format`     | Formatação e auto-fix do backend (local via uv) |
| `make api-test`       | Testes do backend (pytest, local via uv)        |
| `make web-lint`       | Lint do frontend (ESLint, local via npm)        |
| `make web-format`     | Verificação de formatação (Prettier, local via npm) |
| `make web-test`       | Testes do frontend (Vitest, local via npm)      |
| `make lint`           | Lint completo (backend + frontend)              |
| `make format`         | Formatação completa (backend + frontend)        |
| `make test`           | Testes completos (backend + frontend)           |

### 🐍 Backend (Local, sem Docker)

Requer [uv](https://github.com/astral-sh/uv) instalado. Útil para feedback rápido sem subir containers.

```bash
# Testes
uv run --directory apps/api pytest
uv run --directory apps/api pytest --cov=metaway_api --cov-report=term-missing

# Lint (verificação)
uv run --directory apps/api ruff check .

# Formatação + auto-fix
uv run --directory apps/api ruff format .
uv run --directory apps/api ruff check . --fix
```

### ⚛️ Frontend (Local, sem Docker)

Requer [Node.js](https://nodejs.org/) 20+. Todos os comandos rodam da **raiz do projeto** usando `--prefix`.

```bash
# Dev server (hot reload)
npm --prefix apps/web run dev

# Testes
npm --prefix apps/web run test

# Lint (ESLint)
npm --prefix apps/web run lint

# Verificação de formatação (Prettier)
npm --prefix apps/web run format

# Build de produção
npm --prefix apps/web run build
```

### 🐳 Docker Compose (Via Wrapper)

Para compatibilidade com deploy remoto (SSH), use os scripts wrapper que carregam `.env` automaticamente.

| Ação                    | Windows (PowerShell)                      | Linux / Mac (Bash)                       |
| :---------------------- | :---------------------------------------- | :--------------------------------------- |
| Ver logs (geral)        | `.\infra\scripts\compose.ps1 logs -f`     | `./infra/scripts/compose.sh logs -f`     |
| Ver logs (apenas API)   | `.\infra\scripts\compose.ps1 logs -f api` | `./infra/scripts/compose.sh logs -f api` |
| Reiniciar tudo          | `.\infra\scripts\setup.ps1`               | `./infra/scripts/setup.sh`               |
| Derrubar containers     | `.\infra\scripts\compose.ps1 down`        | `./infra/scripts/compose.sh down`        |
| Resetar banco (volumes) | `.\infra\scripts\compose.ps1 down -v`     | `./infra/scripts/compose.sh down -v`     |

> **Nota:** Se preferir rodar `docker compose` manualmente, configure `DOCKER_HOST` no terminal antes, caso use conexão remota.

### ✅ Verificação Completa (Antes de Commit)

Rode lint e testes de ambos os projetos para garantir que tudo está OK.

**Via Makefile (Docker):**

```bash
make lint && make test
```

**Via local (sem Docker):**

```bash
uv run --directory apps/api ruff check . && uv run --directory apps/api pytest && npm --prefix apps/web run lint && npm --prefix apps/web run test
```

---

## 4. Troubleshooting

### "Error response from daemon" ou "docker not found"

- **Local:** O Docker Desktop está rodando?
- **Remoto:** A conexão SSH está funcionando sem senha? Teste `ssh seu-alias`.

### "Error during connect: open //./pipe/dockerDesktopLinuxEngine" (Windows)

Este erro significa que o **Docker Desktop** não está rodando no seu computador.
**Solução:** Abra o aplicativo Docker Desktop e aguarde o ícone 🐳 ficar verde/parar de animar na barra de tarefas.

### "Postgres connection failed"

Aguarde alguns segundos. O banco de dados leva um tempo para iniciar na primeira vez.

### Permissão negada (`./infra/scripts/setup.sh`)

Rode: `chmod +x infra/scripts/setup.sh`

---

## Pré-requisitos

| Ferramenta                                  | Versão mínima | Obrigatório? |
| :------------------------------------------ | :------------ | :----------- |
| [Docker + Compose](https://www.docker.com/) | latest        | Sim          |
| [uv](https://docs.astral.sh/uv/)            | latest        | Dev local    |
| [Node.js + npm](https://nodejs.org/)        | 20+           | Dev local    |
| [make](https://www.gnu.org/software/make/)  | qualquer      | Recomendado  |

> **Nota:** Docker é obrigatório para rodar o projeto. `uv`, `Node.js` e `make` são necessários apenas para desenvolvimento local (testes, lint, formatação).

### Instalação Rápida das Ferramentas de Dev

**uv** (gerenciador Python):

- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Linux / Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Node.js 20+:**

- Windows: `winget install OpenJS.NodeJS.LTS`
- Mac: `brew install node@20`
- Linux: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs`

**make:**

- Windows (com Chocolatey): `choco install make`
- Windows (com winget): `winget install GnuWin32.Make`
- Mac: `xcode-select --install`
- Linux (Debian/Ubuntu): `sudo apt install make`

> O script de setup (`setup.ps1` / `setup.sh`) **instala automaticamente** as ferramentas que faltam. Caso a instalação automática falhe (por ex. falta de permissão), ele exibe o comando manual correspondente. Pode ser necessário reiniciar o terminal após a instalação.

---

## Acessos

### Via Gateway (Nginx — Docker)

Quando os containers estão rodando (`make up`), tudo é acessível por uma única porta:

| Serviço          | URL                              | Descrição                      |
| :--------------- | :------------------------------- | :----------------------------- |
| **Frontend**     | `http://localhost`               | Aplicação Vue                  |
| **Swagger API**  | `http://localhost/docs`          | Documentação interativa da API |
| **Healthcheck**  | `http://localhost/api/v1/health` | Verificação de saúde           |
| **OpenAPI JSON** | `http://localhost/openapi.json`  | Especificação OpenAPI          |

### Acesso Direto (Dev Local, sem Nginx)

| Serviço         | URL                                   | Descrição                       |
| :-------------- | :------------------------------------ | :------------------------------ |
| **Frontend**    | `http://localhost:5173`               | Dev server Vite (`npm run dev`) |
| **Swagger API** | `http://localhost:8000/docs`          | API rodando via uvicorn         |
| **Healthcheck** | `http://localhost:8000/api/v1/health` | Verificação de saúde            |

### Login na API

1. Acesse Swagger (`/docs`) e execute `POST /api/v1/auth/login` com:
   - `username`: CPF (somente dígitos)
   - `password`: senha
2. Copie o `access_token` da resposta.
3. Clique em **Authorize** e informe: `Bearer <access_token>`

**Usuário Admin (Seed):**
CPF e Senha estão definidos no `.env` (variáveis `ADMIN_SEED_CPF` e `ADMIN_SEED_PASSWORD`). Altere-os antes do primeiro deploy.

---

## Guia Avançado: Deploy Remoto (Via SSH)

Para conectar seu Docker local a um servidor remoto, siga estes passos.

**Pré-requisito:** Autenticação SSH por chave pública configurada (sem senha).

**1. Configure seu SSH Local (`~/.ssh/config`)**
Edite (ou crie) o arquivo `C:\Users\SEU_USUARIO\.ssh\config` (Windows) ou `~/.ssh/config` (Linux/Mac) para criar um alias fácil.

Exemplo genérico:

```ssh-config
Host seu-alias-ssh
    HostName seu-servidor.exemplo.com
    User seu-usuario
    Port 22
    IdentityFile C:/Users/SEU_USUARIO/.ssh/sua_chave_privada
```

**2. Teste a conexão**
No terminal: `ssh seu-alias-ssh`
_Deve conectar imediatamente sem pedir senha._

**3. Configure o `.env`**
Agora aponte o Docker para este alias:

```ini
DOCKER_HOST=ssh://seu-alias-ssh
```

Pronto! Agora todos os comandos `docker compose` (e o script de setup) vão operar no servidor remoto.
