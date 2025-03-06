from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, send_from_directory, send_file, Response
from functools import wraps
import json
import os
import logging
from datetime import datetime
import requests
from pathlib import Path
from simple_image_generator import SimpleImageGenerator
import subprocess
import sys
import threading
from logging.config import dictConfig
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configuração de logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
logger = logging.getLogger(__name__)

# Simulação de um banco de dados de usuários (em produção, use um banco de dados real)
USERS = {
    'admin': 'senha123'
}

# Simulação de histórico (em produção, use um banco de dados real)
HISTORY = []

# Inicializa o gerador de imagens
image_generator = SimpleImageGenerator()

# Histórico de conversas
CONVERSATIONS = []

# Sistema de respostas da IA
SYSTEM_PROMPTS = {
    'chat': """Você é um assistente virtual amigável e prestativo. 
    Responda de forma natural e engajadora, mantendo um tom profissional mas acolhedor.""",
    
    'image': """Você é um especialista em arte e design.
    Ajude a refinar prompts para geração de imagens, sugerindo detalhes que melhoram o resultado.
    Mantenha o foco em criar descrições visuais ricas e criativas.""",
    
    'code': """Você é um programador experiente.
    Ajude a desenvolver código, explicando cada passo e seguindo boas práticas.
    Mantenha um plano claro de desenvolvimento e atualize o progresso.""",
    
    'video': """Você é um especialista em produção de vídeo.
    Ajude a planejar e criar vídeos, sugerindo elementos visuais, narrativa e edição.
    Foque em criar conteúdo envolvente e profissional.""",
    
    '3d': """Você é um artista 3D experiente.
    Ajude a criar modelos e cenas 3D, sugerindo técnicas e abordagens.
    Mantenha o foco em criar designs funcionais e visualmente atraentes."""
}

ide_process = None

def check_auth():
    user = request.cookies.get('user')
    return user and user in USERS

def get_ai_response(mode: str, message: str) -> dict:
    """Obtém uma resposta da IA baseada no modo e mensagem."""
    try:
        # Prepara o contexto baseado no modo
        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS['chat'])
        
        # Se for modo de programação, inclui o plano de desenvolvimento
        if mode == 'code':
            response = {
                'text': f"Vou ajudar você com o desenvolvimento de: {message}\n\nPrimeiro, vamos analisar os requisitos e criar um plano:",
                'plan': [
                    {'description': 'Análise dos requisitos', 'status': 'current'},
                    {'description': 'Estruturação do projeto', 'status': 'pending'},
                    {'description': 'Implementação do backend', 'status': 'pending'},
                    {'description': 'Desenvolvimento do frontend', 'status': 'pending'},
                    {'description': 'Testes e depuração', 'status': 'pending'},
                    {'description': 'Documentação', 'status': 'pending'}
                ]
            }
        
        # Se for modo de imagem, ajuda a refinar o prompt
        elif mode == 'image':
            response = {
                'text': f"Vou ajudar você a criar uma imagem incrível baseada em: '{message}'\n\n"
                       f"Sugiro adicionar alguns detalhes para melhorar o resultado:\n"
                       f"- Estilo artístico específico\n"
                       f"- Iluminação e atmosfera\n"
                       f"- Cores predominantes\n"
                       f"- Detalhes do ambiente\n\n"
                       f"Você gostaria de refinar algum desses aspectos?"
            }
        
        # Se for modo de vídeo
        elif mode == 'video':
            response = {
                'text': f"Vamos criar um vídeo sobre: '{message}'\n\n"
                       f"Para começar, precisamos definir:\n"
                       f"- Duração estimada\n"
                       f"- Estilo visual\n"
                       f"- Público-alvo\n"
                       f"- Elementos principais\n\n"
                       f"Qual desses aspectos você gostaria de discutir primeiro?"
            }
        
        # Se for modo 3D
        elif mode == '3d':
            response = {
                'text': f"Vamos criar um modelo 3D para: '{message}'\n\n"
                       f"Precisamos definir:\n"
                       f"- Estilo (realista, cartoon, low-poly, etc)\n"
                       f"- Propósito (jogo, animação, impressão 3D)\n"
                       f"- Nível de detalhe\n"
                       f"- Materiais principais\n\n"
                       f"Por onde você gostaria de começar?"
            }
        
        # Modo chat padrão
        else:
            response = {
                'text': f"Entendi que você quer conversar sobre: '{message}'\n\n"
                       f"Como posso ajudar especificamente com isso?"
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Erro ao gerar resposta da IA: {str(e)}")
        return {'text': "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"}

def start_ide_process():
    """Inicia o processo do IDE em uma thread separada"""
    try:
        # Ativar ambiente virtual
        if sys.platform == 'win32':
            python_path = str(Path('venv/Scripts/python.exe'))
        else:
            python_path = str(Path('venv/bin/python'))

        # Comando para iniciar o IDE
        cmd = [python_path, 'main.py']
        
        # Configurar ambiente para o IDE
        env = os.environ.copy()
        env['IDE_PORT'] = '5001'  # Usar porta 5001 para o IDE
        
        global ide_process
        ide_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
            env=env
        )
        
        # Log do processo
        app.logger.info(f"IDE iniciado com PID {ide_process.pid}")
        
        # Monitorar saída do processo
        def monitor_output():
            while True:
                output = ide_process.stdout.readline()
                if output:
                    app.logger.info(f"IDE output: {output.decode().strip()}")
                if ide_process.poll() is not None:
                    break
        
        # Iniciar thread de monitoramento
        threading.Thread(target=monitor_output, daemon=True).start()
        
        # Aguardar um pouco para garantir que o IDE iniciou
        time.sleep(2)
        
        # Verificar se o processo ainda está rodando
        if ide_process.poll() is None:
            return True
        else:
            error = ide_process.stderr.read().decode()
            app.logger.error(f"IDE falhou ao iniciar: {error}")
            return False
            
    except Exception as e:
        app.logger.error(f"Erro ao iniciar IDE: {str(e)}")
        return False

@app.route('/')
def index():
    try:
        logger.info("Renderizando página inicial")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erro ao renderizar página inicial: {str(e)}")
        return "Erro ao carregar a página", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        logger.info("Renderizando página de login")
        if request.method == 'GET':
            return render_template('login.html')
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username in USERS and USERS[username] == password:
            response = jsonify({'success': True})
            response.set_cookie('user', username)
            return response
        
        return jsonify({
            'success': False,
            'error': 'Usuário ou senha inválidos'
        }), 401
    except Exception as e:
        logger.error(f"Erro ao renderizar página de login: {str(e)}")
        return "Erro ao carregar a página de login", 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if not check_auth():
            return jsonify({'success': False, 'error': 'Não autorizado'}), 401
        
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'chat')
        
        # Se for modo de geração de imagem
        if model == 'image':
            # Primeiro obtém sugestões da IA
            ai_response = get_ai_response(model, message)
            
            # Se o prompt parece completo, gera a imagem
            if "gerar" in message.lower() or "criar" in message.lower():
                image_path = image_generator.generate_image(message)
                if image_path:
                    # Converte o caminho absoluto para URL relativa
                    image_url = f"/images/{os.path.basename(image_path)}"
                    return jsonify({
                        'success': True,
                        'response': ai_response['text'] + f'\n\n<img src="{image_url}" alt="Imagem gerada" style="max-width: 100%; border-radius: 8px;">',
                        'type': 'image'
                    })
            
            # Se não, apenas retorna as sugestões
            return jsonify({
                'success': True,
                'response': ai_response['text'],
                'type': 'text'
            })
        
        # Se for modo de programação
        elif model == 'code':
            ai_response = get_ai_response(model, message)
            return jsonify({
                'success': True,
                'response': ai_response['text'],
                'plan': ai_response.get('plan'),
                'type': 'code'
            })
        
        # Outros modos
        else:
            ai_response = get_ai_response(model, message)
            return jsonify({
                'success': True,
                'response': ai_response['text'],
                'type': 'text'
            })
            
    except Exception as e:
        logger.error(f"Erro no endpoint de chat: {str(e)}")
        return jsonify({
            'success': False,
            'response': 'Erro ao processar sua mensagem'
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    if not check_auth():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 401
    
    return jsonify({
        'success': True,
        'history': HISTORY
    })

@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory(str(image_generator.output_dir), filename)
    except Exception as e:
        logger.error(f"Erro ao servir imagem {filename}: {str(e)}")
        return "Imagem não encontrada", 404

@app.route('/api/start_ide', methods=['POST'])
def start_ide():
    """Endpoint para iniciar o IDE"""
    global ide_process
    
    try:
        # Verificar se o IDE já está rodando
        if ide_process and ide_process.poll() is None:
            return jsonify({
                'success': True,
                'message': 'IDE já está em execução'
            })
        
        # Iniciar IDE
        success = start_ide_process()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'IDE iniciado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao iniciar o IDE'
            })
            
    except Exception as e:
        app.logger.error(f"Erro no endpoint start_ide: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 