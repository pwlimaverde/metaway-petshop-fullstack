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

    # Helper: atualiza PATH da sessao apos instalacao
    function Refresh-Path {
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }

    # 0. Verificar e instalar ferramentas de desenvolvimento
    Write-Step "Verificando ferramentas de desenvolvimento..."

    $needsRestart = $false

    # --- uv ---
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Success "uv encontrado: $(uv --version)"
    } else {
        Write-Host "[INSTALL] uv nao encontrado. Instalando..." -ForegroundColor Yellow
        try {
            & ([scriptblock]::Create((irm https://astral.sh/uv/install.ps1)))
            Refresh-Path
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                Write-Success "uv instalado: $(uv --version)"
            } else {
                $needsRestart = $true
                Write-Host "[AVISO] uv instalado, mas sera disponivel apos reiniciar o terminal." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[AVISO] Falha ao instalar uv. Instale manualmente:" -ForegroundColor Yellow
            Write-Host '   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' -ForegroundColor Gray
        }
    }

    # --- Node.js ---
    if (Get-Command node -ErrorAction SilentlyContinue) {
        Write-Success "Node.js encontrado: $(node --version)"
    } else {
        Write-Host "[INSTALL] Node.js nao encontrado. Instalando via winget..." -ForegroundColor Yellow
        try {
            winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent 2>$null
            Refresh-Path
            if (Get-Command node -ErrorAction SilentlyContinue) {
                Write-Success "Node.js instalado: $(node --version)"
            } else {
                $needsRestart = $true
                Write-Host "[AVISO] Node.js instalado, mas sera disponivel apos reiniciar o terminal." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "[AVISO] Falha ao instalar Node.js. Instale manualmente:" -ForegroundColor Yellow
            Write-Host "   winget install OpenJS.NodeJS.LTS" -ForegroundColor Gray
            Write-Host "   Ou baixe em: https://nodejs.org/" -ForegroundColor Gray
        }
    }

    # --- make ---
    # Helper: verifica se GnuWin32 esta instalado e adiciona ao PATH se necessario
    function Ensure-GnuWin32Path {
        $gnuWin32Bin = "${env:ProgramFiles(x86)}\GnuWin32\bin"
        if (Test-Path "$gnuWin32Bin\make.exe") {
            # Adiciona ao PATH da sessao atual
            if ($env:Path -notlike "*$gnuWin32Bin*") {
                $env:Path = "$gnuWin32Bin;$env:Path"
            }
            # Adiciona ao PATH permanente do usuario (se ainda nao estiver)
            $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$gnuWin32Bin*") {
                [System.Environment]::SetEnvironmentVariable("Path", "$gnuWin32Bin;$userPath", "User")
                Write-Host "   Caminho adicionado ao PATH do usuario: $gnuWin32Bin" -ForegroundColor Gray
            }
            return $true
        }
        return $false
    }

    if (Get-Command make -ErrorAction SilentlyContinue) {
        Write-Success "make encontrado."
    } elseif (Ensure-GnuWin32Path) {
        # GnuWin32 ja esta instalado mas nao estava no PATH
        Write-Success "make encontrado em GnuWin32 (PATH corrigido)."
    } else {
        Write-Host "[INSTALL] make nao encontrado. Tentando instalar..." -ForegroundColor Yellow
        $makeInstalled = $false
        $wingetAttempted = $false

        # Tentar via winget primeiro
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            $wingetAttempted = $true
            try {
                winget install GnuWin32.Make --accept-package-agreements --accept-source-agreements --silent 2>$null

                # GnuWin32 instala em caminho conhecido — verificar e adicionar ao PATH
                if (Ensure-GnuWin32Path) {
                    Write-Success "make instalado via winget."
                    $makeInstalled = $true
                } else {
                    Refresh-Path
                    if (Get-Command make -ErrorAction SilentlyContinue) {
                        Write-Success "make instalado via winget."
                        $makeInstalled = $true
                    }
                }
            } catch { }
        }

        # Tentar via choco SOMENTE se winget nao foi tentado (nao disponivel)
        if (-not $makeInstalled -and -not $wingetAttempted -and (Get-Command choco -ErrorAction SilentlyContinue)) {
            try {
                choco install make -y 2>$null
                Refresh-Path
                if (Get-Command make -ErrorAction SilentlyContinue) {
                    Write-Success "make instalado via chocolatey."
                    $makeInstalled = $true
                }
            } catch { }
        }

        if (-not $makeInstalled) {
            $needsRestart = $true
            Write-Host "[AVISO] Falha ao instalar make. Instale manualmente:" -ForegroundColor Yellow
            Write-Host "   winget install GnuWin32.Make" -ForegroundColor Gray
            Write-Host "   Ou baixe em: https://gnuwin32.sourceforge.net/packages/make.htm" -ForegroundColor Gray
        }
    }

    if ($needsRestart) {
        Write-Host ""
        Write-Host "Algumas ferramentas foram instaladas e podem exigir reinicio do terminal." -ForegroundColor Yellow
    } else {
        Write-Success "Todas as ferramentas de desenvolvimento estao disponiveis."
    }

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
        Write-Host "Frontend:      http://localhost"
        Write-Host "Swagger API:   http://localhost/docs"
        Write-Host "Healthcheck:   http://localhost/api/v1/health"
        Write-Host "=============================================="
        Write-Host "Comandos uteis:"
        Write-Host "   Logs API:      .\infra\scripts\compose.ps1 logs -f api"
        Write-Host "   Logs Geral:    .\infra\scripts\compose.ps1 logs -f"
        Write-Host "   Derrubar:      .\infra\scripts\compose.ps1 down"
        Write-Host "   Lint + Testes: make lint && make test"
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
