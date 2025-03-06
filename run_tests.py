import pytest
import sys
import os
from pathlib import Path

def main():
    """Executa os testes do sistema"""
    # Adiciona diretório raiz ao PYTHONPATH
    root_dir = Path(__file__).parent
    sys.path.append(str(root_dir))
    
    # Configura argumentos do pytest
    args = [
        "tests",  # diretório de testes
        "-v",     # verbose
        "--tb=short",  # traceback curto
        "-s",     # mostra prints
    ]
    
    # Executa os testes
    resultado = pytest.main(args)
    
    # Retorna código de saída
    return resultado

if __name__ == "__main__":
    sys.exit(main()) 