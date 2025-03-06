import sys
import os
from pathlib import Path

def test_comfyui_import():
    """Testa se conseguimos importar o ComfyUI."""
    try:
        # Adiciona o diretório do ComfyUI ao PYTHONPATH
        comfy_path = Path("../ComfyUI-master").resolve()
        sys.path.append(str(comfy_path))
        
        # Tenta importar
        import main
        print("✅ ComfyUI importado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar ComfyUI: {str(e)}")
        return False

def test_dependencies():
    """Testa se as dependências estão instaladas."""
    dependencies = [
        "torch",
        "flask",
        "requests",
        "transformers",
        "pillow",
        "numpy"
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} instalado")
        except ImportError:
            print(f"❌ {dep} não encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Função principal de teste."""
    print("\n=== Testando Integração ComfyUI ===\n")
    
    # Testa dependências
    print("Verificando dependências...")
    if not test_dependencies():
        print("\n❌ Algumas dependências estão faltando")
        return
    
    # Testa importação do ComfyUI
    print("\nTestando importação do ComfyUI...")
    if not test_comfyui_import():
        print("\n❌ Não foi possível importar o ComfyUI")
        return
    
    print("\n✅ Todos os testes passaram!")
    print("\nPara iniciar o sistema:")
    print("1. Execute: python api.py")
    print("2. Faça requisições para http://localhost:5000/api/process")

if __name__ == "__main__":
    main() 