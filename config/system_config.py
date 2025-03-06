import os
from pathlib import Path

# Configurações do Sistema
SYSTEM_NAME = "AI Studio"
VERSION = "1.0.0"
DEBUG = True

# Diretórios
BASE_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
TEMPLATES_DIR = BASE_DIR / "templates"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "outputs"

# Configurações do ComfyUI
COMFYUI_CONFIG = {
    "host": "localhost",
    "port": 8188,
    "api_url": "http://localhost:8188/api",
    "websocket_url": "ws://localhost:8188/ws",
    "models_dir": str(MODELS_DIR),
    "output_dir": str(OUTPUT_DIR)
}

# Configurações de IA
AI_CONFIG = {
    "main_model": "stable-diffusion-v1-5",
    "fallback_model": "stable-diffusion-v1-4",
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Configurações de Segurança
SECURITY_CONFIG = {
    "require_auth": True,
    "allowed_users": ["admin", "Bugijo"],
    "token_expiration": 86400,  # 24 horas
    "encryption_key": "sua_chave_secreta_muito_segura_aqui_2024",  # Nova chave de criptografia
    "max_requests_per_minute": 60
}

# Configurações de Cache
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 1024 * 1024 * 1024,  # 1GB
    "ttl": 3600,  # 1 hora
    "dir": str(CACHE_DIR)
}

# Configurações de Log
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "system.log"),
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Configurações de Integração
INTEGRATION_CONFIG = {
    "github": {
        "enabled": False,
        "token": os.getenv("GITHUB_TOKEN")
    },
    "google": {
        "enabled": False,
        "credentials_file": "credentials.json"
    }
}

# Configurações de Workflow
WORKFLOW_CONFIG = {
    "max_concurrent": 5,
    "timeout": 300,  # 5 minutos
    "auto_retry": True,
    "max_retries": 3
}

# Configurações de Auto-otimização
OPTIMIZATION_CONFIG = {
    "enabled": True,
    "check_interval": 86400,  # 24 horas
    "metrics": [
        "response_time",
        "memory_usage",
        "cache_hits",
        "error_rate"
    ]
}

# Configurações da Interface
UI_CONFIG = {
    "theme": "light",
    "language": "pt-BR",
    "max_messages": 100,
    "auto_scroll": True
}

# Configurações de Desenvolvimento
DEV_CONFIG = {
    "test_mode": False,
    "mock_responses": False,
    "profile_enabled": False
}

# Cria diretórios necessários
for directory in [WORKSPACE_DIR, TEMPLATES_DIR, MODELS_DIR, CACHE_DIR, LOGS_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True) 