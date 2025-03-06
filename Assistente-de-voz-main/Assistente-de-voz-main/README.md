# Assistente de Voz com Automação de Tarefas em Python

Este projeto é um assistente de voz construído em Python que realiza tarefas automatizadas como fornecer a hora atual, realizar pesquisas no Google e enviar mensagens via WhatsApp Web. O assistente responde aos comandos de voz, o que facilita a interação com o usuário.

## Funcionalidades

- **Informar a Hora**: O assistente informa a hora atual em resposta ao comando de voz.
- **Pesquisa no Google**: Realiza pesquisas no Google a partir de um comando de voz e abre o navegador com o resultado encontrado.
- **Enviar Mensagens pelo WhatsApp Web**: Envia mensagens para um contato específico no WhatsApp Web por meio de comandos de voz.
- **Automação Simples**: O assistente realiza as tarefas de maneira automatizada, utilizando bibliotecas como `pyautogui` para interações com a interface gráfica do usuário.

## Tecnologias Utilizadas

- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)**: Para capturar e interpretar os comandos de voz.
- **[pyttsx3](https://pypi.org/project/pyttsx3/)**: Para converter texto em fala, permitindo que o assistente fale com o usuário.
- **[pyautogui](https://pypi.org/project/PyAutoGUI/)**: Para automatizar interações com a tela, como enviar mensagens pelo WhatsApp Web.
- **[googlesearch-python](https://pypi.org/project/googlesearch-python/)**: Para realizar buscas no Google programaticamente.
- **[webbrowser](https://docs.python.org/3/library/webbrowser.html)**: Para abrir o navegador web e realizar pesquisas.

## Pré-requisitos

Antes de executar o projeto, certifique-se de que você possui o Python instalado e que as bibliotecas necessárias foram instaladas. Você pode instalar todas as dependências através do seguinte comando:

```bash
pip install SpeechRecognition pyttsx3 pyautogui googlesearch-python
```
### Como Executar
1 .Clone este repositório em sua máquina local:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
````
2 .Navegue até o diretório do projeto:
```bash
cd seu-repositorio
```
3 .Execute o arquivo principal:
```bash
python seu_arquivo_principal.py
```
4 .O assistente ficará aguardando comandos de voz. Alguns exemplos de comandos que podem ser utilizados:

"Eva, que horas são?": O assistente responderá com a hora atual.

"Eva, pesquise por Python no Google": O assistente fará a busca no Google e abrirá o navegador com o resultado.

"Eva, enviar mensagem": O assistente solicitará o nome do contato e a mensagem a ser enviada via WhatsApp Web.

Considerações
A automação via pyautogui é sensível às coordenadas da tela e pode não funcionar corretamente caso o layout do WhatsApp Web ou a resolução da tela sejam diferentes.

O reconhecimento de voz depende da qualidade do microfone e do ambiente em que o comando é dado.

Sinta-se à vontade para contribuir com este projeto. Caso tenha ideias de melhoria ou novas funcionalidades, abra uma issue ou envie um pull request.



