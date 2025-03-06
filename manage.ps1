# Funções de utilidade
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-ColorOutput Red "Docker não está rodando. Por favor, inicie o Docker primeiro."
        return $false
    }
}

function New-DockerNetwork {
    if (-not (docker network ls | Select-String -Pattern "web")) {
        Write-ColorOutput Yellow "Criando rede 'web'..."
        docker network create web
    }
}

function Start-Services {
    Write-ColorOutput Green "Iniciando serviços..."
    docker-compose up -d
}

function Stop-Services {
    Write-ColorOutput Yellow "Parando serviços..."
    docker-compose down
}

function Restart-Services {
    Write-ColorOutput Yellow "Reiniciando serviços..."
    docker-compose restart
}

function Show-Logs {
    param (
        [string]$Service
    )
    if ($Service) {
        docker-compose logs -f $Service
    }
    else {
        docker-compose logs -f
    }
}

function Show-Status {
    Write-ColorOutput Green "Status dos serviços:"
    docker-compose ps
}

function Clear-Volumes {
    Write-ColorOutput Yellow "Atenção: Isso irá remover todos os volumes. Os dados serão perdidos!"
    $confirmation = Read-Host "Deseja continuar? (s/N)"
    if ($confirmation -match '^[sS]$') {
        Write-ColorOutput Red "Removendo volumes..."
        docker-compose down -v
    }
}

function Update-Images {
    Write-ColorOutput Green "Atualizando imagens..."
    docker-compose pull
    Write-ColorOutput Yellow "Reiniciando serviços com novas imagens..."
    docker-compose up -d
}

function Show-Help {
    Write-Output @"
Uso: .\manage.ps1 [comando]

Comandos:
  start       - Inicia todos os serviços
  stop        - Para todos os serviços
  restart     - Reinicia todos os serviços
  status      - Mostra o status dos serviços
  logs [svc]  - Mostra logs (opcional: especifique o serviço)
  clean       - Remove todos os volumes (cuidado: dados serão perdidos)
  update      - Atualiza imagens dos serviços
  help        - Mostra esta mensagem de ajuda
"@
}

# Verificar se o Docker está rodando
if (-not (Test-Docker)) {
    exit 1
}

# Processar comandos
switch ($args[0]) {
    "start" {
        New-DockerNetwork
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs $args[1]
    }
    "clean" {
        Clear-Volumes
    }
    "update" {
        Update-Images
    }
    default {
        Show-Help
    }
} 