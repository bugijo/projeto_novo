# Funções de utilidade para testes
function Write-TestResult {
    param (
        [string]$TestName,
        [bool]$Success,
        [string]$Message = ""
    )
    
    $color = if ($Success) { "Green" } else { "Red" }
    $status = if ($Success) { "✓" } else { "✗" }
    
    Write-ColorOutput $color "[$status] $TestName"
    if ($Message) {
        Write-ColorOutput "Yellow" "    $Message"
    }
}

function Write-TestHeader {
    param ([string]$Title)
    Write-Output "`n=== $Title ===`n"
}

function Test-PythonEnvironment {
    Write-TestHeader "Testando Ambiente Python"
    
    # Testa Python
    $pythonOk = Test-Python
    Write-TestResult "Verificação do Python" $pythonOk
    
    # Testa ambiente virtual
    $venvPath = "venv"
    New-VirtualEnv
    $venvOk = Test-Path $venvPath
    Write-TestResult "Criação do ambiente virtual" $venvOk
    
    # Testa ativação do ambiente
    try {
        .\venv\Scripts\Activate.ps1
        Write-TestResult "Ativação do ambiente virtual" $true
    }
    catch {
        Write-TestResult "Ativação do ambiente virtual" $false $_
    }
    
    # Testa instalação de dependências
    $depsOk = Install-Dependencies
    Write-TestResult "Instalação de dependências" $depsOk
}

function Test-ComfyUISetup {
    Write-TestHeader "Testando Setup do ComfyUI"
    
    # Testa diretórios do ComfyUI
    $setupOk = Setup-ComfyUI
    Write-TestResult "Setup do ComfyUI" $setupOk
    
    # Testa existência dos diretórios principais
    $paths = @(
        "..\ComfyUI-master\models",
        "..\ComfyUI-master\workflows"
    )
    
    foreach ($path in $paths) {
        $exists = Test-Path $path
        Write-TestResult "Verificação do diretório $path" $exists
    }
}

function Test-APIEndpoints {
    Write-TestHeader "Testando Endpoints da API"
    
    # Inicia o servidor em background
    Start-Process -NoNewWindow -FilePath ".\venv\Scripts\python.exe" -ArgumentList "api.py"
    Start-Sleep -Seconds 5
    
    # Testa endpoints principais
    $endpoints = @(
        @{
            "name" = "Status da API"
            "url" = "http://localhost:5000/api/status"
            "method" = "GET"
        },
        @{
            "name" = "Processamento de mensagem"
            "url" = "http://localhost:5000/api/chat"
            "method" = "POST"
            "body" = @{
                "message" = "Olá, como você está?"
                "type" = "chat"
            }
        }
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            if ($endpoint.method -eq "GET") {
                $response = Invoke-RestMethod -Uri $endpoint.url -Method GET
            }
            else {
                $body = $endpoint.body | ConvertTo-Json
                $response = Invoke-RestMethod -Uri $endpoint.url -Method POST -Body $body -ContentType "application/json"
            }
            Write-TestResult $endpoint.name $true
        }
        catch {
            Write-TestResult $endpoint.name $false $_
        }
    }
    
    # Para o servidor
    Stop-Process -Name "python" -ErrorAction SilentlyContinue
}

function Test-ImageGeneration {
    Write-TestHeader "Testando Geração de Imagens"
    
    # Testa workflow de geração de imagem
    $workflow = @{
        "prompt" = "Um gato programador usando óculos"
        "type" = "image_generation"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/process" -Method POST -Body $workflow -ContentType "application/json"
        Write-TestResult "Geração de imagem" $true
    }
    catch {
        Write-TestResult "Geração de imagem" $false $_
    }
}

function Test-FileOperations {
    Write-TestHeader "Testando Operações com Arquivos"
    
    # Testa criação de arquivo
    $testFile = "test_file.txt"
    try {
        "Teste de conteúdo" | Out-File $testFile
        Write-TestResult "Criação de arquivo" $true
    }
    catch {
        Write-TestResult "Criação de arquivo" $false $_
    }
    
    # Testa leitura de arquivo
    try {
        $content = Get-Content $testFile
        Write-TestResult "Leitura de arquivo" $true
    }
    catch {
        Write-TestResult "Leitura de arquivo" $false $_
    }
    
    # Testa edição de arquivo
    try {
        Add-Content $testFile "`nNova linha"
        Write-TestResult "Edição de arquivo" $true
    }
    catch {
        Write-TestResult "Edição de arquivo" $false $_
    }
    
    # Limpa arquivo de teste
    Remove-Item $testFile -ErrorAction SilentlyContinue
}

function Test-AIAssistant {
    Write-TestHeader "Testando Assistente IA"
    
    $tests = @(
        @{
            "name" = "Resposta simples"
            "prompt" = "Qual é a capital do Brasil?"
        },
        @{
            "name" = "Geração de código"
            "prompt" = "Crie uma função Python que soma dois números"
        },
        @{
            "name" = "Análise de código"
            "prompt" = "Analise este código: def soma(a,b): return a+b"
        }
    )
    
    foreach ($test in $tests) {
        try {
            $body = @{
                "message" = $test.prompt
                "type" = "chat"
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:5000/api/chat" -Method POST -Body $body -ContentType "application/json"
            Write-TestResult $test.name $true
        }
        catch {
            Write-TestResult $test.name $false $_
        }
    }
}

# Executa todos os testes
Write-Output "Iniciando testes do sistema..."

Test-PythonEnvironment
Test-ComfyUISetup
Test-APIEndpoints
Test-ImageGeneration
Test-FileOperations
Test-AIAssistant

Write-Output "`nTestes concluídos!" 