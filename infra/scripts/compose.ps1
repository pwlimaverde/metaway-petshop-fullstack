# compose.ps1 - Wrapper para Docker Compose com carregamento de ambiente
$ErrorActionPreference = "Stop"

# 1. Determina a raiz do projeto
$ScriptDir = $PSScriptRoot
$ProjectRoot = "$ScriptDir/../.."
Push-Location $ProjectRoot

try {
    # 2. Carrega variaveis do .env para a sessao local
    if (Test-Path ".env") {
        Get-Content .env | ForEach-Object {
            if ($_ -match '^([^#=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                # Define a variável apenas para este processo
                [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
            }
        }
    }

    # 3. Executa o Docker Compose com os argumentos passados
    # O comando docker vai usar as variáveis de ambiente carregadas (DOCKER_HOST)
    # E também passamos --env-file para o compose substituir variáveis no yaml
    $DockerArgs = @("--env-file", ".env", "-f", "infra/docker-compose.yml") + $args
    
    # Executa e aguarda
    & docker compose $DockerArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}
