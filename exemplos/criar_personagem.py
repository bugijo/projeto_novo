import asyncio
from core.gerenciador_game_assets import GerenciadorGameAssets, PersonagemConfig

async def criar_personagem_exemplo():
    print("=== Criando Personagem de Exemplo ===\n")
    
    # Inicializa o gerenciador
    gerenciador = GerenciadorGameAssets()
    
    # Configura o personagem
    personagem_config = PersonagemConfig(
        nome="Guerreiro Místico",
        tipo="humanóide",
        atributos={
            "força": 18,
            "agilidade": 14,
            "resistência": 16,
            "inteligência": 12,
            "magia": 10
        },
        aparencia={
            "altura": "1.85m",
            "corpo": "atlético",
            "cabelo": "preto longo com tranças",
            "olhos": "azuis brilhantes",
            "pele": "morena",
            "vestimenta": "armadura de couro com detalhes mágicos"
        },
        animacoes=[
            "idle_combate",
            "andar_normal",
            "correr",
            "ataque_espada",
            "magia_elemental",
            "defender",
            "pular",
            "morrer"
        ],
        habilidades=[
            {
                "nome": "Lâmina Flamejante",
                "tipo": "ataque",
                "elemento": "fogo",
                "dano": 25,
                "custo_mana": 20,
                "efeito": "incendiar"
            },
            {
                "nome": "Escudo Místico",
                "tipo": "defesa",
                "elemento": "luz",
                "bloqueio": 20,
                "duração": 15,
                "efeito": "reflexão_magica"
            }
        ],
        equipamentos=[
            {
                "tipo": "arma",
                "nome": "Espada Rúnica",
                "dano": 18,
                "material": "aço élfico",
                "encantamentos": ["fogo", "penetração"]
            },
            {
                "tipo": "armadura",
                "nome": "Armadura de Couro Mística",
                "defesa": 12,
                "material": "couro de dragão",
                "encantamentos": ["proteção_mágica", "regeneração"]
            }
        ]
    )
    
    # Cria o personagem
    print("Criando personagem...")
    personagem = await gerenciador.criar_personagem(personagem_config)
    
    # Exibe informações do personagem criado
    print("\nPersonagem criado com sucesso!")
    print(f"\nDescrição: {personagem['descricao']}")
    print(f"\nModelo 3D: {personagem['modelo']}")
    print("\nTexturas:")
    for textura in personagem['texturas']:
        print(f"- {textura['tipo']}: {textura['url']}")
    print("\nAnimações:")
    for animacao in personagem['animacoes']:
        print(f"- {animacao['tipo']}: {animacao['url']}")
    
    # Otimiza para mobile
    print("\nOtimizando para dispositivos móveis...")
    personagem_otimizado = gerenciador.otimizar_asset(personagem)
    
    # Exporta o personagem
    print("\nExportando personagem...")
    caminho_export = gerenciador.exportar_asset(personagem_otimizado, "gltf")
    print(f"\nPersonagem exportado para: {caminho_export}")

if __name__ == "__main__":
    asyncio.run(criar_personagem_exemplo()) 