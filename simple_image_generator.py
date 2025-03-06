from transformers import pipeline
import torch
from PIL import Image
import os
from pathlib import Path

class SimpleImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self):
        """Carrega o modelo de geração de imagens."""
        if self.pipe is None:
            print("Carregando modelo de geração de imagens...")
            self.pipe = pipeline(
                "text-to-image",
                model="runwayml/stable-diffusion-v1-5",
                device=self.device
            )
            print("Modelo carregado!")
            
    def generate_image(self, prompt: str) -> str:
        """Gera uma imagem a partir de um prompt."""
        try:
            self.load_model()
            
            # Gera a imagem
            print(f"Gerando imagem para: {prompt}")
            image = self.pipe(prompt).images[0]
            
            # Salva a imagem
            filename = f"generated_{len(list(self.output_dir.glob('*.png')))}.png"
            output_path = self.output_dir / filename
            image.save(output_path)
            
            return str(output_path)
            
        except Exception as e:
            print(f"Erro ao gerar imagem: {str(e)}")
            return None
            
    def __del__(self):
        """Libera recursos quando o objeto é destruído."""
        if self.pipe is not None:
            del self.pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

# Exemplo de uso
if __name__ == "__main__":
    generator = SimpleImageGenerator()
    image_path = generator.generate_image(
        "Um gato programador usando óculos e digitando em um laptop"
    )
    if image_path:
        print(f"Imagem gerada em: {image_path}")
    else:
        print("Erro ao gerar imagem") 