import os
import sys
import cmd
import json
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from .core import AIEngine
from .lm_studio import LMStudioInterface

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICLI(cmd.Cmd):
    intro = """
    🤖 Assistente de Programação Autônomo
    Digite 'help' ou '?' para listar os comandos.
    """
    prompt = "🤖> "
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.lm_studio = LMStudioInterface()
        self.engine = AIEngine()
        self.current_project = None
        self.current_dir = None
        
    def preloop(self):
        """Inicializa o ambiente."""
        if not self.lm_studio.start_server():
            self.console.print("[red]Erro ao iniciar LM Studio[/red]")
            sys.exit(1)
    
    def do_novo(self, arg):
        """Cria um novo projeto.
        
        Uso: novo <nome_projeto> <descrição>
        """
        if not arg:
            self.console.print("[red]Especifique o nome e a descrição do projeto[/red]")
            return
            
        try:
            nome, *desc = arg.split()
            desc = " ".join(desc)
            
            self.console.print("\n[yellow]Analisando requisitos...[/yellow]")
            spec = self.engine.parse_requirements(desc)
            
            if not spec:
                self.console.print("[red]Erro ao analisar requisitos[/red]")
                return
                
            # Mostra especificação
            table = Table(title="Especificação do Projeto")
            table.add_column("Campo")
            table.add_column("Valor")
            
            for field, value in spec.__dict__.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, indent=2)
                table.add_row(field, str(value))
            
            self.console.print(table)
            
            if not self.confirm("Deseja prosseguir com esta especificação?"):
                return
                
            # Cria projeto
            output_dir = Path.cwd() / nome
            if self.engine.create_project(desc, str(output_dir)):
                self.console.print(f"\n[green]Projeto {nome} criado com sucesso![/green]")
                self.current_project = nome
                self.current_dir = output_dir
            else:
                self.console.print("[red]Erro ao criar projeto[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {str(e)}[/red]")
    
    def do_validar(self, arg):
        """Valida o código do arquivo especificado.
        
        Uso: validar <arquivo>
        """
        if not arg:
            self.console.print("[red]Especifique o arquivo[/red]")
            return
            
        try:
            file_path = Path(arg)
            if not file_path.exists():
                self.console.print("[red]Arquivo não encontrado[/red]")
                return
                
            code = file_path.read_text()
            result = self.lm_studio.validate_code(code)
            
            # Mostra resultado
            table = Table(title=f"Validação de {file_path.name}")
            table.add_column("Tipo")
            table.add_column("Detalhes")
            
            if result["erros"]:
                for erro in result["erros"]:
                    table.add_row("Erro", erro, style="red")
                    
            if result["warnings"]:
                for warn in result["warnings"]:
                    table.add_row("Warning", warn, style="yellow")
                    
            if result["sugestões"]:
                for sug in result["sugestões"]:
                    table.add_row("Sugestão", sug, style="blue")
                    
            table.add_row("Score", f"{result['score']}/10", 
                         style="green" if result['score'] >= 7 else "yellow")
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Erro: {str(e)}[/red]")
    
    def do_explicar(self, arg):
        """Gera explicação detalhada do código.
        
        Uso: explicar <arquivo>
        """
        if not arg:
            self.console.print("[red]Especifique o arquivo[/red]")
            return
            
        try:
            file_path = Path(arg)
            if not file_path.exists():
                self.console.print("[red]Arquivo não encontrado[/red]")
                return
                
            code = file_path.read_text()
            explanation = self.lm_studio.explain_code(code)
            
            self.console.print(Panel(
                Markdown(explanation),
                title=f"Explicação de {file_path.name}",
                border_style="blue"
            ))
            
        except Exception as e:
            self.console.print(f"[red]Erro: {str(e)}[/red]")
    
    def do_testes(self, arg):
        """Sugere casos de teste para o código.
        
        Uso: testes <arquivo>
        """
        if not arg:
            self.console.print("[red]Especifique o arquivo[/red]")
            return
            
        try:
            file_path = Path(arg)
            if not file_path.exists():
                self.console.print("[red]Arquivo não encontrado[/red]")
                return
                
            code = file_path.read_text()
            tests = self.lm_studio.suggest_tests(code)
            
            if not tests:
                self.console.print("[yellow]Nenhum teste sugerido[/yellow]")
                return
                
            # Mostra testes
            for i, test in enumerate(tests, 1):
                self.console.print(f"\n[blue]Teste #{i}[/blue]")
                self.console.print(f"Descrição: {test['descrição']}")
                self.console.print(f"Tipo: {test['tipo']}")
                self.console.print("\nCódigo:")
                self.console.print(Syntax(
                    test['código'],
                    "python",
                    theme="monokai",
                    line_numbers=True
                ))
                
            if self.confirm("\nDeseja criar estes testes?"):
                tests_dir = file_path.parent / "tests"
                tests_dir.mkdir(exist_ok=True)
                
                for i, test in enumerate(tests, 1):
                    test_file = tests_dir / f"test_{file_path.stem}_{i}.py"
                    test_file.write_text(test['código'])
                    
                self.console.print(f"\n[green]Testes criados em {tests_dir}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Erro: {str(e)}[/red]")
    
    def do_sair(self, arg):
        """Sai do programa."""
        self.lm_studio.stop_server()
        return True
    
    def confirm(self, message: str) -> bool:
        """Pede confirmação do usuário."""
        response = input(f"\n{message} (s/N) ")
        return response.lower() == 's'

def main():
    """Função principal."""
    try:
        cli = AICLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nPrograma encerrado")
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 