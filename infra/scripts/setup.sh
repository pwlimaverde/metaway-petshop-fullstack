#!/bin/bash
set -e

# setup.sh - Inicialização do Ambiente Metaway Petshop (Linux/Mac)

# Mudar para a raiz do projeto (2 níveis acima de infra/scripts)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

cd "$PROJECT_ROOT"

echo -e "\033[0;36m--- Inicializando ambiente Metaway Petshop ---\033[0m"
echo -e "\033[0;90mDiretório do projeto: $(pwd)\033[0m"

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
    echo "Swagger API:   http://localhost:8000/docs"
    echo "Healthcheck:   http://localhost:8000/api/v1/health"
    echo "=============================================="
    echo "Comandos úteis:"
    echo "   Logs API:      ./infra/scripts/compose.sh logs -f api"
    echo "   Logs Geral:    ./infra/scripts/compose.sh logs -f"
    echo "   Derrubar:      ./infra/scripts/compose.sh down"
else
    echo -e "\033[0;31m[ERRO] Falha ao subir os containers.\033[0m"
    exit 1
fi
