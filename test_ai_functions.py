import unittest
import sys
import os
from pathlib import Path
import json
import requests
from PIL import Image
import numpy as np

class TestAIFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuração inicial dos testes."""
        # Adiciona o diretório do ComfyUI ao PYTHONPATH
        comfy_path = Path("../ComfyUI-master").resolve()
        sys.path.append(str(comfy_path))
        
        # Configura diretório de testes
        cls.test_dir = Path("test_outputs")
        cls.test_dir.mkdir(exist_ok=True)
        
        # Inicia servidor
        cls.api_url = "http://localhost:5000"
    
    def test_01_chat_response(self):
        """Testa resposta do chat."""
        prompt = "Explique o que é Python em uma frase."
        response = self._send_chat_request(prompt)
        
        self.assertIsNotNone(response)
        self.assertIn("response", response)
        self.assertTrue(len(response["response"]) > 0)
    
    def test_02_code_generation(self):
        """Testa geração de código."""
        prompt = "Crie uma função Python que calcula o fatorial de um número."
        response = self._send_chat_request(prompt, type="programacao")
        
        self.assertIsNotNone(response)
        self.assertIn("response", response)
        self.assertIn("def", response["response"])
    
    def test_03_image_generation(self):
        """Testa geração de imagem."""
        workflow = {
            "prompt": "Um robô pintando um quadro",
            "type": "image_generation"
        }
        
        response = requests.post(
            f"{self.api_url}/api/process",
            json=workflow
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Verifica se a imagem foi gerada
        if "image_path" in result:
            img_path = Path(result["image_path"])
            self.assertTrue(img_path.exists())
            
            # Verifica se é uma imagem válida
            img = Image.open(img_path)
            self.assertGreater(img.size[0], 0)
            self.assertGreater(img.size[1], 0)
    
    def test_04_workflow_management(self):
        """Testa gerenciamento de workflows."""
        # Cria workflow
        workflow = {
            "name": "test_workflow",
            "prompt": "Teste de workflow",
            "nodes": {}
        }
        
        # Salva workflow
        response = requests.post(
            f"{self.api_url}/api/workflows",
            json=workflow
        )
        self.assertEqual(response.status_code, 200)
        
        # Lista workflows
        response = requests.get(f"{self.api_url}/api/workflows")
        self.assertEqual(response.status_code, 200)
        workflows = response.json()
        self.assertIn("test_workflow", [w["name"] for w in workflows])
    
    def test_05_file_editing(self):
        """Testa edição de arquivos."""
        test_file = self.test_dir / "test_code.py"
        
        # Cria arquivo
        code = "def test_function():\n    pass\n"
        test_file.write_text(code)
        
        # Edita arquivo via API
        edit_request = {
            "file": str(test_file),
            "changes": [
                {
                    "line": 2,
                    "content": "    return True\n"
                }
            ]
        }
        
        response = requests.post(
            f"{self.api_url}/api/edit",
            json=edit_request
        )
        self.assertEqual(response.status_code, 200)
        
        # Verifica mudanças
        new_code = test_file.read_text()
        self.assertIn("return True", new_code)
    
    def test_06_code_analysis(self):
        """Testa análise de código."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        response = self._send_chat_request(
            f"Analise este código e sugira melhorias: {code}",
            type="programacao"
        )
        
        self.assertIsNotNone(response)
        self.assertIn("response", response)
        self.assertTrue(len(response["response"]) > 0)
    
    def test_07_autonomous_assistant(self):
        """Testa assistente autônomo."""
        tasks = [
            "Crie um arquivo Python que implementa uma calculadora simples",
            "Adicione funções de multiplicação e divisão à calculadora",
            "Crie testes unitários para a calculadora"
        ]
        
        for task in tasks:
            response = self._send_chat_request(task)
            self.assertIsNotNone(response)
            self.assertIn("response", response)
    
    def _send_chat_request(self, message, type="chat"):
        """Auxiliar para enviar requisições ao chat."""
        response = requests.post(
            f"{self.api_url}/api/chat",
            json={"message": message, "type": type}
        )
        return response.json()
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes."""
        # Remove arquivos de teste
        if cls.test_dir.exists():
            for file in cls.test_dir.glob("*"):
                file.unlink()
            cls.test_dir.rmdir()

if __name__ == "__main__":
    unittest.main(verbosity=2) 