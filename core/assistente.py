import speech_recognition as sr
import pyttsx3
import datetime
import os
import sys
import json
import queue
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .automacao import AutomacaoSistema
from .programacao import AssistenteProgramacao
from .interface import InterfaceGrafica
from .servidor import ServidorAPI

@dataclass
class ConfiguracaoAssistente:
    nome: str = "Jarvis"
    voz_id: Optional[str] = None
    taxa_fala: int = 200
    volume: float = 1.0
    idioma: str = "pt-BR"
    tema_interface: str = "dark"
    avatar: str = "default"
    porta_servidor: int = 5000

class AssistenteVirtual:
    def __init__(self, config: Optional[ConfiguracaoAssistente] = None):
        self.config = config or ConfiguracaoAssistente()
        self.reconhecedor = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.fila_comandos = queue.Queue()
        self.automacao = AutomacaoSistema()
        self.programacao = AssistenteProgramacao()
        self.interface = InterfaceGrafica(self)
        self.servidor = ServidorAPI(self)
        self.comandos = self.carregar_comandos()
        self.configurar_voz()
        self.executando = False
        self.threads = []

    def configurar_voz(self):
        """Configura as propriedades da voz do assistente"""
        voices = self.engine.getProperty('voices')
        voz_selecionada = None
        
        # Procura por uma voz no idioma configurado
        for voice in voices:
            if self.config.idioma[:2].lower() in voice.languages:
                voz_selecionada = voice
                break
        
        if voz_selecionada:
            self.engine.setProperty('voice', voz_selecionada.id)
        
        self.engine.setProperty('rate', self.config.taxa_fala)
        self.engine.setProperty('volume', self.config.volume)

    def carregar_comandos(self) -> Dict[str, Any]:
        """Carrega os comandos personalizados do arquivo de configuração"""
        caminho_comandos = Path("config/comandos.json")
        if not caminho_comandos.exists():
            return {}
        
        with open(caminho_comandos, 'r', encoding='utf-8') as file:
            return json.load(file)

    def falar(self, texto: str):
        """Converte texto em fala"""
        print(f"{self.config.nome}: {texto}")
        self.interface.atualizar_historico(f"{self.config.nome}: {texto}")
        self.engine.say(texto)
        self.engine.runAndWait()

    def ouvir(self) -> str:
        """Captura e reconhece o comando de voz do usuário"""
        with sr.Microphone() as source:
            print("Ouvindo...")
            self.interface.atualizar_status("Ouvindo...")
            self.reconhecedor.adjust_for_ambient_noise(source)
            audio = self.reconhecedor.listen(source)

        try:
            comando = self.reconhecedor.recognize_google(audio, language=self.config.idioma)
            print(f"Você disse: {comando}")
            self.interface.atualizar_historico(f"Você: {comando}")
            return comando.lower()
        except sr.UnknownValueError:
            print("Não entendi o comando")
            return ""
        except sr.RequestError:
            print("Erro na requisição")
            return ""

    def processar_comando(self, comando: str):
        """Processa e executa o comando recebido"""
        if not comando:
            return

        # Comandos do sistema
        if "abrir" in comando:
            if "navegador" in comando:
                self.automacao.abrir_programa("chrome")
                self.falar("Abrindo o navegador")

        elif "hora" in comando:
            hora = datetime.datetime.now().strftime('%H:%M')
            self.falar(f"Agora são {hora}")

        elif "programar" in comando or "código" in comando:
            self.programacao.processar_comando(comando)

        # Comandos de automação
        elif any(palavra in comando for palavra in ["mouse", "cursor", "clique"]):
            self.automacao.processar_comando(comando)

    def iniciar_threads(self):
        """Inicia as threads necessárias para o funcionamento do assistente"""
        # Thread para processar comandos da fila
        thread_comandos = threading.Thread(target=self._processar_fila_comandos)
        thread_comandos.daemon = True
        self.threads.append(thread_comandos)

        # Thread para o servidor API
        thread_servidor = threading.Thread(target=self.servidor.iniciar)
        thread_servidor.daemon = True
        self.threads.append(thread_servidor)

        for thread in self.threads:
            thread.start()

    def _processar_fila_comandos(self):
        """Processa comandos da fila em background"""
        while self.executando:
            try:
                comando = self.fila_comandos.get(timeout=1)
                self.processar_comando(comando)
                self.fila_comandos.task_done()
            except queue.Empty:
                continue

    def executar(self):
        """Inicia o assistente virtual"""
        self.executando = True
        self.iniciar_threads()
        self.interface.iniciar()
        
        self.falar(f"Olá, eu sou {self.config.nome}, seu assistente virtual. Como posso ajudar?")
        
        try:
            while self.executando:
                comando = self.ouvir()
                if comando:
                    if "desligar" in comando or "encerrar" in comando:
                        self.falar("Encerrando o assistente. Até logo!")
                        self.executando = False
                        break
                    self.fila_comandos.put(comando)
        except KeyboardInterrupt:
            self.executando = False
        
        # Aguarda todas as threads finalizarem
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    assistente = AssistenteVirtual()
    assistente.executar() 