#!/bin/bash
set -e

# setup.sh - Inicialização do Ambiente Metaway Petshop (Linux/Mac)

# Mudar para a raiz do projeto (2 níveis acima de infra/scripts)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

cd "$PROJECT_ROOT"

echo -e "\033[0;36m--- Inicializando ambiente Metaway Petshop ---\033[0m"
echo -e "\033[0;90mDiretório do projeto: $(pwd)\033[0m"

# Detectar sistema operacional
OS_TYPE="linux"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="mac"
fi

NEEDS_RESTART=false

# 0. Verificar e instalar ferramentas de desenvolvimento
echo -e "\n\033[0;36m>>> Verificando ferramentas de desenvolvimento...\033[0m"

# --- uv ---
if command -v uv &> /dev/null; then
    echo -e "\033[0;32m[OK] uv encontrado: $(uv --version)\033[0m"
else
    echo -e "\033[0;33m[INSTALL] uv não encontrado. Instalando...\033[0m"
    if curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null; then
        # Atualizar PATH para a sessão atual
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        if command -v uv &> /dev/null; then
            echo -e "\033[0;32m[OK] uv instalado: $(uv --version)\033[0m"
        else
            NEEDS_RESTART=true
            echo -e "\033[0;33m[AVISO] uv instalado, mas será disponível após reiniciar o terminal.\033[0m"
        fi
    else
        echo -e "\033[0;33m[AVISO] Falha ao instalar uv. Instale manualmente:\033[0m"
        echo -e "\033[0;90m   curl -LsSf https://astral.sh/uv/install.sh | sh\033[0m"
    fi
fi

# --- Node.js ---
if command -v node &> /dev/null; then
    echo -e "\033[0;32m[OK] Node.js encontrado: $(node --version)\033[0m"
else
    echo -e "\033[0;33m[INSTALL] Node.js não encontrado. Instalando...\033[0m"
    NODE_INSTALLED=false

    if [ "$OS_TYPE" = "mac" ]; then
        if command -v brew &> /dev/null; then
            if brew install node@20 2>/dev/null; then
                NODE_INSTALLED=true
            fi
        else
            echo -e "\033[0;90m   Homebrew não encontrado. Instale via: https://brew.sh\033[0m"
        fi
    else
        # Linux — tentar via package manager
        if command -v apt-get &> /dev/null; then
            if curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null && sudo apt-get install -y nodejs 2>/dev/null; then
                NODE_INSTALLED=true
            fi
        elif command -v dnf &> /dev/null; then
            if sudo dnf install -y nodejs 2>/dev/null; then
                NODE_INSTALLED=true
            fi
        fi
    fi

    if $NODE_INSTALLED && command -v node &> /dev/null; then
        echo -e "\033[0;32m[OK] Node.js instalado: $(node --version)\033[0m"
    else
        NEEDS_RESTART=true
        echo -e "\033[0;33m[AVISO] Falha ao instalar Node.js automaticamente. Instale manualmente:\033[0m"
        if [ "$OS_TYPE" = "mac" ]; then
            echo -e "\033[0;90m   brew install node@20\033[0m"
        else
            echo -e "\033[0;90m   https://nodejs.org/ ou use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash\033[0m"
        fi
    fi
fi

# --- make ---
if command -v make &> /dev/null; then
    echo -e "\033[0;32m[OK] make encontrado.\033[0m"
else
    echo -e "\033[0;33m[INSTALL] make não encontrado. Instalando...\033[0m"
    MAKE_INSTALLED=false

    if [ "$OS_TYPE" = "mac" ]; then
        if xcode-select --install 2>/dev/null; then
            MAKE_INSTALLED=true
        fi
    else
        if command -v apt-get &> /dev/null; then
            if sudo apt-get install -y make 2>/dev/null; then
                MAKE_INSTALLED=true
            fi
        elif command -v dnf &> /dev/null; then
            if sudo dnf install -y make 2>/dev/null; then
                MAKE_INSTALLED=true
            fi
        fi
    fi

    if $MAKE_INSTALLED && command -v make &> /dev/null; then
        echo -e "\033[0;32m[OK] make instalado.\033[0m"
    else
        NEEDS_RESTART=true
        echo -e "\033[0;33m[AVISO] Falha ao instalar make automaticamente. Instale manualmente:\033[0m"
        if [ "$OS_TYPE" = "mac" ]; then
            echo -e "\033[0;90m   xcode-select --install\033[0m"
        else
            echo -e "\033[0;90m   sudo apt install make\033[0m"
        fi
    fi
fi

if $NEEDS_RESTART; then
    echo ""
    echo -e "\033[0;33mAlgumas ferramentas foram instaladas e podem exigir reinício do terminal.\033[0m"
else
    echo -e "\033[0;32m[OK] Todas as ferramentas de desenvolvimento estão disponíveis.\033[0m"
fi

# 1. Verificar e criar .env
echo -e "\n\033[0;36m>>> Verificando configuração de ambiente (.env)...\033[0m"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo -e "\033[0;32m[OK] Arquivo .env criado a partir de .env.example.\033[0m"
        echo -e "\033[0;33mIMPORTANTE: Edite o arquivo .env com suas configurações (especialmente DOCKER_HOST) e rode este script novamente.\033[0m"
        exit 0
    else
        echo -e "\033[0;31m[ERRO] Arquivo .env.example não encontrado na raiz do projeto. Verifique o diretório.\033[0m"
        exit 1
    fi
else
    echo -e "\033[0;32m[OK] Arquivo .env encontrado.\033[0m"
fi

# 2. Carregar variáveis do .env para a sessão atual
echo -e "\n\033[0;36m>>> Carregando variáveis de ambiente...\033[0m"
if [ -f ".env" ]; then
    # Exporta variáveis ignorando comentários e linhas vazias
    while IFS='=' read -r key value; do
        key=$(echo "$key" | xargs)
        [[ -z "$key" || "$key" == \#* ]] && continue
        # Remove aspas envolventes do valor, se houver
        value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        export "$key=$value"
    done < .env
    echo -e "\033[0;32m[OK] Variáveis carregadas.\033[0m"
fi

# 3. Validar conexão Docker
echo -e "\n\033[0;36m>>> Verificando conexão com Docker...\033[0m"

if [ -n "$DOCKER_HOST" ]; then
    echo -e "\033[0;90mConectando ao Docker Host remoto: $DOCKER_HOST\033[0m"
else
    echo -e "\033[0;90mUsando Docker local.\033[0m"
fi

if docker info > /dev/null 2>&1; then
    echo -e "\033[0;32m[OK] Docker conectado e operante.\033[0m"
else
    echo -e "\033[0;31m[ERRO] Falha ao conectar no Docker.\033[0m"
    echo "   Possíveis causas:"
    echo "   1. Docker Desktop não está rodando."
    echo "   2. DOCKER_HOST no .env está incorreto."
    echo "   3. Chave SSH não configurada (para docker remoto)."
    exit 1
fi

# 4. Comandos Docker Compose
echo -e "\n\033[0;36m>>> Subindo a stack (Build + Up)...\033[0m"

# Comando seguro usando --env-file
docker compose --env-file .env -f infra/docker-compose.yml up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n\033[0;36m>>> Status dos Serviços:\033[0m"
    docker compose --env-file .env -f infra/docker-compose.yml ps

    echo -e "\n\033[0;32mSetup concluído com sucesso!\033[0m"
    echo "=============================================="
    echo "Frontend:      http://localhost"
    echo "Swagger API:   http://localhost/docs"
    echo "Healthcheck:   http://localhost/api/v1/health"
    echo "=============================================="
    echo "Comandos úteis:"
    echo "   Logs API:      ./infra/scripts/compose.sh logs -f api"
    echo "   Logs Geral:    ./infra/scripts/compose.sh logs -f"
    echo "   Derrubar:      ./infra/scripts/compose.sh down"
    echo "   Lint + Testes: make lint && make test"
else
    echo -e "\033[0;31m[ERRO] Falha ao subir os containers.\033[0m"
    exit 1
fi
