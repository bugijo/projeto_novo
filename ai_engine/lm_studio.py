import os
import json
import logging
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LMStudioInterface:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or self._get_default_model()
        self.api_url = "http://localhost:1234/v1"
        self.process = None
        self.cache = {}
        
    def _get_default_model(self) -> str:
        """Retorna o caminho do modelo DeepSeek-Coder."""
        models_dir = Path.home() / "AppData/Local/nomic.ai/LM Studio/models"
        for file in models_dir.glob("*deepseek*"):
            if file.suffix in ['.gguf', '.bin']:
                return str(file)
        return None
    
    def start_server(self) -> bool:
        """Inicia o servidor LM Studio."""
        if not self.model_path:
            logger.error("Modelo não encontrado")
            return False
            
        try:
            # Verifica se o LM Studio já está rodando
            try:
                response = requests.get(f"{self.api_url}/models")
                if response.status_code == 200:
                    logger.info("LM Studio já está rodando")
                    return True
            except:
                pass
            
            # Inicia o LM Studio
            lm_studio_path = Path.home() / "AppData/Local/Programs/LM Studio/LM Studio.exe"
            if not lm_studio_path.exists():
                logger.error("LM Studio não encontrado")
                return False
                
            self.process = subprocess.Popen([
                str(lm_studio_path),
                "--model", self.model_path,
                "--api-mode"
            ])
            
            # Aguarda o servidor iniciar
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.api_url}/models")
                    if response.status_code == 200:
                        logger.info("LM Studio iniciado com sucesso")
                        return True
                except:
                    time.sleep(1)
                    
            logger.error("Timeout ao iniciar LM Studio")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao iniciar LM Studio: {str(e)}")
            return False
    
    def stop_server(self):
        """Para o servidor LM Studio."""
        if self.process:
            self.process.terminate()
            self.process = None
    
    def generate(self, 
                prompt: str, 
                max_tokens: int = 2000,
                temperature: float = 0.7,
                top_p: float = 0.95,
                cache_key: str = None) -> Optional[str]:
        """Gera texto usando o LM Studio."""
        # Verifica cache
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            response = requests.post(
                f"{self.api_url}/completions",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": False
                },
                timeout=120  # Timeout maior para gerações longas
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["text"]
                
                # Salva no cache
                if cache_key:
                    self.cache[cache_key] = result
                    
                return result
            else:
                logger.error(f"Erro na API do LM Studio: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {str(e)}")
            return None
    
    def validate_code(self, code: str) -> Dict[str, any]:
        """Valida código usando o modelo."""
        system_prompt = """Você é um expert em revisão de código.
        Analise o código a seguir e retorne um JSON com:
        - erros: lista de erros encontrados
        - warnings: lista de warnings/sugestões
        - score: nota de 0 a 10
        - sugestões: lista de melhorias"""
        
        prompt = f"{system_prompt}\n\nCódigo:\n```\n{code}\n```\n\nAnálise:"
        result = self.generate(prompt, cache_key=f"validate_{hash(code)}")
        
        try:
            return json.loads(result)
        except:
            return {
                "erros": ["Erro ao parsear resultado da validação"],
                "warnings": [],
                "score": 0,
                "sugestões": []
            }
    
    def explain_code(self, code: str) -> str:
        """Gera explicação detalhada do código."""
        prompt = f"""Explique o seguinte código em detalhes:
        
        ```
        {code}
        ```
        
        Inclua:
        1. Visão geral do que o código faz
        2. Explicação de cada parte importante
        3. Possíveis problemas ou limitações
        4. Sugestões de melhoria"""
        
        return self.generate(prompt, cache_key=f"explain_{hash(code)}")
    
    def suggest_tests(self, code: str) -> List[str]:
        """Sugere casos de teste para o código."""
        prompt = f"""Gere casos de teste para o seguinte código:
        
        ```
        {code}
        ```
        
        Retorne um JSON com uma lista de testes, cada um contendo:
        - descrição: o que o teste verifica
        - código: o código do teste
        - tipo: unit/integration/e2e"""
        
        result = self.generate(prompt, cache_key=f"tests_{hash(code)}")
        
        try:
            return json.loads(result)
        except:
            return [] 