import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """Verifica a versão do Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("Python 3.10 ou superior é necessário")
        return False
    return True

def install_dependencies():
    """Instala as dependências necessárias."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

def setup_comfyui():
    """Configura o ComfyUI."""
    try:
        # Verifica se o ComfyUI está presente
        comfy_path = Path("../ComfyUI-master")
        if not comfy_path.exists():
            print("ComfyUI não encontrado. Por favor, clone o repositório primeiro.")
            return False
        
        # Cria diretórios necessários
        (comfy_path / "models").mkdir(exist_ok=True)
        (comfy_path / "workflows").mkdir(exist_ok=True)
        
        return True
    except Exception as e:
        print(f"Erro ao configurar ComfyUI: {e}")
        return False

def main():
    """Função principal de setup."""
    print("Iniciando setup...")
    
    # Verifica Python
    if not check_python():
        return
    
    # Instala dependências
    print("Instalando dependências...")
    if not install_dependencies():
        return
    
    # Configura ComfyUI
    print("Configurando ComfyUI...")
    if not setup_comfyui():
        return
    
    print("\nSetup concluído com sucesso!")
    print("\nPara iniciar o sistema:")
    print("1. Certifique-se de ter os modelos necessários em ../ComfyUI-master/models")
    print("2. Execute: python api.py")

if __name__ == "__main__":
    main() 