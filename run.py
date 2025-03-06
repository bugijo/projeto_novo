#!/usr/bin/env python
import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_environment():
    """Configura o ambiente virtual e instala dependências"""
    if not Path("venv").exists():
        print("Criando ambiente virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Ativa o ambiente virtual
    if sys.platform == "win32":
        python = "venv\\Scripts\\python.exe"
    else:
        python = "venv/bin/python"
    
    # Instala dependências
    print("Instalando dependências...")
    subprocess.run([python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def start_server(debug=False):
    """Inicia o servidor Flask"""
    from api import app
    app.run(debug=debug, host="0.0.0.0", port=5000)

def run_tests():
    """Executa os testes"""
    subprocess.run(["pytest", "-v", "--cov=."], check=True)

def main():
    parser = argparse.ArgumentParser(description="Script de gerenciamento do projeto")
    parser.add_argument("--setup", action="store_true", help="Configura o ambiente")
    parser.add_argument("--start", action="store_true", help="Inicia o servidor")
    parser.add_argument("--test", action="store_true", help="Executa os testes")
    parser.add_argument("--debug", action="store_true", help="Executa em modo debug")
    
    args = parser.parse_args()

    if args.setup:
        setup_environment()
    elif args.start:
        start_server(debug=args.debug)
    elif args.test:
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 