from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt
import re
from typing import Dict, List, Optional

class DestacadorSintaxeMultilinguagem(QSyntaxHighlighter):
    def __init__(self, parent=None, linguagem: str = "python"):
        super().__init__(parent)
        self.linguagem = linguagem.lower()
        self.formatos = {}
        self._configurar_formatos()
        self._configurar_regras()
    
    def _configurar_formatos(self):
        """Configura os formatos de cores para diferentes elementos"""
        # Palavras-chave
        self.formatos["keyword"] = self._criar_formato("#569CD6", True)
        # Tipos
        self.formatos["type"] = self._criar_formato("#4EC9B0", True)
        # Strings
        self.formatos["string"] = self._criar_formato("#CE9178")
        # Números
        self.formatos["number"] = self._criar_formato("#B5CEA8")
        # Comentários
        self.formatos["comment"] = self._criar_formato("#6A9955", italic=True)
        # Operadores
        self.formatos["operator"] = self._criar_formato("#D4D4D4")
        # Funções
        self.formatos["function"] = self._criar_formato("#DCDCAA")
        # Variáveis
        self.formatos["variable"] = self._criar_formato("#9CDCFE")
        # Decoradores
        self.formatos["decorator"] = self._criar_formato("#569CD6")
        # Tags HTML/XML
        self.formatos["tag"] = self._criar_formato("#569CD6")
        # Atributos HTML/XML
        self.formatos["attribute"] = self._criar_formato("#9CDCFE")
        
    def _criar_formato(self, cor: str, negrito: bool = False, italic: bool = False) -> QTextCharFormat:
        """Cria um formato de texto com as propriedades especificadas"""
        formato = QTextCharFormat()
        formato.setForeground(QColor(cor))
        if negrito:
            formato.setFontWeight(700)
        if italic:
            formato.setFontItalic(True)
        return formato
    
    def _configurar_regras(self):
        """Configura as regras de highlight baseado na linguagem"""
        self.regras = []
        
        if self.linguagem == "python":
            self._configurar_regras_python()
        elif self.linguagem == "javascript":
            self._configurar_regras_javascript()
        elif self.linguagem == "html":
            self._configurar_regras_html()
        elif self.linguagem == "css":
            self._configurar_regras_css()
        elif self.linguagem == "java":
            self._configurar_regras_java()
        elif self.linguagem == "cpp":
            self._configurar_regras_cpp()
        else:
            self._configurar_regras_python()  # Fallback para Python
            
    def _configurar_regras_python(self):
        """Configura regras para Python"""
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield'
        ]
        
        tipos = ['int', 'float', 'str', 'list', 'dict', 'set', 'tuple', 'bool']
        
        self._adicionar_regras_comuns(keywords, tipos)
        self.regras.append((r'@\w+', 'decorator'))
        
    def _configurar_regras_javascript(self):
        """Configura regras para JavaScript"""
        keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'new', 'return',
            'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void',
            'while', 'with', 'yield', 'let', 'static', 'enum', 'await', 'async'
        ]
        
        tipos = ['Array', 'Boolean', 'Date', 'Error', 'Function', 'Math', 'Number',
                'Object', 'RegExp', 'String', 'Promise']
        
        self._adicionar_regras_comuns(keywords, tipos)
        self.regras.append((r'(\$|jQuery)', 'function'))
        
    def _configurar_regras_html(self):
        """Configura regras para HTML"""
        self.regras.extend([
            (r'<[!?]?[a-zA-Z0-9_-]+', 'tag'),
            (r'</[a-zA-Z0-9_-]+>', 'tag'),
            (r'[a-zA-Z-]+(?=\s*=)', 'attribute'),
            (r'>', 'tag'),
            (r'<!--.*?-->', 'comment'),
        ])
        
    def _configurar_regras_css(self):
        """Configura regras para CSS"""
        keywords = [
            'align', 'background', 'border', 'bottom', 'clear', 'color',
            'cursor', 'display', 'float', 'font', 'height', 'left',
            'margin', 'padding', 'position', 'right', 'size', 'top',
            'transform', 'transition', 'width'
        ]
        
        self.regras.extend([
            (r'#[0-9A-Fa-f]{3,6}\b', 'number'),
            (r'\.[A-Za-z0-9_-]+', 'class'),
            (r'#[A-Za-z0-9_-]+', 'id'),
            (r'@\w+', 'decorator'),
            (r'/\*.*?\*/', 'comment'),
        ])
        
        for keyword in keywords:
            self.regras.append((fr'\b{keyword}\b', 'keyword'))
            
    def _configurar_regras_java(self):
        """Configura regras para Java"""
        keywords = [
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'final', 'finally', 'float', 'for',
            'if', 'implements', 'import', 'instanceof', 'int', 'interface',
            'long', 'native', 'new', 'package', 'private', 'protected', 'public',
            'return', 'short', 'static', 'strictfp', 'super', 'switch',
            'synchronized', 'this', 'throw', 'throws', 'transient', 'try',
            'void', 'volatile', 'while'
        ]
        
        tipos = ['String', 'Integer', 'Boolean', 'Double', 'Float', 'Long',
                'Object', 'Class', 'Exception', 'System']
        
        self._adicionar_regras_comuns(keywords, tipos)
        self.regras.append((r'@\w+', 'decorator'))
        
    def _configurar_regras_cpp(self):
        """Configura regras para C++"""
        keywords = [
            'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand',
            'bitor', 'bool', 'break', 'case', 'catch', 'char', 'char16_t',
            'char32_t', 'class', 'compl', 'const', 'constexpr', 'const_cast',
            'continue', 'decltype', 'default', 'delete', 'do', 'double',
            'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern',
            'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int',
            'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq',
            'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected',
            'public', 'register', 'reinterpret_cast', 'return', 'short',
            'signed', 'sizeof', 'static', 'static_assert', 'static_cast',
            'struct', 'switch', 'template', 'this', 'thread_local', 'throw',
            'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned',
            'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor',
            'xor_eq'
        ]
        
        tipos = ['string', 'vector', 'map', 'set', 'list', 'queue', 'stack',
                'pair', 'array', 'deque']
        
        self._adicionar_regras_comuns(keywords, tipos)
        self.regras.extend([
            (r'#include\s*[<"].*[>"]', 'keyword'),
            (r'#\w+', 'keyword'),
        ])
        
    def _adicionar_regras_comuns(self, keywords: List[str], tipos: List[str]):
        """Adiciona regras comuns para várias linguagens"""
        # Keywords
        self.regras.append((r'\b(' + '|'.join(keywords) + r')\b', 'keyword'))
        
        # Tipos
        self.regras.append((r'\b(' + '|'.join(tipos) + r')\b', 'type'))
        
        # Strings
        self.regras.extend([
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'string'),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'string'),
        ])
        
        # Números
        self.regras.append((r'\b\d+\b', 'number'))
        
        # Funções
        self.regras.append((r'\b\w+(?=\s*\()', 'function'))
        
        # Comentários de linha única
        self.regras.append((r'//[^\n]*', 'comment'))
        
        # Comentários de múltiplas linhas
        self.regras.append((r'/\*.*?\*/', 'comment'))
        
    def highlightBlock(self, texto: str):
        """Aplica o highlighting no bloco de texto"""
        for padrao, tipo in self.regras:
            formato = self.formatos[tipo]
            for match in re.finditer(padrao, texto):
                inicio = match.start()
                tamanho = match.end() - inicio
                self.setFormat(inicio, tamanho, formato)

class EditorCodigo(QPlainTextEdit):
    def __init__(self, parent=None, linguagem: str = "python"):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(40)
        self.destacador = DestacadorSintaxeMultilinguagem(self.document(), linguagem)
        
    def definir_linguagem(self, linguagem: str):
        """Define a linguagem do editor"""
        self.destacador = DestacadorSintaxeMultilinguagem(self.document(), linguagem)
// ... existing code ... 