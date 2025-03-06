import bcrypt
import json
import time
from pathlib import Path

def create_users():
    # Cria hash para a senha do Bugijo
    password = 'El@1nem@e'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    
    users = {
        "Bugijo": {
            "password": hashed.decode(),
            "role": "admin",
            "created_at": time.time()
        }
    }
    
    # Salva o arquivo
    users_file = Path('data/users.json')
    users_file.parent.mkdir(exist_ok=True)
    users_file.write_text(json.dumps(users, indent=2))
    print("Arquivo de usuários criado com sucesso!")
    print(f"Conteúdo: {json.dumps(users, indent=2)}")

if __name__ == '__main__':
    create_users() 