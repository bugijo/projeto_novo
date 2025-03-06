import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import pyautogui
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class PerfilUsuario:
    def __init__(self):
        self.dados = self._carregar_dados()
        self.historico_atividades = []
        self.driver = None
        
    def _carregar_dados(self) -> dict:
        """Carrega os dados do perfil do usuário"""
        arquivo = Path("data/perfil_usuario.json")
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "preferencias": {
                "series": [],
                "filmes": {
                    "generos_favoritos": [],
                    "assistidos": [],
                    "avaliados": {}
                },
                "musicas": {
                    "generos_favoritos": [],
                    "artistas_favoritos": [],
                    "playlists": {}
                },
                "jogos": {
                    "generos_favoritos": [],
                    "jogos_instalados": [],
                    "tempo_jogado": {}
                },
                "apps": {
                    "mais_usados": {},
                    "configuracoes": {}
                },
                "navegador": {
                    "sites_frequentes": {},
                    "bookmarks": []
                }
            },
            "hobbies": [],
            "rotinas": {},
            "configuracoes_pessoais": {
                "tema": "dark",
                "notificacoes": True,
                "privacidade": {
                    "compartilhar_dados": False,
                    "modo_anonimo": False
                }
            }
        }
    
    def salvar_dados(self):
        """Salva os dados do perfil"""
        arquivo = Path("data/perfil_usuario.json")
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)
    
    def registrar_atividade(self, tipo: str, dados: dict):
        """Registra uma nova atividade do usuário"""
        atividade = {
            "tipo": tipo,
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
        self.historico_atividades.append(atividade)
        self._atualizar_preferencias(tipo, dados)
    
    def _atualizar_preferencias(self, tipo: str, dados: dict):
        """Atualiza as preferências baseado nas atividades"""
        if tipo == "midia":
            if dados.get("categoria") == "serie":
                self.dados["preferencias"]["series"].append(dados["nome"])
            elif dados.get("categoria") == "filme":
                self.dados["preferencias"]["filmes"]["assistidos"].append(dados["nome"])
        elif tipo == "musica":
            if "artista" in dados:
                self.dados["preferencias"]["musicas"]["artistas_favoritos"].append(dados["artista"])
        elif tipo == "jogo":
            if "nome" in dados:
                if dados["nome"] not in self.dados["preferencias"]["jogos"]["jogos_instalados"]:
                    self.dados["preferencias"]["jogos"]["jogos_instalados"].append(dados["nome"])
        elif tipo == "app":
            app_nome = dados.get("nome")
            if app_nome:
                self.dados["preferencias"]["apps"]["mais_usados"][app_nome] = \
                    self.dados["preferencias"]["apps"]["mais_usados"].get(app_nome, 0) + 1
        
        self.salvar_dados()
    
    def sugerir_midia(self, tipo: str) -> List[str]:
        """Sugere mídia baseada nas preferências"""
        if tipo == "filme":
            generos = self.dados["preferencias"]["filmes"]["generos_favoritos"]
            # Aqui você pode integrar com APIs de recomendação de filmes
            return [f"Filme do gênero {g}" for g in generos]
        elif tipo == "serie":
            return self.dados["preferencias"]["series"][-5:]  # últimas 5 séries
        return []
    
    def iniciar_navegador(self):
        """Inicia uma sessão do navegador automatizada"""
        if not self.driver:
            self.driver = webdriver.Chrome()  # ou outro navegador de sua preferência
    
    def fechar_navegador(self):
        """Fecha a sessão do navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def navegar_site(self, url: str, interagir: bool = False):
        """Navega para um site e opcionalmente interage com ele"""
        try:
            if not self.driver:
                self.iniciar_navegador()
            self.driver.get(url)
            if interagir:
                # Aqui você pode adicionar interações específicas
                pass
        except Exception as e:
            print(f"Erro ao navegar: {e}")
    
    def digitar_texto(self, texto: str, intervalo: float = 0.1):
        """Digita um texto simulando digitação humana"""
        pyautogui.write(texto, interval=intervalo)
    
    def mover_mouse(self, x: int, y: int, duracao: float = 0.5):
        """Move o mouse para uma posição específica"""
        pyautogui.moveTo(x, y, duration=duracao)
    
    def clicar(self, x: Optional[int] = None, y: Optional[int] = None):
        """Clica em uma posição específica ou na posição atual do mouse"""
        if x is not None and y is not None:
            pyautogui.click(x, y)
        else:
            pyautogui.click()
    
    def enviar_mensagem(self, plataforma: str, destinatario: str, mensagem: str):
        """Envia uma mensagem em uma plataforma específica"""
        if plataforma == "whatsapp":
            # Implementar lógica para WhatsApp Web
            url = f"https://web.whatsapp.com/send?phone={destinatario}&text={mensagem}"
            self.navegar_site(url)
        elif plataforma == "telegram":
            # Implementar lógica para Telegram Web
            pass
        # Adicionar outras plataformas conforme necessário
    
    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        self.salvar_dados()
        self.fechar_navegador() 