# setup.ps1 - Inicializacao do Ambiente Metaway Petshop

$ErrorActionPreference = "Stop"

# Mudar para a raiz do projeto (2 niveis acima de infra/scripts)
$ProjectRoot = "$PSScriptRoot/../.."
Push-Location $ProjectRoot

try {
    function Write-Step {
        param([string]$Message)
        Write-Host "`n>>> $Message" -ForegroundColor Cyan
    }

    function Write-Success {
        param([string]$Message)
        Write-Host "[OK] $Message" -ForegroundColor Green
    }

    function Write-ErrorMsg {
        param([string]$Message)
        Write-Host "[ERRO] $Message" -ForegroundColor Red
    }

    Write-Host "--- Inicializando ambiente Metaway Petshop ---" -ForegroundColor Cyan
    Write-Host "Diretorio do projeto: $(Get-Location)" -ForegroundColor Gray

    # 1. Verificar e criar .env
    Write-Step "Verificando configuracao de ambiente (.env)..."
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success "Arquivo .env criado a partir de .env.example."
            Write-Host "IMPORTANTE: Edite o arquivo .env com suas configuracoes (especialmente DOCKER_HOST) e rode este script novamente." -ForegroundColor Yellow
            exit
        }
        else {
            Write-ErrorMsg "Arquivo .env.example nao encontrado na raiz do projeto. Verifique o diretorio."
            exit 1
        }
    }
    else {
        Write-Success "Arquivo .env encontrado."
    }

    # 2. Carregar variaveis do .env para a sessao atual
    Write-Step "Carregando variaveis de ambiente..."
    if (Test-Path ".env") {
        Get-Content .env | ForEach-Object {
            if ($_ -match '^([^#=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
            }
        }
        Write-Success "Variaveis carregadas."
    }

    # 3. Validar conexao Docker
    Write-Step "Verificando conexao com Docker..."
    $dockerHost = [System.Environment]::GetEnvironmentVariable("DOCKER_HOST")
    if (-not [string]::IsNullOrWhiteSpace($dockerHost)) {
        Write-Host "Conectando ao Docker Host remoto: $dockerHost" -ForegroundColor Gray
    }
    else {
        Write-Host "Usando Docker local." -ForegroundColor Gray
    }

    try {
        docker info > $null 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Docker command failed" }
        Write-Success "Docker conectado e operante."
    }
    catch {
        Write-ErrorMsg "Falha ao conectar no Docker."
        Write-Host "   Possiveis causas:"
        Write-Host "   1. Docker Desktop nao esta rodando."
        Write-Host "   2. DOCKER_HOST no .env esta incorreto."
        Write-Host "   3. Chave SSH nao configurada (para docker remoto)."
        exit 1
    }

    # 4. Comandos Docker Compose
    Write-Step "Subindo a stack (Build + Up)..."

    # Comando seguro usando --env-file
    docker compose --env-file .env -f infra/docker-compose.yml up -d --build

    if ($LASTEXITCODE -eq 0) {
        Write-Step "Status dos Servicos:"
        docker compose --env-file .env -f infra/docker-compose.yml ps

        Write-Host "`nSetup concluido com sucesso!" -ForegroundColor Green
        Write-Host "=============================================="
        Write-Host "Swagger API:   http://localhost:8000/docs"
        Write-Host "Healthcheck:   http://localhost:8000/api/v1/health"
        Write-Host "=============================================="
        Write-Host "Comandos uteis:"
        Write-Host "   Logs API:      .\infra\scripts\compose.ps1 logs -f api"
        Write-Host "   Logs Geral:    .\infra\scripts\compose.ps1 logs -f"
        Write-Host "   Derrubar:      .\infra\scripts\compose.ps1 down"
    }
    else {
        Write-ErrorMsg "ERRO ao subir os containers."
        exit 1
    }

}
finally {
    # Retornar ao diretorio original
    Pop-Location
}
