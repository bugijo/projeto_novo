import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pythonjsonlogger import jsonlogger

# Cria diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuração básica
def setup_logging(level=logging.INFO):
    """Configura o sistema de logging."""
    
    # Formatos de log
    console_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
    json_format = "%(asctime)s %(levelname)s %(message)s %(filename)s %(lineno)s"
    
    # Logger raiz
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para console
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(console_format))
    logger.addHandler(console)
    
    # Handler para arquivo JSON
    json_handler = RotatingFileHandler(
        log_dir / "app.json",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    json_handler.setLevel(level)
    json_handler.setFormatter(
        jsonlogger.JsonFormatter(json_format)
    )
    logger.addHandler(json_handler)
    
    # Handler para arquivo de erros
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(console_format))
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name):
    """Retorna um logger configurado para o módulo especificado."""
    return logging.getLogger(name)

# Configuração para ambiente de desenvolvimento
def setup_dev_logging():
    """Configura logging para desenvolvimento."""
    setup_logging(level=logging.DEBUG)

# Configuração para ambiente de produção
def setup_prod_logging():
    """Configura logging para produção."""
    setup_logging(level=logging.INFO)

# Configuração para ambiente de teste
def setup_test_logging():
    """Configura logging para testes."""
    setup_logging(level=logging.WARNING)

if __name__ == "__main__":
    # Exemplo de uso
    logger = setup_logging()
    logger.info("Sistema de logging configurado")
    logger.debug("Mensagem de debug")
    logger.warning("Aviso importante")
    logger.error("Erro crítico", exc_info=True) 