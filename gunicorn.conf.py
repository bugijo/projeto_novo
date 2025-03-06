import multiprocessing
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do servidor
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv('THREADS', 4))
worker_class = 'gthread'
timeout = int(os.getenv('TIMEOUT', 120))

# Configurações de logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configurações de processo
daemon = False
pidfile = 'gunicorn.pid'
user = None
group = None
umask = 0
tmp_upload_dir = None

# Configurações de SSL/TLS
keyfile = None
certfile = None

# Configurações de performance
worker_connections = 1000
max_requests = 2000
max_requests_jitter = 400
graceful_timeout = 30
keep_alive = 5

# Configurações de debug
reload = os.getenv('FLASK_ENV', 'production') == 'development'
reload_engine = 'auto'
spew = False
check_config = False

# Hooks
def on_starting(server):
    """Log quando o servidor está iniciando."""
    server.log.info("Iniciando servidor Gunicorn...")

def on_reload(server):
    """Log quando o servidor está recarregando."""
    server.log.info("Recarregando servidor Gunicorn...")

def when_ready(server):
    """Log quando o servidor está pronto."""
    server.log.info(f"Servidor Gunicorn pronto. Listening em {bind}")

def on_exit(server):
    """Log quando o servidor está encerrando."""
    server.log.info("Encerrando servidor Gunicorn...") 