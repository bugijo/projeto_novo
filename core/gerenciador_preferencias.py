from dataclasses import dataclass
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime

@dataclass
class PreferenciasUsuario:
    tema: str = "dark"
    idioma: str = "pt-BR"
    notificacoes_ativas: bool = True
    volume: float = 1.0
    taxa_fala: int = 200
    voz_id: Optional[str] = None
    avatar: str = "default"

@dataclass
class PreferenciasMidia:
    series_favoritas: List[str] = None
    filmes_favoritos: List[str] = None
    generos_preferidos: List[str] = None
    plataformas: List[str] = None
    avaliacoes: Dict[str, float] = None
    
    def __post_init__(self):
        self.series_favoritas = self.series_favoritas or []
        self.filmes_favoritos = self.filmes_favoritos or []
        self.generos_preferidos = self.generos_preferidos or []
        self.plataformas = self.plataformas or []
        self.avaliacoes = self.avaliacoes or {}

@dataclass
class PreferenciasMusica:
    artistas_favoritos: List[str] = None
    generos_preferidos: List[str] = None
    playlists: Dict[str, List[str]] = None
    plataforma_preferida: str = "spotify"
    
    def __post_init__(self):
        self.artistas_favoritos = self.artistas_favoritos or []
        self.generos_preferidos = self.generos_preferidos or []
        self.playlists = self.playlists or {}

class GerenciadorPreferencias:
    def __init__(self):
        self.preferencias_usuario = PreferenciasUsuario()
        self.preferencias_midia = PreferenciasMidia()
        self.preferencias_musica = PreferenciasMusica()
        self.historico_interacoes = []
        self.carregar_preferencias()
    
    def carregar_preferencias(self):
        """Carrega as preferências do arquivo"""
        arquivo = Path("data/preferencias.json")
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
                # Carrega preferências do usuário
                for key, value in dados.get("usuario", {}).items():
                    if hasattr(self.preferencias_usuario, key):
                        setattr(self.preferencias_usuario, key, value)
                
                # Carrega preferências de mídia
                for key, value in dados.get("midia", {}).items():
                    if hasattr(self.preferencias_midia, key):
                        setattr(self.preferencias_midia, key, value)
                
                # Carrega preferências de música
                for key, value in dados.get("musica", {}).items():
                    if hasattr(self.preferencias_musica, key):
                        setattr(self.preferencias_musica, key, value)
                
                # Carrega histórico
                self.historico_interacoes = dados.get("historico", [])
    
    def salvar_preferencias(self):
        """Salva as preferências em arquivo"""
        dados = {
            "usuario": self.preferencias_usuario.__dict__,
            "midia": self.preferencias_midia.__dict__,
            "musica": self.preferencias_musica.__dict__,
            "historico": self.historico_interacoes
        }
        
        arquivo = Path("data/preferencias.json")
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    
    def registrar_interacao(self, tipo: str, dados: dict):
        """Registra uma nova interação do usuário"""
        interacao = {
            "tipo": tipo,
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
        self.historico_interacoes.append(interacao)
        self._atualizar_preferencias(tipo, dados)
        self.salvar_preferencias()
    
    def _atualizar_preferencias(self, tipo: str, dados: dict):
        """Atualiza as preferências baseado na interação"""
        if tipo == "midia":
            if dados.get("tipo") == "serie":
                if dados["nome"] not in self.preferencias_midia.series_favoritas:
                    self.preferencias_midia.series_favoritas.append(dados["nome"])
            elif dados.get("tipo") == "filme":
                if dados["nome"] not in self.preferencias_midia.filmes_favoritos:
                    self.preferencias_midia.filmes_favoritos.append(dados["nome"])
            
            if "genero" in dados:
                if dados["genero"] not in self.preferencias_midia.generos_preferidos:
                    self.preferencias_midia.generos_preferidos.append(dados["genero"])
            
            if "avaliacao" in dados:
                self.preferencias_midia.avaliacoes[dados["nome"]] = dados["avaliacao"]
        
        elif tipo == "musica":
            if "artista" in dados:
                if dados["artista"] not in self.preferencias_musica.artistas_favoritos:
                    self.preferencias_musica.artistas_favoritos.append(dados["artista"])
            
            if "genero" in dados:
                if dados["genero"] not in self.preferencias_musica.generos_preferidos:
                    self.preferencias_musica.generos_preferidos.append(dados["genero"])
            
            if "playlist" in dados:
                nome_playlist = dados["playlist"]
                musica = dados.get("musica")
                if musica:
                    if nome_playlist not in self.preferencias_musica.playlists:
                        self.preferencias_musica.playlists[nome_playlist] = []
                    if musica not in self.preferencias_musica.playlists[nome_playlist]:
                        self.preferencias_musica.playlists[nome_playlist].append(musica)
    
    def obter_recomendacoes(self, tipo: str) -> List[str]:
        """Retorna recomendações baseadas nas preferências"""
        if tipo == "serie":
            # Implementar lógica de recomendação de séries
            return self.preferencias_midia.series_favoritas[-5:]  # Últimas 5 séries
        
        elif tipo == "filme":
            # Implementar lógica de recomendação de filmes
            generos = self.preferencias_midia.generos_preferidos
            return [f"Filme do gênero {g}" for g in generos[:3]]  # 3 gêneros mais recentes
        
        elif tipo == "musica":
            # Implementar lógica de recomendação de músicas
            artistas = self.preferencias_musica.artistas_favoritos
            return [f"Músicas de {a}" for a in artistas[-3:]]  # 3 artistas mais recentes
        
        return []
    
    def atualizar_preferencia_usuario(self, chave: str, valor: any):
        """Atualiza uma preferência específica do usuário"""
        if hasattr(self.preferencias_usuario, chave):
            setattr(self.preferencias_usuario, chave, valor)
            self.salvar_preferencias()
            return True
        return False
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas sobre as preferências do usuário"""
        return {
            "total_series": len(self.preferencias_midia.series_favoritas),
            "total_filmes": len(self.preferencias_midia.filmes_favoritos),
            "total_artistas": len(self.preferencias_musica.artistas_favoritos),
            "total_playlists": len(self.preferencias_musica.playlists),
            "generos_favoritos": {
                "midia": self.preferencias_midia.generos_preferidos[:5],
                "musica": self.preferencias_musica.generos_preferidos[:5]
            },
            "total_interacoes": len(self.historico_interacoes)
        }
    
    def __del__(self):
        """Salva as preferências antes de destruir o objeto"""
        self.salvar_preferencias() 