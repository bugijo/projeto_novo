import json
from typing import Dict, List, Optional
from pathlib import Path

class WorkflowGenerator:
    def __init__(self):
        self.templates_path = Path("workflow_templates")
        self.templates_path.mkdir(exist_ok=True)
        self._load_templates()
        
    def _load_templates(self):
        """Carrega templates de workflows."""
        self.templates = {}
        for file in self.templates_path.glob("*.json"):
            with open(file) as f:
                self.templates[file.stem] = json.load(f)
    
    def create_image_workflow(self, prompt: str) -> Dict:
        """Cria um workflow para geração de imagens."""
        workflow = {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 8,
                    "denoise": 1,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["2", 0],
                    "positive": ["1", 0],
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "seed": 8566257,
                    "steps": 20
                }
            },
            "1": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": prompt
                }
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": "bad, deformed"
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "v1-5-pruned.ckpt"
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": 512,
                    "width": 512
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["6", 0]
                }
            }
        }
        return workflow
    
    def create_code_workflow(self, prompt: str) -> Dict:
        """Cria um workflow para geração de código."""
        # Implementar depois - por enquanto retorna um workflow básico
        return self.create_image_workflow(prompt)
    
    def create_workflow(self, prompt: str, workflow_type: str = "image") -> Dict:
        """Cria um workflow baseado no tipo e prompt."""
        if workflow_type == "image_generation":
            return self.create_image_workflow(prompt)
        elif workflow_type == "code_generation":
            return self.create_code_workflow(prompt)
        else:
            # Workflow padrão para outros tipos
            return self.create_image_workflow(prompt)
    
    def save_template(self, workflow: Dict, name: str):
        """Salva um workflow como template."""
        file_path = self.templates_path / f"{name}.json"
        with open(file_path, "w") as f:
            json.dump(workflow, f, indent=2)
        self._load_templates()  # Recarrega templates
    
    def load_template(self, name: str) -> Optional[Dict]:
        """Carrega um template de workflow."""
        return self.templates.get(name)
    
    def customize_workflow(self, base_workflow: Dict, modifications: Dict) -> Dict:
        """Personaliza um workflow existente."""
        # Cria uma cópia do workflow base
        workflow = json.loads(json.dumps(base_workflow))
        
        # Aplica modificações
        for node_id, modifications in modifications.items():
            if node_id in workflow:
                workflow[node_id]["inputs"].update(modifications)
        
        return workflow 