import os
import sys
import subprocess
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, dest_path: Path, desc: str = None):
    """Baixa um arquivo com barra de progresso."""
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as file, tqdm(
        desc=desc,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def setup_comfyui():
    """Configura o ComfyUI e baixa os modelos necessários."""
    print("Configurando ComfyUI...")
    
    # Diretórios
    comfy_dir = Path("ComfyUI")
    models_dir = comfy_dir / "models"
    checkpoints_dir = models_dir / "checkpoints"
    
    # Cria diretórios
    for dir in [models_dir, checkpoints_dir]:
        dir.mkdir(parents=True, exist_ok=True)
    
    # URLs dos modelos
    models = {
        "sd_xl_base_1.0.safetensors": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "sd_xl_refiner_1.0.safetensors": "https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors"
    }
    
    # Baixa os modelos
    for model_name, url in models.items():
        model_path = checkpoints_dir / model_name
        if not model_path.exists():
            print(f"\nBaixando {model_name}...")
            download_file(url, model_path, desc=model_name)
        else:
            print(f"\n{model_name} já existe, pulando...")
    
    # Instala dependências do ComfyUI
    print("\nInstalando dependências do ComfyUI...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(comfy_dir / "requirements.txt")])
    
    print("\nConfiguração concluída!")

if __name__ == "__main__":
    setup_comfyui() 