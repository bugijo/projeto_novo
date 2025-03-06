import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-padrao")
    FLASK_APP = os.getenv("FLASK_APP", "api.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    
    # Servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    WORKERS = int(os.getenv("WORKERS", 4))
    THREADS = int(os.getenv("THREADS", 4))
    TIMEOUT = int(os.getenv("TIMEOUT", 120))
    
    # ComfyUI
    COMFYUI_PATH = Path(os.getenv("COMFYUI_PATH", "../ComfyUI-master")).resolve()
    MODELS_PATH = COMFYUI_PATH / "models"
    WORKFLOWS_PATH = COMFYUI_PATH / "workflows"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    
    # Cache
    CACHE_TYPE = os.getenv("CACHE_TYPE", "filesystem")
    CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", "cache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    
    # Segurança
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100/hour")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    
    # Monitoramento
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", 9090))

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    
    FLASK_ENV = "development"
    DEBUG = True
    DEBUG_TOOLBAR_ENABLED = True
    PROFILE_REQUESTS = True

class TestingConfig(Config):
    """Configuração para testes."""
    
    FLASK_ENV = "testing"
    TESTING = True
    DEBUG = True
    
    # Desativa recursos pesados em testes
    CACHE_TYPE = "null"
    RATELIMIT_ENABLED = False
    ENABLE_METRICS = False

class ProductionConfig(Config):
    """Configuração para produção."""
    
    FLASK_ENV = "production"
    DEBUG = False
    DEBUG_TOOLBAR_ENABLED = False
    PROFILE_REQUESTS = False
    
    # Configurações mais restritivas
    RATELIMIT_DEFAULT = "50/hour"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB

# Mapeamento de configurações
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config():
    """Retorna a configuração apropriada baseada no ambiente."""
    env = os.getenv("FLASK_ENV", "default")
    return config.get(env, config["default"]) 