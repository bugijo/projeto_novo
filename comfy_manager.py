import os
import sys
import json
import requests
from typing import Dict, List, Optional, Union
from pathlib import Path

class ComfyUIManager:
    def __init__(self, comfy_path: str = "../ComfyUI-master"):
        self.comfy_path = Path(comfy_path).resolve()
        self.api_url = "http://127.0.0.1:8188"
        self.workflows_path = self.comfy_path / "workflows"
        self.workflows_path.mkdir(exist_ok=True)
        
    def start_server(self) -> bool:
        """Inicia o servidor ComfyUI."""
        try:
            # Adiciona o caminho do ComfyUI ao PYTHONPATH
            sys.path.append(str(self.comfy_path))
            
            # Importa e inicia o servidor
            from main import start_server
            start_server()
            return True
        except Exception as e:
            print(f"Erro ao iniciar servidor: {str(e)}")
            return False
    
    def create_workflow(self, prompt: str) -> Dict:
        """Cria um workflow baseado em um prompt em linguagem natural."""
        # Template básico de workflow
        workflow = {
            "nodes": [],
            "prompt": prompt,
            "output": None
        }
        
        # Aqui vamos implementar a lógica para converter o prompt em nós
        # Por enquanto retorna um workflow básico
        return workflow
    
    def execute_workflow(self, workflow: Dict) -> Dict:
        """Executa um workflow no ComfyUI."""
        try:
            response = requests.post(
                f"{self.api_url}/execute",
                json=workflow
            )
            return response.json()
        except Exception as e:
            print(f"Erro ao executar workflow: {str(e)}")
            return None
    
    def save_workflow(self, workflow: Dict, name: str):
        """Salva um workflow para uso futuro."""
        file_path = self.workflows_path / f"{name}.json"
        with open(file_path, "w") as f:
            json.dump(workflow, f, indent=2)
    
    def load_workflow(self, name: str) -> Optional[Dict]:
        """Carrega um workflow salvo."""
        file_path = self.workflows_path / f"{name}.json"
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        return None
    
    def process_request(self, request: str) -> Dict:
        """Processa uma requisição em linguagem natural."""
        # 1. Analisa o tipo de requisição
        request_type = self._analyze_request(request)
        
        # 2. Cria workflow apropriado
        workflow = self.create_workflow(request)
        
        # 3. Executa workflow
        result = self.execute_workflow(workflow)
        
        # 4. Salva workflow para referência futura
        if result:
            self.save_workflow(workflow, f"auto_{len(os.listdir(self.workflows_path))}")
        
        return result
    
    def _analyze_request(self, request: str) -> str:
        """Analisa o tipo de requisição (imagem, código, etc)."""
        # Implementar análise mais sofisticada depois
        if any(kw in request.lower() for kw in ["imagem", "gerar", "criar"]):
            return "image_generation"
        elif any(kw in request.lower() for kw in ["código", "programar", "desenvolver"]):
            return "code_generation"
        return "general"

if __name__ == "__main__":
    # Exemplo de uso
    manager = ComfyUIManager()
    if manager.start_server():
        result = manager.process_request("Crie uma imagem de um gato programador") 