# Funções de utilidade
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Test-Python {
    try {
        $version = python --version
        if ($version -match "Python 3\.10\.*") {
            return $true
        }
        Write-ColorOutput Red "Python 3.10 ou superior é necessário"
        return $false
    }
    catch {
        Write-ColorOutput Red "Python não está instalado"
        return $false
    }
}

function New-VirtualEnv {
    if (-not (Test-Path "venv")) {
        Write-ColorOutput Yellow "Criando ambiente virtual..."
        python -m venv venv
    }
}

function Install-Dependencies {
    Write-ColorOutput Yellow "Instalando dependências..."
    try {
        .\venv\Scripts\pip install -r requirements.txt
        return $true
    }
    catch {
        Write-ColorOutput Red "Erro ao instalar dependências: $_"
        return $false
    }
}

function Setup-ComfyUI {
    $comfyPath = "..\ComfyUI-master"
    if (-not (Test-Path $comfyPath)) {
        Write-ColorOutput Red "ComfyUI não encontrado. Por favor, clone o repositório primeiro."
        return $false
    }

    # Criar diretórios necessários
    New-Item -ItemType Directory -Force -Path "$comfyPath\models" | Out-Null
    New-Item -ItemType Directory -Force -Path "$comfyPath\workflows" | Out-Null

    return $true
}

# Verificar Python
if (-not (Test-Python)) {
    Write-ColorOutput Yellow "Por favor, instale Python 3.10 ou superior de https://www.python.org/downloads/"
    exit 1
}

# Criar ambiente virtual
New-VirtualEnv

# Ativar o ambiente virtual usando o Python 3.10
C:\Users\Usuário\OneDrive\Documentos\Python-3.10.16\python.exe -m venv venv

# Ativar o ambiente virtual
& .\venv\Scripts\Activate.ps1

# Instalar as dependências
C:\Users\Usuário\OneDrive\Documentos\Python-3.10.16\python.exe -m pip install -r requirements.txt

# Configurar ComfyUI
if (-not (Setup-ComfyUI)) {
    exit 1
}

# Mensagem de conclusão
Write-Output "Ambiente configurado com sucesso!"

Write-ColorOutput Green "`nSetup concluído com sucesso!"
Write-ColorOutput Yellow "`nPara iniciar o sistema:"
Write-ColorOutput White "1. Certifique-se de ter os modelos necessários em ..\ComfyUI-master\models"
Write-ColorOutput White "2. Execute: .\venv\Scripts\python api.py" 