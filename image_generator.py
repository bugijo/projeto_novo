import torch
from diffusers import StableDiffusionPipeline
import os
from pathlib import Path

class ImageGenerator:
    def __init__(self):
        self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self):
        """Carrega o modelo de geração de imagens."""
        if self.pipe is None:
            print("Carregando modelo de geração de imagens...")
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.pipe = self.pipe.to(self.device)
            print("Modelo carregado!")
            
    def generate_image(self, prompt: str, negative_prompt: str = None) -> str:
        """Gera uma imagem a partir de um prompt."""
        try:
            self.load_model()
            
            # Gera a imagem
            print(f"Gerando imagem para: {prompt}")
            image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=30,
                guidance_scale=7.5
            ).images[0]
            
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
            torch.cuda.empty_cache()

# Exemplo de uso
if __name__ == "__main__":
    generator = ImageGenerator()
    image_path = generator.generate_image(
        prompt="Um gato programador usando óculos e digitando em um laptop",
        negative_prompt="baixa qualidade, borrado, distorcido"
    )
    if image_path:
        print(f"Imagem gerada em: {image_path}")
    else:
        print("Erro ao gerar imagem") 