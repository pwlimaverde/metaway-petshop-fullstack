#!/bin/bash
set -e

# compose.sh - Wrapper para Docker Compose com carregamento de ambiente

# 1. Determina a raiz do projeto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

cd "$PROJECT_ROOT"

# 2. Carrega variáveis do .env (exportando para o shell atual)
if [ -f ".env" ]; then
    while IFS='=' read -r key value; do
        key=$(echo "$key" | xargs)
        [[ -z "$key" || "$key" == \#* ]] && continue
        value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        export "$key=$value"
    done < .env
fi

# 3. Executa o Docker Compose com os argumentos passados
# Usa --env-file para garantir que as variáveis também vão para o compose
docker compose --env-file .env -f infra/docker-compose.yml "$@"
