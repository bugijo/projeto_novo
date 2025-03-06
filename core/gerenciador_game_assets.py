import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import asyncio
import aiohttp

@dataclass
class PersonagemConfig:
    nome: str
    tipo: str  # humanóide, monstro, animal, etc
    atributos: Dict[str, float]  # força, agilidade, etc
    aparencia: Dict[str, str]  # cor do cabelo, altura, etc
    animacoes: List[str]  # idle, andar, correr, etc
    habilidades: List[Dict[str, any]]
    equipamentos: List[Dict[str, any]]
    
@dataclass
class CenarioConfig:
    nome: str
    tipo: str  # floresta, cidade, dungeon, etc
    dimensoes: Dict[str, int]  # largura, altura
    elementos: List[Dict[str, any]]  # árvores, prédios, etc
    clima: Dict[str, any]  # tipo de clima, efeitos
    iluminacao: Dict[str, any]  # tipo de luz, intensidade
    colisoes: List[Dict[str, any]]
    
@dataclass
class ItemConfig:
    nome: str
    tipo: str  # arma, armadura, consumível, etc
    atributos: Dict[str, float]
    aparencia: Dict[str, str]
    efeitos: List[Dict[str, any]]
    raridade: str
    valor: int

class GerenciadorGameAssets:
    def __init__(self):
        self.config = self._carregar_config()
        self.apis = {
            "openai": self.config["apis"]["openai"]["api_key"],
            "poly": self.config["apis"]["poly"]["api_key"],
            "sketchfab": self.config["apis"]["sketchfab"]["api_key"]
        }
        self.cache_dir = Path("assets/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _carregar_config(self) -> dict:
        """Carrega as configurações do gerenciador"""
        config_path = Path("config/game_assets_config.json")
        if not config_path.exists():
            return self._criar_config_padrao()
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def _criar_config_padrao(self) -> dict:
        """Cria uma configuração padrão"""
        config = {
            "apis": {
                "openai": {"api_key": "", "modelo": "gpt-4"},
                "poly": {"api_key": ""},
                "sketchfab": {"api_key": ""}
            },
            "recursos": {
                "personagens": {
                    "formatos": ["fbx", "gltf", "obj"],
                    "max_poligonos": 10000,
                    "texturas_max": 2048
                },
                "cenarios": {
                    "formatos": ["fbx", "gltf", "obj"],
                    "max_poligonos": 100000,
                    "texturas_max": 4096
                },
                "itens": {
                    "formatos": ["fbx", "gltf", "obj"],
                    "max_poligonos": 5000,
                    "texturas_max": 1024
                }
            },
            "otimizacao": {
                "compressao_texturas": True,
                "nivel_lod": 3,
                "batch_processing": True
            }
        }
        
        config_path = Path("config/game_assets_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
        return config

    async def criar_personagem(self, config: PersonagemConfig) -> Dict[str, any]:
        """Cria um novo personagem usando IA e APIs de modelos 3D"""
        # Gera descrição detalhada usando GPT
        descricao = await self._gerar_descricao_ia("personagem", config)
        
        # Busca ou gera modelo 3D
        modelo = await self._obter_modelo_3d("personagem", descricao)
        
        # Gera texturas e materiais
        texturas = await self._gerar_texturas(config.aparencia)
        
        # Gera animações
        animacoes = await self._gerar_animacoes(config.animacoes)
        
        return {
            "descricao": descricao,
            "modelo": modelo,
            "texturas": texturas,
            "animacoes": animacoes
        }

    async def criar_cenario(self, config: CenarioConfig) -> Dict[str, any]:
        """Cria um novo cenário"""
        # Gera descrição detalhada
        descricao = await self._gerar_descricao_ia("cenario", config)
        
        # Busca ou gera elementos do cenário
        elementos = []
        for elemento in config.elementos:
            modelo = await self._obter_modelo_3d("cenario", elemento)
            elementos.append(modelo)
            
        # Gera mapa de iluminação
        iluminacao = await self._gerar_iluminacao(config.iluminacao)
        
        # Gera efeitos de clima
        efeitos_clima = await self._gerar_efeitos_clima(config.clima)
        
        return {
            "descricao": descricao,
            "elementos": elementos,
            "iluminacao": iluminacao,
            "clima": efeitos_clima
        }

    async def criar_item(self, config: ItemConfig) -> Dict[str, any]:
        """Cria um novo item"""
        # Gera descrição detalhada
        descricao = await self._gerar_descricao_ia("item", config)
        
        # Busca ou gera modelo 3D
        modelo = await self._obter_modelo_3d("item", descricao)
        
        # Gera texturas e materiais
        texturas = await self._gerar_texturas(config.aparencia)
        
        # Gera efeitos visuais
        efeitos = await self._gerar_efeitos_visuais(config.efeitos)
        
        return {
            "descricao": descricao,
            "modelo": modelo,
            "texturas": texturas,
            "efeitos": efeitos
        }

    async def _gerar_descricao_ia(self, tipo: str, config: Union[PersonagemConfig, CenarioConfig, ItemConfig]) -> str:
        """Gera uma descrição detalhada usando IA"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.apis['openai']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config["apis"]["openai"]["modelo"],
                    "messages": [
                        {"role": "system", "content": f"Você é um especialista em design de {tipo}s para jogos."},
                        {"role": "user", "content": f"Crie uma descrição detalhada para um {tipo} com as seguintes características: {json.dumps(config.__dict__)}"}
                    ]
                }
            ) as response:
                data = await response.json()
                return data["choices"][0]["message"]["content"]

    async def _obter_modelo_3d(self, tipo: str, descricao: str) -> Dict[str, str]:
        """Busca ou gera um modelo 3D adequado"""
        # Primeiro tenta buscar no Sketchfab
        modelo = await self._buscar_sketchfab(tipo, descricao)
        if modelo:
            return modelo
            
        # Se não encontrar, tenta no Poly
        modelo = await self._buscar_poly(tipo, descricao)
        if modelo:
            return modelo
            
        # Se ainda não encontrar, gera um novo
        return await self._gerar_modelo_3d(tipo, descricao)

    async def _buscar_sketchfab(self, tipo: str, descricao: str) -> Optional[Dict[str, str]]:
        """Busca um modelo no Sketchfab"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.sketchfab.com/v3/search",
                headers={"Authorization": f"Bearer {self.apis['sketchfab']}"},
                params={
                    "type": "models",
                    "q": descricao,
                    "categories": tipo
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["results"]:
                        return {
                            "url": data["results"][0]["download_url"],
                            "formato": data["results"][0]["format"]
                        }
                return None

    async def _buscar_poly(self, tipo: str, descricao: str) -> Optional[Dict[str, str]]:
        """Busca um modelo no Poly"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://poly.googleapis.com/v1/assets",
                params={
                    "keywords": descricao,
                    "format": "OBJ",
                    "key": self.apis["poly"]
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["assets"]:
                        return {
                            "url": data["assets"][0]["formats"][0]["root"]["url"],
                            "formato": "obj"
                        }
                return None

    async def _gerar_modelo_3d(self, tipo: str, descricao: str) -> Dict[str, str]:
        """Gera um novo modelo 3D usando IA"""
        # Implementar integração com serviços de geração de modelos 3D
        # Por enquanto retorna um modelo de exemplo
        return {
            "url": f"assets/modelos/{tipo}_padrao.fbx",
            "formato": "fbx"
        }

    async def _gerar_texturas(self, config: Dict[str, str]) -> List[Dict[str, str]]:
        """Gera texturas para o modelo"""
        texturas = []
        for nome, valor in config.items():
            textura = await self._gerar_textura(nome, valor)
            texturas.append(textura)
        return texturas

    async def _gerar_textura(self, tipo: str, descricao: str) -> Dict[str, str]:
        """Gera uma textura específica"""
        # Implementar geração de texturas
        return {
            "tipo": tipo,
            "url": f"assets/texturas/{tipo}_padrao.png"
        }

    async def _gerar_animacoes(self, tipos: List[str]) -> List[Dict[str, str]]:
        """Gera animações para o modelo"""
        animacoes = []
        for tipo in tipos:
            animacao = await self._gerar_animacao(tipo)
            animacoes.append(animacao)
        return animacoes

    async def _gerar_animacao(self, tipo: str) -> Dict[str, str]:
        """Gera uma animação específica"""
        # Implementar geração de animações
        return {
            "tipo": tipo,
            "url": f"assets/animacoes/{tipo}_padrao.fbx"
        }

    async def _gerar_iluminacao(self, config: Dict[str, any]) -> Dict[str, any]:
        """Gera mapa de iluminação para o cenário"""
        # Implementar geração de iluminação
        return {
            "mapa_luz": f"assets/iluminacao/padrao.hdr",
            "config": config
        }

    async def _gerar_efeitos_clima(self, config: Dict[str, any]) -> List[Dict[str, str]]:
        """Gera efeitos de clima"""
        # Implementar geração de efeitos
        return [{
            "tipo": config["tipo"],
            "particulas": f"assets/efeitos/{config['tipo']}_particulas.vfx"
        }]

    async def _gerar_efeitos_visuais(self, efeitos: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """Gera efeitos visuais para itens"""
        resultados = []
        for efeito in efeitos:
            resultado = await self._gerar_efeito_visual(efeito)
            resultados.append(resultado)
        return resultados

    async def _gerar_efeito_visual(self, config: Dict[str, any]) -> Dict[str, str]:
        """Gera um efeito visual específico"""
        # Implementar geração de efeitos
        return {
            "tipo": config["tipo"],
            "url": f"assets/efeitos/{config['tipo']}_padrao.vfx"
        }

    def otimizar_asset(self, asset: Dict[str, any]) -> Dict[str, any]:
        """Otimiza um asset para uso mobile"""
        # Implementar otimização de assets
        return asset

    def exportar_asset(self, asset: Dict[str, any], formato: str) -> str:
        """Exporta um asset para o formato especificado"""
        # Implementar exportação
        return f"assets/exportados/{asset['nome']}.{formato}" 