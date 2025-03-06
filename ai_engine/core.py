import os
import json
import logging
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import shutil

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectSpec:
    name: str
    description: str
    platform: str
    language: str
    dependencies: List[str]
    features: List[str]
    architecture: Dict[str, any]

@dataclass
class CodeGenResult:
    files: Dict[str, str]  # path -> content
    tests: Dict[str, str]  # test_path -> content
    dependencies: Dict[str, str]  # name -> version
    build_steps: List[str]
    validation_results: Dict[str, bool]

class AIEngine:
    def __init__(self, lm_studio_url: str = "http://localhost:1234/v1"):
        self.lm_studio_url = lm_studio_url
        self.cache_dir = Path("ai_engine/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict:
        kb_path = self.cache_dir / "knowledge_base.json"
        if kb_path.exists():
            return json.loads(kb_path.read_text())
        return {"decisions": [], "corrections": [], "patterns": []}
    
    def _save_knowledge_base(self):
        kb_path = self.cache_dir / "knowledge_base.json"
        kb_path.write_text(json.dumps(self.knowledge_base, indent=2))
    
    def _generate_completion(self, prompt: str, max_tokens: int = 2000) -> str:
        """Gera completions usando LM Studio local."""
        try:
            response = requests.post(
                f"{self.lm_studio_url}/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["text"]
            else:
                logger.error(f"Erro na API do LM Studio: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Erro ao gerar completion: {str(e)}")
            return None
    
    def parse_requirements(self, prompt: str) -> ProjectSpec:
        """Converte requisitos em linguagem natural para especificação técnica."""
        system_prompt = """Você é um especialista em arquitetura de software.
        Analise os requisitos e gere uma especificação técnica detalhada.
        Inclua: plataforma alvo, linguagem, dependências, features e arquitetura."""
        
        full_prompt = f"{system_prompt}\n\nRequisitos:\n{prompt}\n\nEspecificação:"
        result = self._generate_completion(full_prompt)
        
        try:
            spec_dict = json.loads(result)
            return ProjectSpec(**spec_dict)
        except Exception as e:
            logger.error(f"Erro ao parsear especificação: {str(e)}")
            return None
    
    def generate_code(self, spec: ProjectSpec) -> CodeGenResult:
        """Gera código baseado na especificação."""
        system_prompt = """Você é um expert em desenvolvimento de software.
        Gere código completo baseado na especificação, incluindo testes."""
        
        full_prompt = f"{system_prompt}\n\nEspecificação:\n{json.dumps(spec.__dict__)}\n\nCódigo:"
        result = self._generate_completion(full_prompt)
        
        try:
            code_dict = json.loads(result)
            return CodeGenResult(**code_dict)
        except Exception as e:
            logger.error(f"Erro ao gerar código: {str(e)}")
            return None
    
    def validate_code(self, result: CodeGenResult) -> bool:
        """Valida o código gerado usando análise estática e testes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Cria estrutura de arquivos temporária
            tmp_path = Path(tmpdir)
            for file_path, content in result.files.items():
                full_path = tmp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Executa testes
            for test_path, test_content in result.tests.items():
                full_path = tmp_path / test_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(test_content)
            
            try:
                # Executa testes no ambiente virtual
                subprocess.run(
                    ["python", "-m", "pytest", str(tmp_path)],
                    check=True,
                    capture_output=True
                )
                return True
            except subprocess.CalledProcessError:
                return False
    
    def deploy_project(self, result: CodeGenResult, output_dir: str):
        """Deploy do projeto para o diretório especificado."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Copia arquivos
        for file_path, content in result.files.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Cria ambiente virtual
        subprocess.run(["python", "-m", "venv", str(output_path / "venv")], check=True)
        
        # Instala dependências
        requirements_path = output_path / "requirements.txt"
        with requirements_path.open("w") as f:
            for name, version in result.dependencies.items():
                f.write(f"{name}=={version}\n")
        
        # Atualiza knowledge base
        self.knowledge_base["decisions"].append({
            "type": "deployment",
            "project": output_path.name,
            "timestamp": str(datetime.now()),
            "status": "success"
        })
        self._save_knowledge_base()

    def create_project(self, prompt: str, output_dir: str) -> bool:
        """Fluxo completo de criação de projeto."""
        try:
            # 1. Parse dos requisitos
            spec = self.parse_requirements(prompt)
            if not spec:
                return False
            
            # 2. Geração de código
            result = self.generate_code(spec)
            if not result:
                return False
            
            # 3. Validação
            if not self.validate_code(result):
                return False
            
            # 4. Deploy
            self.deploy_project(result, output_dir)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar projeto: {str(e)}")
            return False 