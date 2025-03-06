import pyautogui
import keyboard
import mouse
import time
import os

class AutomacaoSistema:
    def __init__(self):
        # Configurações de segurança do PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0

    def mover_mouse(self, x=None, y=None):
        """Move o mouse para uma posição específica ou relativa"""
        if x is None or y is None:
            # Move o mouse relativamente à posição atual
            current_x, current_y = pyautogui.position()
            pyautogui.moveRel(50, 0)  # Move 50 pixels para a direita
        else:
            pyautogui.moveTo(x, y)

    def clicar(self, x=None, y=None, botao='left'):
        """Realiza um clique do mouse"""
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, button=botao)
        else:
            pyautogui.click(button=botao)

    def digitar_texto(self, texto, intervalo=0.1):
        """Digite um texto com um intervalo entre as teclas"""
        pyautogui.write(texto, interval=intervalo)

    def pressionar_tecla(self, tecla):
        """Pressiona uma tecla específica"""
        pyautogui.press(tecla)

    def combinar_teclas(self, *teclas):
        """Pressiona uma combinação de teclas"""
        pyautogui.hotkey(*teclas)

    def localizar_imagem(self, imagem_path):
        """Localiza uma imagem na tela"""
        try:
            posicao = pyautogui.locateOnScreen(imagem_path, confidence=0.9)
            if posicao:
                return posicao
            return None
        except:
            return None

    def abrir_programa(self, caminho):
        """Abre um programa específico"""
        try:
            os.startfile(caminho)
            return True
        except:
            return False

    def esperar_imagem(self, imagem_path, timeout=10):
        """Espera até que uma imagem apareça na tela"""
        inicio = time.time()
        while True:
            if time.time() - inicio > timeout:
                return False
            if self.localizar_imagem(imagem_path):
                return True
            time.sleep(0.5)

    def arrastar_mouse(self, x, y, duracao=0.5):
        """Arrasta o mouse de sua posição atual até as coordenadas especificadas"""
        pyautogui.dragTo(x, y, duration=duracao)

    def rolar_pagina(self, quantidade):
        """Rola a página para cima ou para baixo"""
        pyautogui.scroll(quantidade)

    def capturar_tela(self, regiao=None):
        """Captura uma screenshot da tela ou de uma região específica"""
        return pyautogui.screenshot(region=regiao)

    def executar_acao_complexa(self, acoes):
        """Executa uma série de ações em sequência"""
        for acao in acoes:
            tipo = acao.get('tipo')
            params = acao.get('params', {})
            
            if tipo == 'mover':
                self.mover_mouse(**params)
            elif tipo == 'clicar':
                self.clicar(**params)
            elif tipo == 'digitar':
                self.digitar_texto(**params)
            elif tipo == 'tecla':
                self.pressionar_tecla(**params)
            elif tipo == 'esperar':
                time.sleep(params.get('tempo', 1))
            
            time.sleep(0.5)  # Pequena pausa entre ações 