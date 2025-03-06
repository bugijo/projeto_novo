import unittest
import requests
import json
import os
from PIL import Image
import time

class TestGenerationFeatures(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api"
    
    def setUp(self):
        # Configurar autenticação
        response = requests.post(f"{self.BASE_URL}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.token = response.json()["token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Criar diretório para outputs
        self.output_dir = "test_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_image_generation(self):
        """Testa geração de imagens"""
        # Teste de geração de logo
        logo_prompt = "Crie um logo moderno para uma empresa de tecnologia chamada TechAI"
        response = requests.post(
            f"{self.BASE_URL}/generate/image",
            headers=self.headers,
            json={"prompt": logo_prompt, "type": "logo"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("image_url" in result)
        self.assertTrue(os.path.exists(result["image_url"]))
        
        # Teste de geração de cenário de jogo
        game_prompt = "Crie um cenário de jogo cyberpunk com prédios neon e carros voadores"
        response = requests.post(
            f"{self.BASE_URL}/generate/image",
            headers=self.headers,
            json={"prompt": game_prompt, "type": "game_scene"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("image_url" in result)
        self.assertTrue(os.path.exists(result["image_url"]))
    
    def test_3d_model_generation(self):
        """Testa geração de modelos 3D"""
        # Teste de geração de personagem 3D
        character_prompt = "Crie um personagem 3D estilo anime com cabelo azul e armadura futurista"
        response = requests.post(
            f"{self.BASE_URL}/generate/3d",
            headers=self.headers,
            json={"prompt": character_prompt, "type": "character"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("model_url" in result)
        self.assertTrue(os.path.exists(result["model_url"]))
        
        # Teste de geração de objeto 3D
        object_prompt = "Crie uma espada mágica com cristais brilhantes"
        response = requests.post(
            f"{self.BASE_URL}/generate/3d",
            headers=self.headers,
            json={"prompt": object_prompt, "type": "object"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("model_url" in result)
        self.assertTrue(os.path.exists(result["model_url"]))
    
    def test_video_generation(self):
        """Testa geração de vídeos"""
        # Teste de geração de vídeo curto
        video_prompt = "Crie uma animação de uma nave espacial decolando"
        response = requests.post(
            f"{self.BASE_URL}/generate/video",
            headers=self.headers,
            json={"prompt": video_prompt, "duration": 10}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("video_url" in result)
        self.assertTrue(os.path.exists(result["video_url"]))
    
    def test_code_generation(self):
        """Testa geração de código"""
        # Teste de geração de código Python
        code_prompt = "Crie uma classe Python para um jogo de RPG com sistema de inventário"
        response = requests.post(
            f"{self.BASE_URL}/generate/code",
            headers=self.headers,
            json={"prompt": code_prompt, "language": "python"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("code" in result)
        self.assertTrue("language" in result)
        
    def test_workflow_generation(self):
        """Testa geração de workflows complexos"""
        # Teste de geração de jogo completo
        game_prompt = """
        Crie um jogo simples com:
        - Um personagem 3D
        - Um cenário cyberpunk
        - Sistema de inventário
        - Música de fundo
        - Interface do usuário
        """
        response = requests.post(
            f"{self.BASE_URL}/generate/workflow",
            headers=self.headers,
            json={"prompt": game_prompt, "type": "game"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue("task_id" in result)
        
        # Acompanha o progresso do workflow
        task_id = result["task_id"]
        while True:
            status_response = requests.get(
                f"{self.BASE_URL}/task/{task_id}",
                headers=self.headers
            )
            status = status_response.json()
            if status["status"] in ["completed", "failed"]:
                break
            time.sleep(1)
        
        self.assertEqual(status["status"], "completed")
        self.assertTrue("outputs" in status)
        self.assertTrue("model_url" in status["outputs"])
        self.assertTrue("scene_url" in status["outputs"])
        self.assertTrue("code_url" in status["outputs"])
        self.assertTrue("ui_url" in status["outputs"])
    
    def tearDown(self):
        # Limpar arquivos gerados
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)

if __name__ == "__main__":
    unittest.main() 