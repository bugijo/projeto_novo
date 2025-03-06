import pyautogui
import keyboard
import mouse
import win32gui
import win32con
import win32api
import win32process
import psutil
import subprocess
import os
import json
from pathlib import Path
import time
import logging
from typing import Optional, Dict, List, Tuple, Union

class AutomacaoAvancada:
    def __init__(self):
        # Configurações de segurança
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # Carrega configurações
        self.config = self._carregar_configuracoes()
        
        # Inicializa logger
        self._configurar_logger()
        
        # Dicionário de atalhos registrados
        self.atalhos = {}
        
        # Lista de macros gravadas
        self.macros = self._carregar_macros()
        
        # Estado da gravação de macro
        self.gravando_macro = False
        self.macro_atual = []
        
        # Monitora janelas
        self.janelas_monitoradas = set()

    def _carregar_configuracoes(self) -> dict:
        """Carrega configurações de automação"""
        config_path = Path("config/automacao.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "delay_padrao": 0.5,
            "nivel_seguranca": "alto",
            "teclas_proibidas": ["win", "alt+f4", "ctrl+alt+del"],
            "apps_protegidos": ["chrome.exe", "explorer.exe"],
            "diretorio_macros": "macros"
        }

    def _configurar_logger(self):
        """Configura o sistema de logging"""
        self.logger = logging.getLogger("automacao")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("logs/automacao.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _carregar_macros(self) -> Dict[str, List[dict]]:
        """Carrega macros salvas"""
        macro_path = Path(self.config["diretorio_macros"])
        macros = {}
        
        if macro_path.exists():
            for arquivo in macro_path.glob("*.json"):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    macros[arquivo.stem] = json.load(f)
        
        return macros

    def salvar_macro(self, nome: str, acoes: List[dict]):
        """Salva uma macro em arquivo"""
        macro_path = Path(self.config["diretorio_macros"]) / f"{nome}.json"
        macro_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(macro_path, 'w', encoding='utf-8') as f:
            json.dump(acoes, f, indent=4)
        
        self.macros[nome] = acoes
        self.logger.info(f"Macro '{nome}' salva com sucesso")

    def iniciar_gravacao_macro(self):
        """Inicia a gravação de uma macro"""
        if not self.gravando_macro:
            self.gravando_macro = True
            self.macro_atual = []
            self.logger.info("Iniciando gravação de macro")
            return True
        return False

    def parar_gravacao_macro(self, nome: str) -> bool:
        """Para a gravação da macro atual"""
        if self.gravando_macro:
            self.gravando_macro = False
            if self.macro_atual:
                self.salvar_macro(nome, self.macro_atual)
                self.macro_atual = []
                return True
        return False

    def executar_macro(self, nome: str) -> bool:
        """Executa uma macro salva"""
        if nome not in self.macros:
            self.logger.error(f"Macro '{nome}' não encontrada")
            return False
        
        try:
            for acao in self.macros[nome]:
                self._executar_acao(acao)
            self.logger.info(f"Macro '{nome}' executada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao executar macro '{nome}': {e}")
            return False

    def _executar_acao(self, acao: dict):
        """Executa uma ação específica"""
        tipo = acao.get("tipo")
        params = acao.get("params", {})
        
        if tipo == "mouse_mover":
            pyautogui.moveTo(**params)
        elif tipo == "mouse_clicar":
            pyautogui.click(**params)
        elif tipo == "tecla_pressionar":
            keyboard.press_and_release(params["tecla"])
        elif tipo == "digitar":
            pyautogui.write(params["texto"], interval=params.get("intervalo", 0.1))
        elif tipo == "esperar":
            time.sleep(params["tempo"])
        elif tipo == "executar_programa":
            self.executar_programa(**params)

    def registrar_atalho(self, teclas: str, callback: callable) -> bool:
        """Registra um atalho de teclado"""
        try:
            if teclas not in self.config["teclas_proibidas"]:
                keyboard.add_hotkey(teclas, callback)
                self.atalhos[teclas] = callback
                self.logger.info(f"Atalho '{teclas}' registrado com sucesso")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao registrar atalho '{teclas}': {e}")
            return False

    def remover_atalho(self, teclas: str) -> bool:
        """Remove um atalho registrado"""
        try:
            if teclas in self.atalhos:
                keyboard.remove_hotkey(teclas)
                del self.atalhos[teclas]
                self.logger.info(f"Atalho '{teclas}' removido com sucesso")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao remover atalho '{teclas}': {e}")
            return False

    def executar_programa(self, caminho: str, argumentos: Optional[List[str]] = None, 
                         aguardar: bool = False) -> Optional[subprocess.Popen]:
        """Executa um programa"""
        try:
            processo = subprocess.Popen([caminho] + (argumentos or []))
            if aguardar:
                processo.wait()
            self.logger.info(f"Programa '{caminho}' executado com sucesso")
            return processo
        except Exception as e:
            self.logger.error(f"Erro ao executar programa '{caminho}': {e}")
            return None

    def encontrar_janela(self, titulo: str) -> Optional[int]:
        """Encontra uma janela pelo título"""
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                texto = win32gui.GetWindowText(hwnd)
                if titulo.lower() in texto.lower():
                    extra.append(hwnd)
        
        handles = []
        win32gui.EnumWindows(callback, handles)
        return handles[0] if handles else None

    def focar_janela(self, handle: int) -> bool:
        """Foca uma janela específica"""
        try:
            if win32gui.IsIconic(handle):  # Minimizada
                win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(handle)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao focar janela {handle}: {e}")
            return False

    def monitorar_janela(self, titulo: str, callback: callable):
        """Monitora mudanças em uma janela específica"""
        handle = self.encontrar_janela(titulo)
        if handle:
            self.janelas_monitoradas.add(handle)
            
            def monitor():
                while handle in self.janelas_monitoradas:
                    if not win32gui.IsWindow(handle):
                        callback("fechada")
                        self.janelas_monitoradas.remove(handle)
                        break
                    time.sleep(1)
            
            import threading
            threading.Thread(target=monitor, daemon=True).start()
            return True
        return False

    def capturar_regiao(self, x: int, y: int, largura: int, altura: int) -> Optional[Image]:
        """Captura uma região específica da tela"""
        try:
            return pyautogui.screenshot(region=(x, y, largura, altura))
        except Exception as e:
            self.logger.error(f"Erro ao capturar região: {e}")
            return None

    def mover_janela(self, handle: int, x: int, y: int, largura: Optional[int] = None, 
                     altura: Optional[int] = None) -> bool:
        """Move e/ou redimensiona uma janela"""
        try:
            if largura is None or altura is None:
                # Apenas move
                win32gui.SetWindowPos(handle, 0, x, y, 0, 0, 
                                    win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            else:
                # Move e redimensiona
                win32gui.SetWindowPos(handle, 0, x, y, largura, altura, 
                                    win32con.SWP_NOZORDER)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao mover/redimensionar janela {handle}: {e}")
            return False

    def listar_processos(self) -> List[Dict[str, Union[str, int, float]]]:
        """Lista todos os processos em execução"""
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processos.append({
                    "pid": info['pid'],
                    "nome": info['name'],
                    "cpu": info['cpu_percent'],
                    "memoria": info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processos

    def encerrar_processo(self, pid: int) -> bool:
        """Encerra um processo pelo PID"""
        try:
            processo = psutil.Process(pid)
            if processo.name() not in self.config["apps_protegidos"]:
                processo.terminate()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao encerrar processo {pid}: {e}")
            return False

    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        # Remove todos os atalhos registrados
        for teclas in list(self.atalhos.keys()):
            self.remover_atalho(teclas)
        
        # Para monitoramento de janelas
        self.janelas_monitoradas.clear() 