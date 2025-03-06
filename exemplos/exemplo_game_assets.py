import asyncio
from core.gerenciador_game_assets import (
    GerenciadorGameAssets,
    PersonagemConfig,
    CenarioConfig,
    ItemConfig
)

async def exemplo_criacao_assets():
    """Exemplo de criação de assets para um jogo"""
    
    print("=== Iniciando criação de assets para o jogo ===\n")
    
    # Inicializa o gerenciador
    gerenciador = GerenciadorGameAssets()
    
    # 1. Criar um personagem
    print("1. Criando personagem principal...")
    personagem_config = PersonagemConfig(
        nome="Guerreiro",
        tipo="humanóide",
        atributos={
            "força": 15,
            "agilidade": 12,
            "resistência": 14,
            "inteligência": 8
        },
        aparencia={
            "altura": "1.80m",
            "corpo": "musculoso",
            "cabelo": "preto longo",
            "olhos": "castanhos",
            "pele": "bronzeada",
            "armadura": "peitoral de ferro"
        },
        animacoes=[
            "idle",
            "andar",
            "correr",
            "atacar_espada",
            "defender_escudo",
            "pular",
            "morrer"
        ],
        habilidades=[
            {
                "nome": "Golpe Giratório",
                "tipo": "ataque",
                "dano": 20,
                "custo": 15,
                "efeito": "dano em área"
            },
            {
                "nome": "Escudo Protetor",
                "tipo": "defesa",
                "bloqueio": 15,
                "duração": 10,
                "efeito": "aumenta defesa"
            }
        ],
        equipamentos=[
            {
                "tipo": "arma",
                "nome": "Espada Longa",
                "dano": 12,
                "material": "aço"
            },
            {
                "tipo": "escudo",
                "nome": "Escudo de Ferro",
                "defesa": 8,
                "material": "ferro"
            }
        ]
    )
    
    personagem = await gerenciador.criar_personagem(personagem_config)
    print(f"Personagem criado: {personagem['descricao']}\n")
    
    # 2. Criar um cenário
    print("2. Criando cenário da floresta...")
    cenario_config = CenarioConfig(
        nome="Floresta Mística",
        tipo="floresta",
        dimensoes={
            "largura": 1000,
            "altura": 1000
        },
        elementos=[
            {
                "tipo": "árvore",
                "quantidade": 100,
                "variações": 3,
                "distribuição": "aleatória"
            },
            {
                "tipo": "pedra",
                "quantidade": 50,
                "variações": 2,
                "distribuição": "agrupada"
            },
            {
                "tipo": "arbusto",
                "quantidade": 200,
                "variações": 4,
                "distribuição": "aleatória"
            },
            {
                "tipo": "rio",
                "pontos": [
                    {"x": 0, "y": 500},
                    {"x": 1000, "y": 450}
                ],
                "largura": 20
            }
        ],
        clima={
            "tipo": "ensolarado",
            "intensidade": 0.8,
            "partículas": ["folhas", "pólen"],
            "vento": {"direção": "nordeste", "força": 0.3}
        },
        iluminacao={
            "tipo": "diurna",
            "intensidade": 1.0,
            "cor": "#FFF5E6",
            "sombras": True,
            "ambient_occlusion": True
        },
        colisoes=[
            {
                "tipo": "árvore",
                "forma": "cilindro",
                "raio": 1.0,
                "altura": 10.0
            },
            {
                "tipo": "pedra",
                "forma": "caixa",
                "dimensoes": {"x": 2.0, "y": 1.5, "z": 2.0}
            },
            {
                "tipo": "rio",
                "forma": "malha",
                "profundidade": 2.0
            }
        ]
    )
    
    cenario = await gerenciador.criar_cenario(cenario_config)
    print(f"Cenário criado: {cenario['descricao']}\n")
    
    # 3. Criar um item
    print("3. Criando item especial...")
    item_config = ItemConfig(
        nome="Espada de Fogo",
        tipo="arma",
        atributos={
            "dano": 25,
            "velocidade": 1.2,
            "crítico": 0.15
        },
        aparencia={
            "material": "aço negro",
            "lâmina": "rúnica",
            "empunhadura": "couro vermelho",
            "gema": "rubi"
        },
        efeitos=[
            {
                "tipo": "fogo",
                "dano": 5,
                "duração": 3,
                "partículas": "chamas",
                "luz": {"cor": "#FF4400", "intensidade": 0.8}
            }
        ],
        raridade="épico",
        valor=1000
    )
    
    item = await gerenciador.criar_item(item_config)
    print(f"Item criado: {item['descricao']}\n")
    
    # 4. Otimizar assets para mobile
    print("4. Otimizando assets para mobile...")
    personagem_otimizado = gerenciador.otimizar_asset(personagem)
    cenario_otimizado = gerenciador.otimizar_asset(cenario)
    item_otimizado = gerenciador.otimizar_asset(item)
    
    # 5. Exportar assets
    print("5. Exportando assets...")
    personagem_path = gerenciador.exportar_asset(personagem_otimizado, "gltf")
    cenario_path = gerenciador.exportar_asset(cenario_otimizado, "gltf")
    item_path = gerenciador.exportar_asset(item_otimizado, "gltf")
    
    print(f"""
Assets exportados:
- Personagem: {personagem_path}
- Cenário: {cenario_path}
- Item: {item_path}
""")
    
    print("=== Criação de assets concluída ===")

if __name__ == "__main__":
    asyncio.run(exemplo_criacao_assets()) 