import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
import json
import subprocess
import shutil
import virtualenv
import git
from datetime import datetime
import nbformat
from nbconvert import PythonExporter
import pytest
import black
import isort
import pylint.lint
from cookiecutter.main import cookiecutter
from jinja2 import Template
import ast
import libcst
import rope.base.project
from rope.refactor import restructure
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue
import difflib
from .interface_programacao import InterfaceProgramacao
from PyQt6.QtCore import QTimer, QMetaObject, Q_ARG, Qt
from PyQt6.QtWidgets import QApplication
import time
from .perfil_usuario import PerfilUsuario
from .gerenciador_configuracoes import GerenciadorConfiguracoes
from .seletor_linguagem import SeletorLinguagem
import re
import esprima  # Para JavaScript
import javalang  # Para Java
import clang.cindex  # Para C++
from bs4 import BeautifulSoup  # Para HTML
import tinycss2  # Para CSS

class AnalisadorCodigo:
    def __init__(self):
        self.cache = {}
        self.cache_tempo = 300  # 5 minutos
        self.config = self._carregar_config()
        
    def _carregar_config(self) -> dict:
        """Carrega configurações do analisador"""
        try:
            with open("config/programacao.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("preferencias", {}).get("linguagens", {})
        except Exception:
            return {}
            
    def analisar_arquivo(self, caminho: str) -> dict:
        """Analisa um arquivo e retorna informações sobre ele"""
        try:
            # Determina a linguagem pelo arquivo
            ext = Path(caminho).suffix
            linguagem = self.config.get("associacoes_arquivo", {}).get(ext, "python")
            
            with open(caminho, "r", encoding="utf-8") as f:
                codigo = f.read()
                
            # Chama o analisador específico da linguagem
            if linguagem == "python":
                return self._analisar_python(codigo)
            elif linguagem == "javascript":
                return self._analisar_javascript(codigo)
            elif linguagem == "java":
                return self._analisar_java(codigo)
            elif linguagem == "cpp":
                return self._analisar_cpp(codigo)
            elif linguagem == "html":
                return self._analisar_html(codigo)
            elif linguagem == "css":
                return self._analisar_css(codigo)
            else:
                return self._analisar_python(codigo)  # Fallback para Python
                
        except Exception as e:
            print(f"Erro ao analisar arquivo: {e}")
            return {}
            
    def _analisar_python(self, codigo: str) -> dict:
        """Analisa código Python"""
        tree = ast.parse(codigo)
        return {
            "imports": self._extrair_imports_python(tree),
            "classes": self._extrair_classes_python(tree),
            "funcoes": self._extrair_funcoes_python(tree),
            "sugestoes": self._gerar_sugestoes_python(tree, codigo)
        }
        
    def _analisar_javascript(self, codigo: str) -> dict:
        """Analisa código JavaScript"""
        try:
            tree = esprima.parseScript(codigo, {"loc": True, "range": True})
            return {
                "imports": self._extrair_imports_javascript(tree),
                "classes": self._extrair_classes_javascript(tree),
                "funcoes": self._extrair_funcoes_javascript(tree),
                "sugestoes": self._gerar_sugestoes_javascript(tree, codigo)
            }
        except Exception as e:
            print(f"Erro ao analisar JavaScript: {e}")
            return {}
            
    def _analisar_java(self, codigo: str) -> dict:
        """Analisa código Java"""
        try:
            tree = javalang.parse.parse(codigo)
            return {
                "imports": self._extrair_imports_java(tree),
                "classes": self._extrair_classes_java(tree),
                "funcoes": self._extrair_funcoes_java(tree),
                "sugestoes": self._gerar_sugestoes_java(tree, codigo)
            }
        except Exception as e:
            print(f"Erro ao analisar Java: {e}")
            return {}
            
    def _analisar_cpp(self, codigo: str) -> dict:
        """Analisa código C++"""
        try:
            index = clang.cindex.Index.create()
            tu = index.parse("temp.cpp", unsaved_files=[("temp.cpp", codigo)])
            return {
                "includes": self._extrair_includes_cpp(tu.cursor),
                "classes": self._extrair_classes_cpp(tu.cursor),
                "funcoes": self._extrair_funcoes_cpp(tu.cursor),
                "sugestoes": self._gerar_sugestoes_cpp(tu.cursor, codigo)
            }
        except Exception as e:
            print(f"Erro ao analisar C++: {e}")
            return {}
            
    def _analisar_html(self, codigo: str) -> dict:
        """Analisa código HTML"""
        try:
            soup = BeautifulSoup(codigo, "html.parser")
            return {
                "meta": self._extrair_meta_html(soup),
                "estrutura": self._extrair_estrutura_html(soup),
                "scripts": self._extrair_scripts_html(soup),
                "estilos": self._extrair_estilos_html(soup),
                "sugestoes": self._gerar_sugestoes_html(soup, codigo)
            }
        except Exception as e:
            print(f"Erro ao analisar HTML: {e}")
            return {}
            
    def _analisar_css(self, codigo: str) -> dict:
        """Analisa código CSS"""
        try:
            regras = tinycss2.parse_stylesheet(codigo)
            return {
                "seletores": self._extrair_seletores_css(regras),
                "propriedades": self._extrair_propriedades_css(regras),
                "media_queries": self._extrair_media_queries_css(regras),
                "sugestoes": self._gerar_sugestoes_css(regras, codigo)
            }
        except Exception as e:
            print(f"Erro ao analisar CSS: {e}")
            return {}
            
    def _extrair_imports_python(self, tree: ast.AST) -> List[dict]:
        """Extrai imports de código Python"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "tipo": "import",
                        "modulo": alias.name,
                        "alias": alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append({
                        "tipo": "from",
                        "modulo": node.module,
                        "nome": alias.name,
                        "alias": alias.asname
                    })
        return imports
        
    def _extrair_imports_javascript(self, tree) -> List[dict]:
        """Extrai imports de código JavaScript"""
        imports = []
        for node in tree.body:
            if node.type == "ImportDeclaration":
                imports.append({
                    "tipo": "import",
                    "fonte": node.source.value,
                    "especificadores": [
                        {
                            "tipo": spec.type,
                            "nome": spec.local.name,
                            "importado": spec.imported.name if hasattr(spec, "imported") else None
                        }
                        for spec in node.specifiers
                    ]
                })
        return imports
        
    def _extrair_imports_java(self, tree) -> List[dict]:
        """Extrai imports de código Java"""
        imports = []
        for imp in tree.imports:
            imports.append({
                "tipo": "import",
                "pacote": imp.path,
                "estatico": imp.static,
                "wildcard": imp.wildcard
            })
        return imports
        
    def _extrair_includes_cpp(self, cursor) -> List[dict]:
        """Extrai includes de código C++"""
        includes = []
        for node in cursor.get_children():
            if node.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE:
                includes.append({
                    "nome": node.displayname,
                    "sistema": node.is_system_include()
                })
        return includes
        
    def _extrair_meta_html(self, soup) -> dict:
        """Extrai metadados de HTML"""
        meta = {}
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if tag.get("name"):
                meta[tag["name"]] = tag.get("content")
            elif tag.get("property"):
                meta[tag["property"]] = tag.get("content")
        return meta
        
    def _extrair_seletores_css(self, regras) -> List[dict]:
        """Extrai seletores de CSS"""
        seletores = []
        for regra in regras:
            if regra.type == "qualified-rule":
                seletores.append({
                    "seletor": regra.prelude,
                    "especificidade": self._calcular_especificidade_css(regra.prelude)
                })
        return seletores
        
    def _gerar_sugestoes_python(self, tree: ast.AST, codigo: str) -> List[str]:
        """Gera sugestões para código Python"""
        sugestoes = []
        
        # Verifica número de argumentos em funções
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 5:
                    sugestoes.append(
                        f"A função '{node.name}' tem muitos argumentos ({len(node.args.args)}). "
                        "Considere refatorar usando uma classe ou dataclass."
                    )
                    
                if not node.returns and not isinstance(node, ast.AsyncFunctionDef):
                    sugestoes.append(
                        f"A função '{node.name}' não tem tipo de retorno definido. "
                        "Considere adicionar anotações de tipo."
                    )
                    
                if not ast.get_docstring(node):
                    sugestoes.append(
                        f"A função '{node.name}' não tem docstring. "
                        "Adicione documentação para melhor manutenibilidade."
                    )
        
        # Verifica imports não utilizados
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.name)
                    
        for imp in imports:
            if imp not in codigo:
                sugestoes.append(f"O import '{imp}' parece não estar sendo utilizado.")
                
        return sugestoes
        
    def _gerar_sugestoes_javascript(self, tree, codigo: str) -> List[str]:
        """Gera sugestões para código JavaScript"""
        sugestoes = []
        
        # Verifica uso de var (sugere let/const)
        if "var " in codigo:
            sugestoes.append("Considere usar 'let' ou 'const' em vez de 'var' para melhor escopo de variáveis.")
            
        # Verifica funções muito longas
        for node in tree.body:
            if node.type == "FunctionDeclaration":
                if len(node.body.body) > 20:
                    sugestoes.append(
                        f"A função '{node.id.name}' é muito longa. "
                        "Considere dividir em funções menores."
                    )
                    
        return sugestoes
        
    def _gerar_sugestoes_java(self, tree, codigo: str) -> List[str]:
        """Gera sugestões para código Java"""
        sugestoes = []
        
        # Verifica classes muito longas
        for tipo in tree.types:
            if len(tipo.body) > 30:
                sugestoes.append(
                    f"A classe '{tipo.name}' tem muitos membros. "
                    "Considere dividir em classes menores."
                )
                
        return sugestoes
        
    def _gerar_sugestoes_cpp(self, cursor, codigo: str) -> List[str]:
        """Gera sugestões para código C++"""
        sugestoes = []
        
        # Verifica uso de ponteiros raw
        if "*" in codigo and "unique_ptr" not in codigo and "shared_ptr" not in codigo:
            sugestoes.append(
                "Considere usar smart pointers (unique_ptr/shared_ptr) "
                "em vez de ponteiros raw."
            )
            
        return sugestoes
        
    def _gerar_sugestoes_html(self, soup, codigo: str) -> List[str]:
        """Gera sugestões para código HTML"""
        sugestoes = []
        
        # Verifica presença de tags semânticas
        tags_semanticas = ["header", "nav", "main", "article", "section", "footer"]
        for tag in tags_semanticas:
            if not soup.find(tag):
                sugestoes.append(f"Considere usar a tag semântica <{tag}> para melhor estrutura.")
                
        return sugestoes
        
    def _gerar_sugestoes_css(self, regras, codigo: str) -> List[str]:
        """Gera sugestões para código CSS"""
        sugestoes = []
        
        # Verifica uso de !important
        if "!important" in codigo:
            sugestoes.append(
                "Evite usar !important. "
                "Considere melhorar a especificidade dos seletores."
            )
            
        return sugestoes
        
    def _calcular_especificidade_css(self, seletor: str) -> dict:
        """Calcula a especificidade de um seletor CSS"""
        return {
            "id": len(re.findall(r"#[\w-]+", seletor)),
            "classe": len(re.findall(r"\.[\w-]+", seletor)),
            "elemento": len(re.findall(r"^[\w-]+|\s+[\w-]+", seletor))
        }

class MonitorArquivos(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.arquivos_modificados = set()
        self.lock = threading.Lock()
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            with self.lock:
                self.arquivos_modificados.add(event.src_path)
                self.callback(event.src_path)

class AssistenteProgramacao:
    def __init__(self):
        self.perfil = PerfilUsuario()
        self.config = GerenciadorConfiguracoes()
        self.seletor = SeletorLinguagem()
        self.analisador = AnalisadorCodigo()
        self.monitor = None
        self.observer = None
        self.interface = None
        
        # Inicializa estado
        self.arquivos_abertos = set()
        self.fila_analise = queue.Queue()
        
        # Inicializa monitoramento
        self.observer = Observer()
        self.monitor = MonitorArquivos(self._arquivo_modificado)
        self.observer.start()
        
        # Inicializa interface
        self._inicializar_interface()
        
        # Inicia thread de processamento
        threading.Thread(target=self._processar_analise, daemon=True).start()
        
        # Registra observador de configurações
        self.config.adicionar_observador(self._configuracao_alterada)
        
    def _configuracao_alterada(self, caminho: str, valor: Any):
        """Callback chamado quando uma configuração é alterada"""
        if caminho and caminho.startswith("preferencias.tema"):
            if self.interface:
                self.interface.aplicar_tema()
        elif caminho and caminho.startswith("preferencias.interface"):
            if self.interface:
                self.interface.atualizar_interface()
        elif caminho and caminho.startswith("preferencias.editor"):
            if self.interface:
                self.interface.atualizar_editores()
                
    def executar_acao(self, comando: str):
        """Executa uma ação baseada no comando do usuário"""
        comando = comando.lower()
        
        # Comandos relacionados a mídia
        if "assistir" in comando:
            if "filme" in comando:
                sugestoes = self.perfil.sugerir_midia("filme")
                if sugestoes:
                    print(f"Baseado nos seus gostos, sugiro: {', '.join(sugestoes)}")
            elif "série" in comando or "serie" in comando:
                sugestoes = self.perfil.sugerir_midia("serie")
                if sugestoes:
                    print(f"Você pode continuar assistindo: {', '.join(sugestoes)}")
        
        # Comandos de automação
        elif "abrir" in comando:
            if "navegador" in comando:
                self.perfil.iniciar_navegador()
            elif "whatsapp" in comando:
                self.perfil.navegar_site("https://web.whatsapp.com")
        
        # Comandos de mensagem
        elif "enviar mensagem" in comando:
            # Exemplo: "enviar mensagem para João: olá"
            partes = comando.split(":")
            if len(partes) == 2:
                destinatario = partes[0].split("para")[1].strip()
                mensagem = partes[1].strip()
                self.perfil.enviar_mensagem("whatsapp", destinatario, mensagem)
        
        # Registra a atividade
        self.perfil.registrar_atividade("comando", {"texto": comando})
        
    def atualizar_preferencias(self, novas_prefs: dict):
        """Atualiza as preferências do usuário"""
        self.perfil.dados["preferencias"].update(novas_prefs)
        self.perfil.salvar_dados()
        
    def obter_sugestoes_personalizadas(self) -> dict:
        """Retorna sugestões personalizadas baseadas no perfil"""
        sugestoes = {
            "apps": list(self.perfil.dados["preferencias"]["apps"]["mais_usados"].keys())[:5],
            "sites": list(self.perfil.dados["preferencias"]["navegador"]["sites_frequentes"].keys())[:5]
        }
        return sugestoes
        
    def registrar_uso_app(self, app: str):
        """Registra o uso de um aplicativo"""
        apps = self.perfil.dados["preferencias"]["apps"]["mais_usados"]
        apps[app] = apps.get(app, 0) + 1
        self.perfil.salvar_dados()
        
    def registrar_acesso_site(self, url: str):
        """Registra o acesso a um site"""
        sites = self.perfil.dados["preferencias"]["navegador"]["sites_frequentes"]
        sites[url] = sites.get(url, 0) + 1
        self.perfil.salvar_dados()
        
    def obter_tema_preferido(self) -> str:
        """Retorna o tema preferido do usuário"""
        return self.config.obter_configuracao("preferencias.tema.padrao", "dark")
        
    def definir_tema(self, tema: str):
        """Define o tema preferido do usuário"""
        self.config.definir_configuracao("preferencias.tema.padrao", tema)
        
    def obter_configuracoes_editor(self) -> dict:
        """Retorna as configurações do editor"""
        return self.config.obter_config_editor()
        
    def obter_configuracoes_analise(self) -> dict:
        """Retorna as configurações de análise"""
        return self.config.obter_config_analise()
        
    def obter_configuracoes_sugestoes(self) -> dict:
        """Retorna as configurações de sugestões"""
        return self.config.obter_config_sugestoes()
        
    def obter_configuracoes_notificacoes(self) -> dict:
        """Retorna as configurações de notificações"""
        return self.config.obter_config_notificacoes()
        
    def restaurar_configuracoes_padrao(self):
        """Restaura todas as configurações para o padrão"""
        self.config.restaurar_padrao()
        
    def _inicializar_interface(self):
        """Inicializa a interface gráfica"""
        self.interface = InterfaceProgramacao(self)
        
    def mostrar_interface(self):
        """Mostra a interface gráfica"""
        if self.interface:
            self.interface.show()
            
    def _arquivo_modificado(self, caminho):
        """Callback chamado quando um arquivo é modificado"""
        if caminho in self.arquivos_abertos:
            print(f"Arquivo modificado: {caminho}")
            self.fila_analise.put(caminho)
            
    def _processar_analise(self):
        """Processa arquivos na fila de análise"""
        while True:
            try:
                caminho = self.fila_analise.get(timeout=1)
                if caminho:
                    sugestoes = self.analisar_arquivo(caminho)
                    if sugestoes:
                        self.interface.atualizar_sugestoes(caminho, sugestoes)
            except queue.Empty:
                continue
                
    def analisar_arquivo(self, caminho):
        """Analisa um arquivo Python"""
        try:
            return self.analisador.analisar_arquivo(caminho)
        except Exception as e:
            print(f"Erro ao analisar arquivo: {e}")
            return None
            
    def sugerir_codigo(self, resultado):
        """Gera sugestões de código baseadas na análise"""
        sugestoes = []
        
        if "funcoes" in resultado:
            for funcao in resultado["funcoes"]:
                if funcao["argumentos"] > 5:
                    sugestoes.append(
                        f"Refatore a função '{funcao['nome']}' para usar menos argumentos"
                    )
                if not funcao["docstring"]:
                    sugestoes.append(
                        f"Adicione documentação para a função '{funcao['nome']}'"
                    )
                    
        if "imports" in resultado:
            imports_nao_usados = [imp for imp in resultado["imports"] if not imp.get("usado", True)]
            if imports_nao_usados:
                sugestoes.append("Remova os imports não utilizados")
                
        return sugestoes
            
    def finalizar(self):
        """Finaliza o assistente"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.interface = None

    def iniciar_monitoramento(self, diretorio):
        """Inicia o monitoramento de um diretório"""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.schedule(self.monitor, diretorio, recursive=False)
        except Exception as e:
            print(f"Erro ao iniciar monitoramento: {e}")

    def sugerir_linguagem(self, descricao: str) -> Dict[str, Any]:
        """Sugere a melhor linguagem para um projeto"""
        sugestoes = self.seletor.sugerir_linguagem(descricao)
        
        if not sugestoes:
            return {
                "linguagem": "python",
                "frameworks": [],
                "motivo": "Nenhuma sugestão específica encontrada. Python é uma boa escolha geral."
            }
            
        melhor_opcao = sugestoes[0]
        tipo_projeto = self._identificar_tipo_projeto(descricao)
        frameworks = self.seletor.obter_frameworks(melhor_opcao["linguagem"], tipo_projeto)
        
        return {
            "linguagem": melhor_opcao["linguagem"],
            "frameworks": frameworks,
            "motivo": self._gerar_justificativa(melhor_opcao, tipo_projeto),
            "alternativas": sugestoes[1:]
        }
        
    def _identificar_tipo_projeto(self, descricao: str) -> str:
        """Identifica o tipo de projeto baseado na descrição"""
        descricao = descricao.lower()
        
        if "web" in descricao or "site" in descricao:
            if "frontend" in descricao or "interface" in descricao:
                return "web"
            return "backend"
            
        if "gui" in descricao or "interface gráfica" in descricao:
            return "gui"
            
        if "jogo" in descricao:
            return "jogos"
            
        if "dados" in descricao or "análise" in descricao:
            return "dados"
            
        if "automação" in descricao or "automatizar" in descricao:
            return "automacao"
            
        return "geral"
        
    def _gerar_justificativa(self, sugestao: Dict[str, Any], tipo_projeto: str) -> str:
        """Gera uma justificativa para a sugestão de linguagem"""
        linguagem = sugestao["linguagem"]
        caracteristicas = self.seletor.caracteristicas_linguagens[linguagem]
        
        pontos_fortes = []
        if caracteristicas["facilidade"] >= 8:
            pontos_fortes.append("fácil de aprender e usar")
        if caracteristicas["performance"] >= 8:
            pontos_fortes.append("excelente performance")
        if caracteristicas["ecosystem"] >= 8:
            pontos_fortes.append("rico ecossistema de bibliotecas")
        if caracteristicas[tipo_projeto] >= 8:
            pontos_fortes.append(f"ótima para {tipo_projeto}")
            
        return f"{linguagem.capitalize()} é recomendada por ser {', '.join(pontos_fortes)}."

    def criar_projeto(self, nome: str, descricao: str, caminho: Optional[str] = None) -> bool:
        """Cria um novo projeto com a estrutura adequada"""
        try:
            sugestao = self.sugerir_linguagem(descricao)
            linguagem = sugestao["linguagem"]
            frameworks = sugestao["frameworks"]
            
            # Define o caminho do projeto
            if not caminho:
                caminho = Path.cwd() / nome
            else:
                caminho = Path(caminho) / nome
                
            # Cria a estrutura básica
            caminho.mkdir(parents=True, exist_ok=True)
            
            # Cria arquivos específicos da linguagem
            self._criar_estrutura_projeto(caminho, linguagem, frameworks)
            
            # Registra o projeto no perfil
            self.perfil.registrar_atividade("projeto", {
                "nome": nome,
                "linguagem": linguagem,
                "frameworks": frameworks,
                "caminho": str(caminho)
            })
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar projeto: {e}")
            return False
            
    def _criar_estrutura_projeto(self, caminho: Path, linguagem: str, frameworks: List[str]):
        """Cria a estrutura de arquivos do projeto"""
        # Cria diretórios comuns
        (caminho / "src").mkdir(exist_ok=True)
        (caminho / "tests").mkdir(exist_ok=True)
        (caminho / "docs").mkdir(exist_ok=True)
        
        # Cria arquivos específicos da linguagem
        if linguagem == "python":
            self._criar_estrutura_python(caminho, frameworks)
        elif linguagem == "javascript":
            self._criar_estrutura_javascript(caminho, frameworks)
        elif linguagem == "java":
            self._criar_estrutura_java(caminho, frameworks)
        elif linguagem == "cpp":
            self._criar_estrutura_cpp(caminho, frameworks)
            
    def _criar_estrutura_python(self, caminho: Path, frameworks: List[str]):
        """Cria estrutura para projeto Python"""
        # Cria arquivo requirements.txt
        with open(caminho / "requirements.txt", "w") as f:
            for framework in frameworks:
                f.write(f"{framework}\n")
                
        # Cria arquivo setup.py
        with open(caminho / "setup.py", "w") as f:
            f.write(f"""from setuptools import setup, find_packages

setup(
    name="{caminho.name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        {', '.join(f"'{fw}'" for fw in frameworks)}
    ],
)""")
        
        # Cria __init__.py
        (caminho / "src" / "__init__.py").touch()
        (caminho / "tests" / "__init__.py").touch()
        
        # Cria arquivo principal
        with open(caminho / "src" / "main.py", "w") as f:
            f.write("""def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()""")
            
    def _criar_estrutura_javascript(self, caminho: Path, frameworks: List[str]):
        """Cria estrutura para projeto JavaScript"""
        # Cria package.json
        with open(caminho / "package.json", "w") as f:
            json.dump({
                "name": caminho.name,
                "version": "1.0.0",
                "description": "",
                "main": "index.js",
                "scripts": {
                    "test": "echo \\"Error: no test specified\\" && exit 1"
                },
                "keywords": [],
                "author": "",
                "license": "ISC",
                "dependencies": {
                    fw: "latest" for fw in frameworks
                }
            }, f, indent=2)
            
        # Cria arquivo principal
        with open(caminho / "src" / "index.js", "w") as f:
            f.write("""console.log('Hello, World!');""")
            
    def _criar_estrutura_java(self, caminho: Path, frameworks: List[str]):
        """Cria estrutura para projeto Java"""
        # Cria pom.xml para Maven
        with open(caminho / "pom.xml", "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>{caminho.name}</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
</project>""")
            
        # Cria estrutura de pacotes
        src_main = caminho / "src" / "main" / "java" / "com" / "example"
        src_main.mkdir(parents=True)
        
        # Cria arquivo principal
        with open(src_main / "Main.java", "w") as f:
            f.write("""package com.example;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}""")
            
    def _criar_estrutura_cpp(self, caminho: Path, frameworks: List[str]):
        """Cria estrutura para projeto C++"""
        # Cria CMakeLists.txt
        with open(caminho / "CMakeLists.txt", "w") as f:
            f.write(f"""cmake_minimum_required(VERSION 3.10)
project({caminho.name})

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${{PROJECT_NAME}} src/main.cpp)""")
            
        # Cria arquivo principal
        with open(caminho / "src" / "main.cpp", "w") as f:
            f.write("""#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}""") 