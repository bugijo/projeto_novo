import requests
import json
import time
import os

def test_generations():
    """Testa todas as funcionalidades de geração."""
    BASE_URL = "http://localhost:5000/api"
    
    # Login
    print("Fazendo login...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Teste de geração de logo
    print("\nTestando geração de logo...")
    response = requests.post(
        f"{BASE_URL}/generate/image",
        headers=headers,
        json={
            "prompt": "Crie um logo moderno para uma empresa de tecnologia chamada TechAI",
            "type": "logo"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Teste de geração de cenário de jogo
    print("\nTestando geração de cenário de jogo...")
    response = requests.post(
        f"{BASE_URL}/generate/image",
        headers=headers,
        json={
            "prompt": "Crie um cenário de jogo cyberpunk com prédios neon e carros voadores",
            "type": "game_scene"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Teste de geração de personagem 3D
    print("\nTestando geração de personagem 3D...")
    response = requests.post(
        f"{BASE_URL}/generate/3d",
        headers=headers,
        json={
            "prompt": "Crie um personagem 3D estilo anime com cabelo azul e armadura futurista",
            "type": "character"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Teste de geração de vídeo
    print("\nTestando geração de vídeo...")
    response = requests.post(
        f"{BASE_URL}/generate/video",
        headers=headers,
        json={
            "prompt": "Crie uma animação de uma nave espacial decolando",
            "duration": 5
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Teste de geração de código
    print("\nTestando geração de código...")
    response = requests.post(
        f"{BASE_URL}/generate/code",
        headers=headers,
        json={
            "prompt": "Crie uma classe Python para um jogo de RPG com sistema de inventário",
            "language": "python"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Teste de workflow completo
    print("\nTestando geração de workflow completo...")
    response = requests.post(
        f"{BASE_URL}/generate/workflow",
        headers=headers,
        json={
            "prompt": """
            Crie um jogo simples com:
            - Um personagem 3D
            - Um cenário cyberpunk
            - Sistema de inventário
            - Música de fundo
            - Interface do usuário
            """,
            "type": "game"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Resposta inicial: {result}")
    
    if "task_id" in result:
        print("\nAcompanhando progresso do workflow...")
        while True:
            status_response = requests.get(
                f"{BASE_URL}/task/{result['task_id']}",
                headers=headers
            )
            status = status_response.json()
            print(f"Status: {status['status']}")
            
            if status["status"] in ["completed", "failed"]:
                print(f"Resultado final: {status}")
                break
            time.sleep(1)

if __name__ == "__main__":
    test_generations() 