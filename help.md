# Help — Metaway Petshop Fullstack

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

- **Opção B: Rodar em Servidor Remoto (VPS/Hostinger)** ☁️
  Se você quer comandar o deploy da sua máquina, mas rodar os containers em um servidor.
  **Ação:** Descomente e aponte para seu alias SSH configurado.
  ```ini
  DOCKER_HOST=ssh://hostinger-root
  ```
  > _Precisa de ajuda para configurar o SSH? Veja a seção [Guia Avançado: Deploy Remoto](#guia-avancado-deploy-remoto-via-ssh) no final deste arquivo._

---

## 2. Setup Automatizado (Start!) 🚀

Com o `.env` configurado, inicialize o projeto. O script abaixo verifica o Docker, carrega as variáveis e sobe os containers.

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

1. **Configuração Automática (`.env`):** Cria o arquivo `.env` (se não existir) baseado no exemplo e carrega as variáveis de ambiente para a sessão atual.
2. **Setup do Docker Remoto:** Se `DOCKER_HOST` estiver definido, configura a conexão SSH automaticamente.
3. **Verificação de Saúde:** Confere se o Docker está rodando e acessível antes de tentar qualquer comando.
4. **Deploy:** Constrói as imagens (`docker compose build`) e sobe os containers (`docker compose up -d`) garantindo que tudo esteja atualizado.

---

## 3. Comandos do Dia a Dia

Para garantir compatibilidade total (Local e Remoto), **use os scripts wrapper abaixo**. Eles carregam automaticamente as configurações do `.env` (incluindo SSH remoto) antes de executar o comando.

### 🐳 Docker Compose (Via Wrapper)

**Ver logs (Geral)**

- Windows: `.\infra\scripts\compose.ps1 logs -f`
- Linux/Mac: `./infra/scripts/compose.sh logs -f`

**Ver logs (Apenas API)**

- Windows: `.\infra\scripts\compose.ps1 logs -f api`
- Linux/Mac: `./infra/scripts/compose.sh logs -f api`

**Reiniciar tudo (Rebuild)**

- Windows: `.\infra\scripts\setup.ps1`
- Linux/Mac: `./infra/scripts/setup.sh`

**Derrubar containers (Stop & Remove)**

- Windows: `.\infra\scripts\compose.ps1 down`
- Linux/Mac: `./infra/scripts/compose.sh down`

**Resetar banco de dados (Apagar volumes)**

- Windows: `.\infra\scripts\compose.ps1 down -v`
- Linux/Mac: `./infra/scripts/compose.sh down -v`

> **Nota para Especialistas:** Se você preferir rodar `docker compose` manualmente, lembre-se de configurar a variável `DOCKER_HOST` no seu terminal antes de executar, caso esteja usando conexão remota.

### 🐍 Backend (Local)

Requer [uv](https://github.com/astral-sh/uv) instalado. Útil para rodar testes rapidamente sem subir o Docker.

**Rodar testes & Lint**

```bash
uv run --directory apps/api pytest
uv run --directory apps/api ruff check .
```

### ⚛️ Frontend (Local)

Requer Node.js.

```bash
cd apps/web
npx vitest run
npx eslint .
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

| Ferramenta                                     | Versão mínima |
| :--------------------------------------------- | :------------ |
| [Docker + Compose](https://www.docker.com/)    | latest        |
| [uv](https://docs.astral.sh/uv/) _(dev local)_ | latest        |
| [Node.js](https://nodejs.org/) _(dev local)_   | 20+           |

> **Nota:** Docker é obrigatório. `uv` e `Node.js` só são necessários para rodar testes/lint localmente sem Docker.

---

## Acessos

| Serviço         | URL Local                             | URL Remota (Exemplo)      | Credenciais   |
| :-------------- | :------------------------------------ | :------------------------ | :------------ |
| **Swagger API** | `http://localhost:8000/docs`          | `http://SEU_IP:8000/docs` | `/auth/token` |
| **Frontend**    | `http://localhost:80`                 | `http://SEU_IP:80`        | -             |
| **Healthcheck** | `http://localhost:8000/api/v1/health` | `http://SEU_IP:8000/...`  | -             |

**Usuário Admin (Seed):**
CPF e Senha estão definidos no arquivo `.env` (variáveis `ADMIN_SEED_CPF` e `ADMIN_SEED_PASSWORD`). Altere-os antes do primeiro deploy.

---

## Guia Avançado: Deploy Remoto (Via SSH)

Para conectar seu Docker local a um servidor remoto (como Hostinger VPS), siga estes passos únicos.

**Pré-requisito:** Autenticação SSH por chave pública configurada (sem senha).

**1. Configure seu SSH Local (`~/.ssh/config`)**
Edite (ou crie) o arquivo `C:\Users\SEU_USUARIO\.ssh\config` (Windows) ou `~/.ssh/config` (Linux/Mac) para criar um alias fácil.

Exemplo para Hostinger:

```ssh-config
Host hostinger-root
    HostName srv1321059.hstgr.cloud
    User root
    Port 22
    IdentityFile C:/Users/pwlim/.ssh/id_hostinger_root
```

**2. Teste a conexão**
No terminal: `ssh hostinger-root`
_Deve conectar imediatamente sem pedir senha._

**3. Configure o `.env`**
Agora aponte o Docker para este alias:

```ini
DOCKER_HOST=ssh://hostinger-root
```

Pronto! Agora todos os comandos `docker compose` (e o script de setup) vão operar no servidor remoto.
