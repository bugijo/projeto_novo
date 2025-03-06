import os
import logging
import asyncio
from typing import Dict, Any, Optional
import uuid
from PIL import Image
import numpy as np

class GenerationManager:
    """Gerenciador de geração de conteúdo usando ComfyUI."""
    
    def __init__(self):
        self.logger = logging.getLogger('GenerationManager')
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Diretórios específicos
        self.image_dir = os.path.join(self.output_dir, "images")
        self.model_dir = os.path.join(self.output_dir, "models")
        self.video_dir = os.path.join(self.output_dir, "videos")
        self.code_dir = os.path.join(self.output_dir, "code")
        
        for directory in [self.image_dir, self.model_dir, self.video_dir, self.code_dir]:
            os.makedirs(directory, exist_ok=True)
    
    async def generate_image(self, prompt: str, type: str = "general") -> Dict[str, Any]:
        """Gera uma imagem baseada no prompt."""
        try:
            # Configura workflow baseado no tipo
            workflow = self._get_image_workflow(type)
            
            # Gera ID único para o arquivo
            image_id = str(uuid.uuid4())
            output_path = os.path.join(self.image_dir, f"{image_id}.png")
            
            # Executa workflow no ComfyUI
            result = await self._execute_workflow(workflow, {
                "prompt": prompt,
                "output_path": output_path
            })
            
            return {
                "status": "success",
                "image_url": output_path,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração de imagem: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def generate_3d_model(self, prompt: str, type: str = "character") -> Dict[str, Any]:
        """Gera um modelo 3D baseado no prompt."""
        try:
            # Configura workflow baseado no tipo
            workflow = self._get_3d_workflow(type)
            
            # Gera ID único para o arquivo
            model_id = str(uuid.uuid4())
            output_path = os.path.join(self.model_dir, f"{model_id}.glb")
            
            # Executa workflow no ComfyUI
            result = await self._execute_workflow(workflow, {
                "prompt": prompt,
                "output_path": output_path
            })
            
            return {
                "status": "success",
                "model_url": output_path,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração do modelo 3D: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def generate_video(self, prompt: str, duration: int = 10) -> Dict[str, Any]:
        """Gera um vídeo baseado no prompt."""
        try:
            # Configura workflow para vídeo
            workflow = self._get_video_workflow(duration)
            
            # Gera ID único para o arquivo
            video_id = str(uuid.uuid4())
            output_path = os.path.join(self.video_dir, f"{video_id}.mp4")
            
            # Executa workflow no ComfyUI
            result = await self._execute_workflow(workflow, {
                "prompt": prompt,
                "output_path": output_path,
                "duration": duration
            })
            
            return {
                "status": "success",
                "video_url": output_path,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração do vídeo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def generate_code(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """Gera código baseado no prompt."""
        try:
            # Configura workflow para geração de código
            workflow = self._get_code_workflow(language)
            
            # Gera ID único para o arquivo
            code_id = str(uuid.uuid4())
            output_path = os.path.join(self.code_dir, f"{code_id}.{self._get_file_extension(language)}")
            
            # Executa workflow no ComfyUI
            result = await self._execute_workflow(workflow, {
                "prompt": prompt,
                "language": language,
                "output_path": output_path
            })
            
            return {
                "status": "success",
                "code": result.get("code", ""),
                "language": language,
                "file_url": output_path,
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração de código: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def generate_workflow(self, prompt: str, type: str = "game") -> Dict[str, Any]:
        """Gera um workflow completo baseado no prompt."""
        try:
            # Gera ID único para o workflow
            workflow_id = str(uuid.uuid4())
            output_dir = os.path.join(self.output_dir, f"workflow_{workflow_id}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Configura workflow complexo
            workflow = self._get_complex_workflow(type)
            
            # Executa workflow no ComfyUI
            result = await self._execute_workflow(workflow, {
                "prompt": prompt,
                "output_dir": output_dir
            })
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "outputs": result.get("outputs", {}),
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração do workflow: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_image_workflow(self, type: str) -> Dict[str, Any]:
        """Retorna configuração do workflow para geração de imagem."""
        workflows = {
            "logo": {
                "model": "stable-diffusion-logo",
                "steps": 30,
                "cfg_scale": 7.5,
                "width": 512,
                "height": 512
            },
            "game_scene": {
                "model": "stable-diffusion-game",
                "steps": 50,
                "cfg_scale": 8.0,
                "width": 1024,
                "height": 576
            },
            "general": {
                "model": "stable-diffusion-v1-5",
                "steps": 40,
                "cfg_scale": 7.0,
                "width": 768,
                "height": 768
            }
        }
        return workflows.get(type, workflows["general"])
    
    def _get_3d_workflow(self, type: str) -> Dict[str, Any]:
        """Retorna configuração do workflow para geração 3D."""
        workflows = {
            "character": {
                "model": "point-e-character",
                "steps": 100,
                "resolution": 256,
                "detail_level": "high"
            },
            "object": {
                "model": "point-e-object",
                "steps": 80,
                "resolution": 128,
                "detail_level": "medium"
            }
        }
        return workflows.get(type, workflows["object"])
    
    def _get_video_workflow(self, duration: int) -> Dict[str, Any]:
        """Retorna configuração do workflow para geração de vídeo."""
        return {
            "model": "stable-diffusion-video",
            "fps": 30,
            "frames": duration * 30,
            "motion_bucket_id": 127,
            "noise_aug_level": 0.1
        }
    
    def _get_code_workflow(self, language: str) -> Dict[str, Any]:
        """Retorna configuração do workflow para geração de código."""
        return {
            "model": "code-llama",
            "temperature": 0.7,
            "max_length": 2048,
            "language": language
        }
    
    def _get_complex_workflow(self, type: str) -> Dict[str, Any]:
        """Retorna configuração para workflows complexos."""
        workflows = {
            "game": {
                "steps": [
                    {"type": "3d_model", "config": self._get_3d_workflow("character")},
                    {"type": "image", "config": self._get_image_workflow("game_scene")},
                    {"type": "code", "config": self._get_code_workflow("python")},
                    {"type": "ui", "config": self._get_image_workflow("ui")}
                ],
                "dependencies": {
                    "character_model": ["game_logic"],
                    "game_scene": ["game_logic", "ui"],
                    "ui": ["game_logic"]
                }
            }
        }
        return workflows.get(type, {})
    
    def _get_file_extension(self, language: str) -> str:
        """Retorna a extensão de arquivo apropriada para cada linguagem."""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "csharp": "cs"
        }
        return extensions.get(language, "txt")
    
    async def _execute_workflow(self, workflow: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um workflow no ComfyUI."""
        # TODO: Implementar integração real com ComfyUI
        # Por enquanto, simula a execução
        await asyncio.sleep(2)  # Simula processamento
        
        if "output_path" in params:
            # Cria uma imagem de teste
            img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            Image.fromarray(img).save(params["output_path"])
        
        return {
            "status": "success",
            "metadata": {
                "workflow": workflow,
                "params": params,
                "timestamp": str(uuid.uuid4())
            }
        } 