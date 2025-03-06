import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Union

class ComfyUIIntegration:
    def __init__(self):
        self.comfy_path = Path("ComfyUI").resolve()
        self.api_url = "http://127.0.0.1:8188"
        self.process = None
        self.workflows_path = self.comfy_path / "workflows"
        self.workflows_path.mkdir(exist_ok=True)
        
    def start_server(self) -> bool:
        """Inicia o servidor ComfyUI em background."""
        try:
            if self.process and self.process.poll() is None:
                print("Servidor ComfyUI já está rodando")
                return True
                
            python_path = sys.executable
            cmd = [python_path, str(self.comfy_path / "main.py")]
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.comfy_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Espera um pouco para o servidor iniciar
            import time
            time.sleep(5)
            
            # Verifica se o servidor está respondendo
            try:
                response = requests.get(f"{self.api_url}/history")
                if response.status_code == 200:
                    print("Servidor ComfyUI iniciado com sucesso")
                    return True
            except:
                pass
                
            print("Erro ao iniciar servidor ComfyUI")
            return False
            
        except Exception as e:
            print(f"Erro ao iniciar servidor ComfyUI: {str(e)}")
            return False
            
    def stop_server(self):
        """Para o servidor ComfyUI."""
        if self.process:
            self.process.terminate()
            self.process = None
            
    def create_image_workflow(self, prompt: str) -> Dict:
        """Cria um workflow para geração de imagem."""
        workflow = {
            "3": {
                "inputs": {
                    "seed": 5371934908291,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {
                    "title": "KSampler"
                }
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {
                    "title": "Load Checkpoint"
                }
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {
                    "title": "Empty Latent Image"
                }
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Positive)"
                }
            },
            "7": {
                "inputs": {
                    "text": "bad quality, blurry, distorted",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Negative)"
                }
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {
                    "title": "VAE Decode"
                }
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            }
        }
        return workflow
        
    def execute_workflow(self, workflow: Dict) -> Optional[str]:
        """Executa um workflow e retorna o caminho da imagem gerada."""
        try:
            # Envia o workflow
            response = requests.post(
                f"{self.api_url}/prompt",
                json={"prompt": workflow}
            )
            
            if response.status_code != 200:
                print(f"Erro ao enviar workflow: {response.text}")
                return None
                
            prompt_id = response.json()["prompt_id"]
            
            # Espera a execução completar
            while True:
                history = requests.get(f"{self.api_url}/history").json()
                if prompt_id in history:
                    outputs = history[prompt_id]["outputs"]
                    if outputs:
                        # Pega o caminho da última imagem gerada
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                image_path = node_output["images"][0]["filename"]
                                return os.path.join(self.comfy_path, "output", image_path)
                    break
                    
                import time
                time.sleep(1)
                
        except Exception as e:
            print(f"Erro ao executar workflow: {str(e)}")
            
        return None
        
    def generate_image(self, prompt: str) -> Optional[str]:
        """Gera uma imagem a partir de um prompt."""
        if not self.start_server():
            return None
            
        workflow = self.create_image_workflow(prompt)
        return self.execute_workflow(workflow)
        
    def __del__(self):
        """Garante que o servidor seja desligado quando o objeto é destruído."""
        self.stop_server()

# Exemplo de uso
if __name__ == "__main__":
    comfy = ComfyUIIntegration()
    image_path = comfy.generate_image("Um gato programador usando óculos e digitando em um laptop")
    if image_path:
        print(f"Imagem gerada em: {image_path}")
    else:
        print("Erro ao gerar imagem") 