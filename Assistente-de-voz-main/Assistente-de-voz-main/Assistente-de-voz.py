import speech_recognition as sr
import pyttsx3
import datetime
import os
import webbrowser
import time
from googlesearch import search
import pyautogui


def executa_comando(palavra_chave='eva'):
    audio = sr.Recognizer()
    with sr.Microphone() as source:
        print('Ouvindo...')
        audio.adjust_for_ambient_noise(source)
        voz = audio.listen(source)

    try:
        comando = audio.recognize_google(voz, language='pt-BR')
        print('Comando reconhecido:', comando)
        if palavra_chave.lower() in comando.lower():
            return comando.lower().replace(palavra_chave.lower(), '').strip()
        else:
            print('Palavra-chave não encontrada.')
            return ''
    except sr.UnknownValueError:
        print('Não entendi o comando.')
        return ''
    except sr.RequestError:
        print('Erro no serviço de reconhecimento de voz.')
        return ''


def falar(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()


def pesquisar_google(query):
    try:
        resultados = search(query, num=1, stop=1, pause=2)
        for resultado in resultados:
            return resultado
    except Exception as e:
        print("Erro ao pesquisar no Google:", e)
        return "Desculpe, não consegui encontrar nada."


def abrir_navegador(url):
    try:
        navegador = 'chrome'
        caminho_executavel = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
        webbrowser.register(
            navegador, None, webbrowser.BackgroundBrowser(caminho_executavel))
        webbrowser.get(navegador).open(url)
    except webbrowser.Error as e:
        print("Erro ao abrir o navegador:", e)
        falar("Desculpe, não consegui abrir o navegador.")


def enviar_mensagem_whatsapp(contato, mensagem):
    os.system("start https://web.whatsapp.com/")
    # Aumente o tempo se necessário para garantir que o WhatsApp Web carregue completamente
    time.sleep(10)

    # Selecionar o campo de pesquisa de contatos e digitar o nome do contato
    pyautogui.click(272, 220)  # Ajuste as coordenadas para o campo de pesquisa
    time.sleep(2)  # Espera o campo de pesquisa abrir
    pyautogui.write(contato, interval=0.05)
    time.sleep(2)  # Aguarda a lista de contatos aparecer

    # Selecionar o contato da lista
    pyautogui.press('enter')
    time.sleep(2)  # Aguarda a conversa abrir

    # Digitar a mensagem
    pyautogui.write(mensagem, interval=0.05)
    pyautogui.press('enter')  # Envia a mensagem


def comando_voz_usuario():
    comando = executa_comando(palavra_chave='eva')

    if 'horas' in comando:
        hora = datetime.datetime.now().strftime('%H:%M')
        falar('Agora são ' + hora)
    elif 'pesquise por' in comando:
        falar("Sim senhor")
        termo_pesquisa = comando.replace('pesquise por', '')
        resultado = pesquisar_google(termo_pesquisa)
        if resultado:
            print("Resultado da pesquisa no Google:", resultado)
            falar("Aqui está o que encontrei no Google: ")
            abrir_navegador(resultado)
        else:
            falar("Desculpe, não consegui encontrar nada.")
    elif 'enviar mensagem' in comando:
        falar("Para quem gostaria de enviar?")
        # Captura o nome do contato
        contato = executa_comando(palavra_chave='')
        if contato:
            falar("Qual mensagem gostaria de enviar?")
            mensagem = executa_comando(palavra_chave='')  # Captura a mensagem
            if mensagem:
                enviar_mensagem_whatsapp(contato, mensagem)
            else:
                falar("Desculpe, não consegui capturar a mensagem.")
        else:
            falar("Desculpe, não consegui capturar o contato.")

    elif 'sair' in comando:
        falar("Encerrando o assistente de voz.")
        return False
    return True


# Loop contínuo para ouvir comandos
while True:
    if not comando_voz_usuario():
        break
