import os
import sys
import subprocess
import requests
import zipfile
import io
from pathlib import Path

def download_file_with_progress(url: str, desc: str = None):
    """Baixa um arquivo e retorna os bytes."""
    print(f"Baixando {desc or url}...")
    response = requests.get(url, stream=True, verify=False)
    response.raise_for_status()
    
    # Obtém o tamanho total do arquivo
    total_size = int(response.headers.get('content-length', 0))
    if total_size == 0:
        print("Aviso: Tamanho do arquivo desconhecido")
        # Baixa diretamente
        return response.content
        
    block_size = 1024
    downloaded = 0
    
    # Baixa o arquivo em chunks
    content = bytearray()
    for data in response.iter_content(block_size):
        downloaded += len(data)
        content.extend(data)
        
        # Mostra o progresso
        if total_size > 0:
            done = int(50 * downloaded / total_size)
            sys.stdout.write('\r[{}{}] {:.1f}%'.format(
                '=' * done,
                ' ' * (50-done),
                downloaded * 100 / total_size
            ))
            sys.stdout.flush()
    
    print()
    return bytes(content)

def setup_comfyui():
    """Configura o ComfyUI manualmente."""
    print("Configurando ComfyUI...")
    
    # Diretórios
    comfy_dir = Path("ComfyUI")
    models_dir = comfy_dir / "models"
    checkpoints_dir = models_dir / "checkpoints"
    
    # Cria diretórios
    for dir in [models_dir, checkpoints_dir]:
        dir.mkdir(parents=True, exist_ok=True)
    
    # Baixa o ComfyUI
    try:
        print("\nBaixando ComfyUI do GitHub...")
        response = requests.get(
            "https://github.com/comfyanonymous/ComfyUI/archive/refs/heads/master.zip",
            verify=False
        )
        response.raise_for_status()
        
        # Extrai o ComfyUI
        print("Extraindo ComfyUI...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall()
            
        # Move os arquivos para o diretório correto
        if (Path("ComfyUI-master").exists()):
            for item in Path("ComfyUI-master").iterdir():
                if item.name not in ['.git']:
                    dest = comfy_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            for subitem in item.iterdir():
                                if not (dest / subitem.name).exists():
                                    subitem.rename(dest / subitem.name)
                        else:
                            item.unlink()
                    else:
                        item.rename(dest)
            
            # Remove o diretório temporário
            import shutil
            shutil.rmtree("ComfyUI-master", ignore_errors=True)
    except Exception as e:
        print(f"Erro ao baixar/extrair ComfyUI: {str(e)}")
        return False
    
    # Instala dependências básicas
    print("\nInstalando dependências básicas...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "torch", "torchvision", "torchaudio",
        "numpy", "aiohttp", "pillow", "tqdm"
    ])
    
    # Baixa os modelos
    print("\nBaixando modelos...")
    models = {
        "sd_xl_base_1.0.safetensors": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
    }
    
    for model_name, url in models.items():
        model_path = checkpoints_dir / model_name
        if not model_path.exists():
            try:
                print(f"\nBaixando {model_name}...")
                response = requests.get(url, verify=False)
                response.raise_for_status()
                
                with open(model_path, 'wb') as f:
                    f.write(response.content)
                print(f"{model_name} baixado com sucesso!")
            except Exception as e:
                print(f"\nErro ao baixar {model_name}: {str(e)}")
                continue
    
    print("\nConfiguração concluída!")
    return True

if __name__ == "__main__":
    # Desativa verificação SSL para evitar problemas
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    if setup_comfyui():
        print("\nComfyUI configurado com sucesso!")
    else:
        print("\nErro ao configurar ComfyUI") 