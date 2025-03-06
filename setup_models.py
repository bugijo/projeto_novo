import os
import logging
import subprocess
import ssl
import urllib.request

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs dos modelos (versões mais leves)
MODELOS = {
    'phi': {
        'url': 'https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf',
        'arquivo': 'models/phi-2.Q4_K_M.gguf'
    },
    'tinyllama': {
        'url': 'https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
        'arquivo': 'models/tinyllama-1.1b-chat.Q4_K_M.gguf'
    }
}

def baixar_arquivo(url, destino):
    """Baixa um arquivo usando urllib com configuração SSL personalizada."""
    if os.path.exists(destino):
        logger.info(f"Arquivo {destino} já existe, pulando download...")
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        
        # Configurar contexto SSL
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Baixar arquivo
        logger.info(f"Baixando {url}...")
        urllib.request.urlretrieve(url, destino)
        logger.info(f"Download concluído: {destino}")
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar {url}: {str(e)}")
        return False

def instalar_dependencias():
    """Instala as dependências necessárias."""
    deps = [
        'llama-cpp-python',
        'torch --index-url https://download.pytorch.org/whl/cpu',
        'transformers',
        'accelerate'
    ]
    
    for dep in deps:
        try:
            # Usando --trusted-host para evitar problemas de SSL
            cmd = f'pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org {dep}'
            subprocess.run(cmd.split(), check=True)
            logger.info(f"Instalado {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao instalar {dep}: {str(e)}")

def main():
    """Função principal para configuração dos modelos."""
    logger.info("Iniciando setup dos modelos...")
    
    # Criar diretório models se não existir
    os.makedirs('models', exist_ok=True)
    
    # Instalar dependências
    logger.info("Instalando dependências...")
    instalar_dependencias()
    
    # Baixar modelos
    for nome, info in MODELOS.items():
        logger.info(f"Baixando modelo {nome}...")
        if baixar_arquivo(info['url'], info['arquivo']):
            logger.info(f"Modelo {nome} baixado com sucesso!")
        else:
            logger.error(f"Falha ao baixar modelo {nome}")

if __name__ == "__main__":
    main() 