import speech_recognition as sr
import pyttsx3
import pyautogui
import os
import sys
import datetime
import webbrowser
from gtts import gTTS
from playsound import playsound
import keyboard
import mouse
import json
import requests
from transformers import pipeline

class AssistenteVirtual:
    def __init__(self):
        self.nome = "Jarvis"
        self.reconhecedor = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.configurar_voz()
        self.comandos = self.carregar_comandos()
        self.nlp = pipeline("text-generation", model="gpt2")

    def configurar_voz(self):
        """Configura as propriedades da voz do assistente"""
        voices = self.engine.getProperty('voices')
        # Procura por uma voz em português
        for voice in voices:
            if "portuguese" in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 1.0)

    def carregar_comandos(self):
        """Carrega os comandos personalizados do arquivo de configuração"""
        try:
            with open('comandos.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def falar(self, texto):
        """Converte texto em fala"""
        print(f"{self.nome}: {texto}")
        self.engine.say(texto)
        self.engine.runAndWait()

    def ouvir(self):
        """Captura e reconhece o comando de voz do usuário"""
        with sr.Microphone() as source:
            print("Ouvindo...")
            self.reconhecedor.adjust_for_ambient_noise(source)
            audio = self.reconhecedor.listen(source)

        try:
            comando = self.reconhecedor.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {comando}")
            return comando.lower()
        except sr.UnknownValueError:
            print("Não entendi o comando")
            return ""
        except sr.RequestError:
            print("Erro na requisição")
            return ""

    def executar_comando(self, comando):
        """Executa o comando reconhecido"""
        if "abrir" in comando:
            if "navegador" in comando:
                webbrowser.open("http://google.com")
                self.falar("Abrindo o navegador")
            # Adicionar mais comandos de abertura de programas

        elif "hora" in comando:
            hora = datetime.datetime.now().strftime('%H:%M')
            self.falar(f"Agora são {hora}")

        elif "pesquisar" in comando:
            termo = comando.replace("pesquisar", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={termo}")
            self.falar(f"Pesquisando por {termo}")

        elif "programar" in comando or "código" in comando:
            self.assistente_programacao(comando)

    def assistente_programacao(self, comando):
        """Módulo de assistência à programação"""
        if "criar arquivo" in comando:
            nome_arquivo = comando.split("criar arquivo")[-1].strip()
            with open(f"{nome_arquivo}.py", "w") as f:
                f.write("# Novo arquivo Python\n")
            self.falar(f"Arquivo {nome_arquivo}.py criado com sucesso")

        elif "sugerir código" in comando:
            prompt = comando.replace("sugerir código", "").strip()
            sugestao = self.nlp(prompt, max_length=100)[0]['generated_text']
            self.falar("Aqui está minha sugestão de código")
            print(sugestao)

    def executar(self):
        """Inicia o assistente virtual"""
        self.falar(f"Olá, eu sou o {self.nome}, seu assistente virtual. Como posso ajudar?")
        
        while True:
            comando = self.ouvir()
            if comando:
                if "desligar" in comando or "encerrar" in comando:
                    self.falar("Encerrando o assistente. Até logo!")
                    break
                self.executar_comando(comando)

if __name__ == "__main__":
    assistente = AssistenteVirtual()
    assistente.executar() 