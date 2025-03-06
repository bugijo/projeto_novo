from core.auth_manager import AuthManager

def test_login():
    auth = AuthManager()
    
    # Tenta autenticar com o usuário Bugijo
    token = auth.authenticate('Bugijo', 'El@1nem@e')
    
    if token:
        print("Login bem sucedido!")
        print(f"Token: {token}")
    else:
        print("Falha no login!")
        
    # Verifica o arquivo de usuários
    with open('data/users.json', 'r') as f:
        print("\nConteúdo do arquivo users.json:")
        print(f.read())

if __name__ == '__main__':
    test_login() 