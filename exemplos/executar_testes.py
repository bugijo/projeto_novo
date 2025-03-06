import os
import sys
import subprocess
import asyncio

async def executar_testes():
    print("=== Iniciando Testes Gerais ===\n")
    
    # Diretório dos exemplos
    dir_exemplos = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Teste do Olá Mundo
    print("1. Testando aplicação Olá Mundo...")
    try:
        processo = subprocess.Popen(
            [sys.executable, os.path.join(dir_exemplos, "ola_mundo.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Aplicação Olá Mundo iniciada. Pressione Ctrl+C para continuar...")
        try:
            processo.wait(timeout=10)
        except subprocess.TimeoutExpired:
            processo.terminate()
        print("Teste Olá Mundo concluído!\n")
    except Exception as e:
        print(f"Erro ao executar Olá Mundo: {e}\n")
    
    # 2. Teste do App Mobile
    print("2. Verificando app mobile Flutter...")
    app_dir = os.path.join(dir_exemplos, "app_mobile")
    if os.path.exists(app_dir):
        print("Estrutura do app mobile criada com sucesso!")
        print("Para executar o app mobile:")
        print("1. Certifique-se de ter o Flutter instalado")
        print("2. Navegue até a pasta app_mobile")
        print("3. Execute 'flutter run'\n")
    else:
        print("Diretório do app mobile não encontrado\n")
    
    # 3. Teste de Criação de Personagem
    print("3. Testando criação de personagem...")
    try:
        processo = await asyncio.create_subprocess_exec(
            sys.executable,
            os.path.join(dir_exemplos, "criar_personagem.py"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await processo.communicate()
        if stdout:
            print(stdout.decode())
        if stderr:
            print("Erros:", stderr.decode())
        print("Teste de criação de personagem concluído!\n")
    except Exception as e:
        print(f"Erro ao criar personagem: {e}\n")
    
    print("=== Testes Concluídos ===")

if __name__ == "__main__":
    try:
        asyncio.run(executar_testes())
    except KeyboardInterrupt:
        print("\nTestes interrompidos pelo usuário") 