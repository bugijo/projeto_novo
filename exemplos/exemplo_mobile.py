import asyncio
from core.gerenciador_mobile import GerenciadorMobile

async def exemplo_desenvolvimento_mobile():
    """Exemplo de uso do gerenciador mobile"""
    
    # Inicializa o gerenciador
    gerenciador = GerenciadorMobile()
    
    # Verifica o ambiente de desenvolvimento
    status = gerenciador.verificar_ambiente()
    print("\nStatus do ambiente de desenvolvimento:")
    for ferramenta, instalado in status.items():
        print(f"{ferramenta}: {'Instalado' if instalado else 'Não instalado'}")
    
    # Cria um novo projeto Flutter
    print("\nCriando projeto Flutter...")
    projeto_flutter = gerenciador.criar_projeto(
        nome="meu_app_flutter",
        framework="flutter",
        template="ecommerce",
        caminho="./projetos"
    )
    if projeto_flutter:
        print("Projeto Flutter criado com sucesso!")
    
    # Configura e inicia emulador Android
    print("\nConfigurando emulador Android...")
    if gerenciador.configurar_emulador("android", "pixel_api_30"):
        print("Emulador configurado com sucesso!")
        print("Iniciando emulador...")
        if gerenciador.iniciar_emulador("android", "pixel_api_30"):
            print("Emulador iniciado com sucesso!")
    
    # Compila o projeto
    print("\nCompilando projeto para Android...")
    if gerenciador.compilar_projeto("./projetos/meu_app_flutter", "android", "debug"):
        print("Projeto compilado com sucesso!")
    
    # Gera recursos (ícones e splash screens)
    print("\nGerando recursos...")
    if gerenciador.gerar_recursos(
        "./projetos/meu_app_flutter",
        "assets/icone.png",
        "assets/splash.png"
    ):
        print("Recursos gerados com sucesso!")
    
    # Executa testes
    print("\nExecutando testes...")
    resultados = gerenciador.executar_testes("./projetos/meu_app_flutter")
    print("Resultados dos testes:")
    for tipo, resultado in resultados.items():
        print(f"{tipo}: {resultado}")
    
    # Atualiza versão
    print("\nAtualizando versão do app...")
    if gerenciador.atualizar_versao(
        "./projetos/meu_app_flutter",
        "1.0.0",
        "1"
    ):
        print("Versão atualizada com sucesso!")
    
    # Exemplo de publicação (necessita credenciais)
    print("\nPreparando para publicação...")
    credenciais = {
        "keystore_path": "path/to/keystore",
        "keystore_password": "senha",
        "key_alias": "alias",
        "key_password": "senha"
    }
    if gerenciador.publicar_app(
        "./projetos/meu_app_flutter",
        "android",
        credenciais
    ):
        print("App publicado com sucesso!")

if __name__ == "__main__":
    # Executa o exemplo
    asyncio.run(exemplo_desenvolvimento_mobile()) 