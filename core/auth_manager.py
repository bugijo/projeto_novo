import os
import jwt
import time
import bcrypt
from typing import Dict, Optional
import logging
from pathlib import Path
import json

from config.system_config import SECURITY_CONFIG

class AuthManager:
    """Gerenciador de autenticação e autorização."""
    
    def __init__(self):
        self.logger = logging.getLogger('AuthManager')
        self.users_file = Path('data/users.json')
        self.users_file.parent.mkdir(exist_ok=True)
        
        # Configura logging
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Adiciona handler para arquivo
        fh = logging.FileHandler('logs/auth.log')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Carrega ou cria arquivo de usuários
        if not self.users_file.exists():
            self._create_default_users()
        else:
            try:
                # Verifica se o arquivo é válido
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                self.logger.error("Arquivo users.json corrompido. Recriando...")
                self._create_default_users()
    
    def _create_default_users(self):
        """Cria usuários padrão."""
        try:
            # Cria hash para a senha do admin
            admin_salt = bcrypt.gensalt()
            admin_hash = bcrypt.hashpw('admin123'.encode('utf-8'), admin_salt)
            
            # Cria hash para a senha do Bugijo
            bugijo_salt = bcrypt.gensalt()
            bugijo_hash = bcrypt.hashpw('El@1nem@e'.encode('utf-8'), bugijo_salt)
            
            users = {
                'admin': {
                    'password': admin_hash.decode('utf-8'),
                    'role': 'admin',
                    'created_at': time.time()
                },
                'Bugijo': {
                    'password': bugijo_hash.decode('utf-8'),
                    'role': 'admin',
                    'created_at': time.time()
                }
            }
            
            # Garante que o diretório existe
            self.users_file.parent.mkdir(exist_ok=True)
            
            # Salva o arquivo
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Arquivo de usuários criado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar usuários padrão: {str(e)}")
            raise
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Autentica um usuário e retorna um token JWT."""
        try:
            if not self.users_file.exists():
                self.logger.error("Arquivo de usuários não encontrado")
                self._create_default_users()
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if username not in users:
                self.logger.warning(f"Tentativa de login com usuário inexistente: {username}")
                return None
            
            user = users[username]
            stored_hash = user['password'].encode('utf-8')
            provided_password = password.encode('utf-8')
            
            self.logger.debug(f"Verificando senha para usuário: {username}")
            self.logger.debug(f"Hash armazenado: {stored_hash}")
            
            if not bcrypt.checkpw(provided_password, stored_hash):
                self.logger.warning(f"Senha incorreta para o usuário: {username}")
                return None
            
            # Gera token JWT
            token = jwt.encode(
                {
                    'user': username,
                    'role': user['role'],
                    'exp': time.time() + SECURITY_CONFIG['token_expiration']
                },
                SECURITY_CONFIG['encryption_key'],
                algorithm='HS256'
            )
            
            self.logger.info(f"Login bem sucedido para o usuário: {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Erro na autenticação: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verifica um token JWT e retorna os dados do usuário."""
        try:
            data = jwt.decode(
                token,
                SECURITY_CONFIG['encryption_key'],
                algorithms=['HS256']
            )
            
            # Verifica expiração
            if data['exp'] < time.time():
                return None
            
            return data
            
        except jwt.InvalidTokenError:
            self.logger.warning("Token inválido recebido")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao verificar token: {str(e)}")
            return None
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Cria um novo usuário."""
        try:
            users = json.loads(self.users_file.read_text())
            
            if username in users:
                return False
            
            # Hash da senha
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            
            # Adiciona usuário
            users[username] = {
                'password': hashed.decode(),
                'role': role,
                'created_at': time.time()
            }
            
            self.users_file.write_text(json.dumps(users, indent=2))
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar usuário: {str(e)}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Remove um usuário."""
        try:
            users = json.loads(self.users_file.read_text())
            
            if username not in users or users[username]['role'] == 'admin':
                return False
            
            del users[username]
            self.users_file.write_text(json.dumps(users, indent=2))
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao deletar usuário: {str(e)}")
            return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Altera a senha de um usuário."""
        try:
            users = json.loads(self.users_file.read_text())
            
            if username not in users:
                return False
            
            user = users[username]
            if not bcrypt.checkpw(old_password.encode(), user['password'].encode()):
                return False
            
            # Hash da nova senha
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(new_password.encode(), salt)
            user['password'] = hashed.decode()
            
            self.users_file.write_text(json.dumps(users, indent=2))
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao alterar senha: {str(e)}")
            return False 