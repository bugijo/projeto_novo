# Script de instalação do DevAssistant IDE para Windows
Write-Host "Iniciando instalação do DevAssistant IDE..." -ForegroundColor Green

# Verificar se o Python está instalado
try {
    $pythonVersion = python --version
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python não encontrado. Por favor, instale o Python 3.9 ou superior." -ForegroundColor Red
    exit 1
}

# Verificar se o pip está instalado
try {
    $pipVersion = pip --version
    Write-Host "Pip encontrado: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Pip não encontrado. Por favor, instale o pip." -ForegroundColor Red
    exit 1
}

# Criar ambiente virtual
Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
python -m venv venv

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate

# Atualizar pip
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Instalar dependências
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Criar diretórios necessários
Write-Host "Criando diretórios..." -ForegroundColor Yellow
$dirs = @(
    "$HOME\workspace",
    "$HOME\.devassistant\temp",
    "$HOME\.devassistant\cache",
    "$HOME\.devassistant\logs"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Diretório criado: $dir" -ForegroundColor Green
    }
}

# Criar atalho na área de trabalho
Write-Host "Criando atalho na área de trabalho..." -ForegroundColor Yellow
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$HOME\Desktop\DevAssistant IDE.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -Command `"cd '$PWD'; .\venv\Scripts\Activate; python main.py`""
$Shortcut.WorkingDirectory = $PWD
$Shortcut.Save()

Write-Host "`nInstalação concluída com sucesso!" -ForegroundColor Green
Write-Host "Você pode iniciar o DevAssistant IDE através do atalho criado na área de trabalho." -ForegroundColor Green
Write-Host "Ou executando 'python main.py' neste diretório após ativar o ambiente virtual." -ForegroundColor Green 