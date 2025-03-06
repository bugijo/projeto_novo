from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import queue
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ServidorAPI:
    def __init__(self, assistente):
        self.assistente = assistente
        self.app = Flask(__name__)
        CORS(self.app)
        self.configurar_rotas()

    def configurar_rotas(self):
        @self.app.route('/comando', methods=['POST'])
        def receber_comando():
            """Recebe comandos do aplicativo móvel"""
            dados = request.get_json()
            if not dados or 'comando' not in dados:
                return jsonify({'erro': 'Comando não fornecido'}), 400
            
            comando = dados['comando']
            self.assistente.fila_comandos.put(comando)
            return jsonify({'status': 'Comando recebido'})

        @self.app.route('/status', methods=['GET'])
        def obter_status():
            """Retorna o status atual do assistente"""
            return jsonify({
                'nome': self.assistente.config.nome,
                'status': 'ativo' if self.assistente.executando else 'inativo',
                'tema': self.assistente.config.tema_interface,
                'avatar': self.assistente.config.avatar
            })

        @self.app.route('/configuracao', methods=['GET', 'POST'])
        def configuracao():
            """Obtém ou atualiza as configurações do assistente"""
            if request.method == 'GET':
                return jsonify({
                    'nome': self.assistente.config.nome,
                    'taxa_fala': self.assistente.config.taxa_fala,
                    'volume': self.assistente.config.volume,
                    'idioma': self.assistente.config.idioma,
                    'tema': self.assistente.config.tema_interface,
                    'avatar': self.assistente.config.avatar
                })
            else:
                dados = request.get_json()
                if not dados:
                    return jsonify({'erro': 'Dados não fornecidos'}), 400
                
                # Atualiza as configurações
                if 'nome' in dados:
                    self.assistente.config.nome = dados['nome']
                if 'taxa_fala' in dados:
                    self.assistente.config.taxa_fala = dados['taxa_fala']
                    self.assistente.configurar_voz()
                if 'volume' in dados:
                    self.assistente.config.volume = dados['volume']
                    self.assistente.configurar_voz()
                if 'idioma' in dados:
                    self.assistente.config.idioma = dados['idioma']
                    self.assistente.configurar_voz()
                if 'tema' in dados:
                    self.assistente.config.tema_interface = dados['tema']
                    self.assistente.interface.mudar_tema(dados['tema'])
                if 'avatar' in dados:
                    self.assistente.config.avatar = dados['avatar']
                    self.assistente.interface.atualizar_avatar()
                
                return jsonify({'status': 'Configurações atualizadas'})

        @self.app.route('/vozes', methods=['GET'])
        def listar_vozes():
            """Lista as vozes disponíveis"""
            vozes = []
            for voice in self.assistente.engine.getProperty('voices'):
                vozes.append({
                    'id': voice.id,
                    'nome': voice.name,
                    'idiomas': voice.languages,
                    'genero': voice.gender
                })
            return jsonify(vozes)

        @self.app.route('/avatares', methods=['GET'])
        def listar_avatares():
            """Lista os avatares disponíveis"""
            pasta_avatares = Path("assets/avatars")
            if not pasta_avatares.exists():
                return jsonify(['default'])
            return jsonify([f.stem for f in pasta_avatares.glob("*.png")])

        @self.app.route('/comandos', methods=['GET'])
        def listar_comandos():
            """Lista os comandos disponíveis"""
            return jsonify(self.assistente.comandos)

    def iniciar(self):
        """Inicia o servidor Flask"""
        self.app.run(
            host='0.0.0.0',
            port=self.assistente.config.porta_servidor,
            debug=False,
            use_reloader=False
        ) 