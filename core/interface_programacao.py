from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QTextEdit, QTreeView, QSplitter, QLabel,
                            QStatusBar, QToolBar, QMenu, QFileDialog, QMessageBox,
                            QApplication, QPushButton, QComboBox, QSystemTrayIcon,
                            QActionGroup, QScrollArea, QPlainTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QFileInfo, QThread, QMetaObject, Q_ARG
from PyQt6.QtGui import (QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QAction,
                      QStandardItemModel, QStandardItem, QIcon, QPixmap, QPalette, QTextOption,
                      QTextCursor, QTextFormat, QKeyEvent, QPaintEvent, QResizeEvent, QPainter, QSize)
import os
from pathlib import Path
import webbrowser

class EditorSintaxe(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formatos = {}
        self._configurar_formatos()
        self._configurar_regras()
    
    def _configurar_formatos(self):
        # Palavras-chave
        formato_keyword = QTextCharFormat()
        formato_keyword.setForeground(QColor("#C678DD"))
        formato_keyword.setFontWeight(QFont.Weight.Bold)
        self.formatos["keyword"] = formato_keyword
        
        # Strings
        formato_string = QTextCharFormat()
        formato_string.setForeground(QColor("#98C379"))
        self.formatos["string"] = formato_string
        
        # Números
        formato_number = QTextCharFormat()
        formato_number.setForeground(QColor("#D19A66"))
        self.formatos["number"] = formato_number
        
        # Comentários
        formato_comment = QTextCharFormat()
        formato_comment.setForeground(QColor("#5C6370"))
        formato_comment.setFontItalic(True)
        self.formatos["comment"] = formato_comment
    
    def _configurar_regras(self):
        """Configura as regras de highlight"""
        self.regras = []
        
        # Palavras-chave do Python
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield'
        ]
        
        # Adiciona regras para palavras-chave
        for palavra in keywords:
            padrao = f'\\b{palavra}\\b'
            self.regras.append((padrao, 'keyword'))
        
        # Strings
        self.regras.extend([
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'string'),  # String com aspas duplas
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'string'),  # String com aspas simples
        ])
        
        # Números
        self.regras.append((r'\b[0-9]+\b', 'number'))
        
        # Comentários
        self.regras.append((r'#[^\n]*', 'comment'))
    
    def highlightBlock(self, texto: str):
        """Implementa o highlight de sintaxe"""
        import re
        
        # Aplica as regras de highlight
        for padrao, tipo in self.regras:
            for match in re.finditer(padrao, texto):
                inicio = match.start()
                tamanho = match.end() - inicio
                self.setFormat(inicio, tamanho, self.formatos[tipo])

class EditorCodigo(QPlainTextEdit):
    def __init__(self, parent=None, linguagem=None):
        super().__init__(parent)
        self.setup_editor()
        self.linguagem = linguagem
        
    def setup_editor(self):
        """Configura o editor"""
        # Configurações básicas
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopWidth(4 * self.fontMetrics().width(' '))
        
        # Área de números de linha
        self.numeros_linha = NumerosLinha(self)
        
        # Destaque de sintaxe
        self.highlighter = None
        
        # Configurações padrão
        self.mostrar_numeros = True
        self.destacar_linha_atual = True
        self.mostrar_espacos = True
        self.auto_indentacao = True
        self.auto_completar = True
        self.auto_fechar_chaves = True
        self.auto_fechar_tags = True
        self.destacar_sintaxe = True
        
        # Conecta sinais
        self.cursorPositionChanged.connect(self.destacar_linha_atual_slot)
        self.textChanged.connect(self.texto_alterado)
        
    def setShowLineNumbers(self, show: bool):
        """Define se mostra números de linha"""
        self.mostrar_numeros = show
        self.numeros_linha.setVisible(show)
        self.updateGeometry()
        
    def setHighlightCurrentLine(self, highlight: bool):
        """Define se destaca a linha atual"""
        self.destacar_linha_atual = highlight
        self.destacar_linha_atual_slot()
        
    def setShowSpaces(self, show: bool):
        """Define se mostra espaços em branco"""
        self.mostrar_espacos = show
        option = self.document().defaultTextOption()
        option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces if show
                       else option.flags() & ~QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(option)
        
    def setAutoIndentation(self, enable: bool):
        """Define se usa auto indentação"""
        self.auto_indentacao = enable
        
    def setAutoCompletion(self, enable: bool):
        """Define se usa auto completar"""
        self.auto_completar = enable
        
    def setAutoCloseBrackets(self, enable: bool):
        """Define se fecha chaves automaticamente"""
        self.auto_fechar_chaves = enable
        
    def setAutoCloseTags(self, enable: bool):
        """Define se fecha tags automaticamente"""
        self.auto_fechar_tags = enable
        
    def setSyntaxHighlighting(self, enable: bool):
        """Define se usa destaque de sintaxe"""
        self.destacar_sintaxe = enable
        if enable and not self.highlighter:
            self.highlighter = EditorSintaxe(self.document())
        elif not enable and self.highlighter:
            self.highlighter.setDocument(None)
            self.highlighter = None
            
    def keyPressEvent(self, event: QKeyEvent):
        """Trata eventos de teclado"""
        # Auto indentação
        if self.auto_indentacao and event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            texto = block.text()
            indentacao = len(texto) - len(texto.lstrip())
            super().keyPressEvent(event)
            if indentacao > 0:
                cursor = self.textCursor()
                cursor.insertText(" " * indentacao)
            return
            
        # Auto fechar chaves
        if self.auto_fechar_chaves and event.text() in "({[":
            cursor = self.textCursor()
            fechamento = {"(": ")", "{": "}", "[": "]"}[event.text()]
            super().keyPressEvent(event)
            cursor.insertText(fechamento)
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return
            
        # Auto fechar tags
        if self.auto_fechar_tags and event.text() == "<":
            cursor = self.textCursor()
            super().keyPressEvent(event)
            cursor.insertText(">")
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return
            
        super().keyPressEvent(event)
        
    def texto_alterado(self):
        """Chamado quando o texto é alterado"""
        if self.auto_completar:
            cursor = self.textCursor()
            texto = cursor.block().text()[:cursor.positionInBlock()]
            if texto.strip():
                # Aqui você pode implementar a lógica de auto completar
                pass
                
    def destacar_linha_atual_slot(self):
        """Destaca a linha atual"""
        if not self.destacar_linha_atual:
            self.setExtraSelections([])
            return
            
        selecao = QTextEdit.ExtraSelection()
        cor = self.palette().color(QPalette.Highlight).lighter(160)
        selecao.format.setBackground(cor)
        selecao.format.setProperty(QTextFormat.FullWidthSelection, True)
        selecao.cursor = self.textCursor()
        selecao.cursor.clearSelection()
        
        self.setExtraSelections([selecao])
        
    def resizeEvent(self, event: QResizeEvent):
        """Trata evento de redimensionamento"""
        super().resizeEvent(event)
        if self.mostrar_numeros:
            cr = self.contentsRect()
            self.numeros_linha.setGeometry(
                QRect(cr.left(), cr.top(), 
                     self.numeros_linha.largura_necessaria(), cr.height())
            )
            
    def paintEvent(self, event: QPaintEvent):
        """Trata evento de pintura"""
        if self.mostrar_numeros:
            self.numeros_linha.update(
                0, event.rect().y(),
                self.numeros_linha.width(), event.rect().height()
            )
        super().paintEvent(event)

class NumerosLinha(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFont(editor.font())
        
    def sizeHint(self):
        """Retorna o tamanho sugerido do widget"""
        return QSize(self.largura_necessaria(), 0)
        
    def largura_necessaria(self):
        """Calcula a largura necessária para os números"""
        digitos = 1
        maximo = max(1, self.editor.blockCount())
        while maximo >= 10:
            maximo //= 10
            digitos += 1
        espaco = 3 + self.fontMetrics().width('9') * digitos
        return espaco
        
    def paintEvent(self, event):
        """Pinta os números de linha"""
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
        
        block = self.editor.firstVisibleBlock()
        numero_bloco = block.blockNumber()
        topo = self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()
        ).top()
        bottom = topo + self.editor.blockBoundingRect(block).height()
        
        while block.isValid() and topo <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                numero = str(numero_bloco + 1)
                painter.setPen(self.palette().color(QPalette.Text))
                painter.drawText(
                    0, topo,
                    self.width() - 2, self.fontMetrics().height(),
                    Qt.AlignRight, numero
                )
                
            block = block.next()
            topo = bottom
            bottom = topo + self.editor.blockBoundingRect(block).height()
            numero_bloco += 1

class ArvoreArquivos(QTreeView):
    arquivo_selecionado = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTreeView {
                background-color: #21252B;
                color: #ABB2BF;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #2C313A;
            }
            QTreeView::item:selected {
                background-color: #3E4451;
            }
        """)
        
        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels(['Nome'])
        self.setModel(self.modelo)
        
        # Carrega a estrutura de arquivos
        self.carregar_arquivos()
    
    def carregar_arquivos(self, diretorio='.'):
        """Carrega a estrutura de arquivos do diretório"""
        self.modelo.clear()
        self.modelo.setHorizontalHeaderLabels(['Nome'])
        
        raiz = QStandardItem(os.path.basename(diretorio))
        self.modelo.appendRow(raiz)
        self._carregar_diretorio(Path(diretorio), raiz)
    
    def _carregar_diretorio(self, diretorio: Path, item_pai=None):
        """Carrega um diretório na árvore de arquivos"""
        try:
            if item_pai is None:
                item_pai = self.modelo
            
            # Limita a profundidade da recursão
            profundidade_atual = 0
            item_temp = item_pai
            while item_temp and item_temp != self.modelo:
                profundidade_atual += 1
                item_temp = item_temp.parent()
            
            if profundidade_atual > 5:  # Limita a 5 níveis de profundidade
                return
            
            # Lista arquivos e diretórios
            try:
                for caminho in diretorio.iterdir():
                    if caminho.is_file() and caminho.suffix == '.py':
                        item = QStandardItem(caminho.name)
                        item.setData(caminho, Qt.ItemDataRole.UserRole)
                        item_pai.appendRow(item)
                    elif caminho.is_dir() and not caminho.name.startswith('.'):
                        item_dir = QStandardItem(caminho.name)
                        self._carregar_diretorio(caminho, item_dir)
                        item_pai.appendRow(item_dir)
            except PermissionError:
                pass  # Ignora diretórios sem permissão
            except Exception as e:
                print(f"Erro ao carregar diretório: {e}")
        except Exception as e:
            print(f"Erro ao carregar diretório: {e}")

class PainelSugestoes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do painel"""
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Sugestões")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(titulo)
        
        # Container de sugestões
        self.container_sugestoes = QWidget()
        self.layout_sugestoes = QVBoxLayout(self.container_sugestoes)
        layout.addWidget(self.container_sugestoes)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidget(self.container_sugestoes)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Botão de atualizar
        btn_atualizar = QPushButton("Atualizar Sugestões")
        btn_atualizar.clicked.connect(self.solicitar_atualizacao)
        layout.addWidget(btn_atualizar)
        
    def atualizar_sugestoes(self, sugestoes):
        """Atualiza o painel com novas sugestões"""
        # Limpa sugestões anteriores
        for i in reversed(range(self.layout_sugestoes.count())): 
            self.layout_sugestoes.itemAt(i).widget().setParent(None)
            
        if isinstance(sugestoes, dict):
            for categoria, itens in sugestoes.items():
                # Adiciona título da categoria
                label_categoria = QLabel(f"=== {categoria.upper()} ===")
                label_categoria.setStyleSheet("""
                    font-weight: bold;
                    color: #4a9eff;
                    padding: 5px;
                    border-bottom: 1px solid #4a9eff;
                """)
                self.layout_sugestoes.addWidget(label_categoria)
                
                # Adiciona itens
                if isinstance(itens, list):
                    for item in itens:
                        container_item = QWidget()
                        layout_item = QHBoxLayout(container_item)
                        
                        # Ícone ou bullet point
                        icone = QLabel("•")
                        icone.setStyleSheet("color: #4a9eff; font-size: 16px;")
                        layout_item.addWidget(icone)
                        
                        # Texto do item
                        label_item = QLabel(str(item))
                        label_item.setWordWrap(True)
                        layout_item.addWidget(label_item, 1)
                        
                        # Botão de ação (se aplicável)
                        if "http" in str(item) or "www." in str(item):
                            btn_abrir = QPushButton("Abrir")
                            btn_abrir.setFixedWidth(60)
                            btn_abrir.clicked.connect(lambda checked, url=item: self.abrir_url(url))
                            layout_item.addWidget(btn_abrir)
                            
                        self.layout_sugestoes.addWidget(container_item)
                else:
                    label_item = QLabel(str(itens))
                    label_item.setWordWrap(True)
                    self.layout_sugestoes.addWidget(label_item)
                    
                # Adiciona espaçamento entre categorias
                espaco = QWidget()
                espaco.setFixedHeight(10)
                self.layout_sugestoes.addWidget(espaco)
        elif isinstance(sugestoes, list):
            for sugestao in sugestoes:
                label = QLabel(f"• {sugestao}")
                label.setWordWrap(True)
                self.layout_sugestoes.addWidget(label)
        else:
            label = QLabel(str(sugestoes))
            label.setWordWrap(True)
            self.layout_sugestoes.addWidget(label)
            
        # Adiciona espaço flexível no final
        self.layout_sugestoes.addStretch()
        
    def solicitar_atualizacao(self):
        """Solicita atualização das sugestões"""
        if hasattr(self.parent(), "atualizar_sugestoes_personalizadas"):
            self.parent().atualizar_sugestoes_personalizadas()
            
    def abrir_url(self, url):
        """Abre uma URL no navegador"""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        webbrowser.open(url)

class InterfaceProgramacao(QMainWindow):
    def __init__(self, assistente):
        super().__init__()
        self.assistente = assistente
        self.arquivos_abertos = {}
        self.editor_atual = None
        
        # Carrega configurações
        self.tema_atual = self.assistente.obter_tema_preferido()
        self.config_linguagens = self.assistente.config.obter_configuracao('preferencias.linguagens')
        
        self.setup_ui()
        self.aplicar_tema()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        self.setWindowTitle("Assistente de Programação")
        self.resize(1200, 800)
        
        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        # Layout principal
        layout = QHBoxLayout(widget_central)
        
        # Árvore de arquivos
        self.arvore_arquivos = ArvoreArquivos()
        layout.addWidget(self.arvore_arquivos, 1)
        
        # Container central
        container_central = QWidget()
        layout_central = QVBoxLayout(container_central)
        layout.addWidget(container_central, 4)
        
        # Barra de ferramentas
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Seletor de linguagem
        self.combo_linguagem = QComboBox()
        self.combo_linguagem.addItems(self.config_linguagens['suportadas'].keys())
        self.combo_linguagem.setCurrentText(self.config_linguagens['padrao'])
        self.combo_linguagem.currentTextChanged.connect(self._linguagem_alterada)
        toolbar.addWidget(QLabel("Linguagem:"))
        toolbar.addWidget(self.combo_linguagem)
        
        # Tabs de arquivos
        self.tabs_arquivos = QTabWidget()
        self.tabs_arquivos.setTabsClosable(True)
        self.tabs_arquivos.tabCloseRequested.connect(self.fechar_arquivo)
        layout_central.addWidget(self.tabs_arquivos)
        
        # Painel de sugestões
        self.painel_sugestoes = PainelSugestoes()
        layout_central.addWidget(self.painel_sugestoes)
        
        # Menu
        self.criar_menu()
        
        # Atualiza sugestões personalizadas
        self.atualizar_sugestoes_personalizadas()
        
        # Aplica configurações de interface
        self.atualizar_interface()
        
    def criar_menu(self):
        """Cria o menu da aplicação"""
        menu_arquivo = self.menuBar().addMenu("&Arquivo")
        menu_exibir = self.menuBar().addMenu("&Exibir")
        menu_preferencias = self.menuBar().addMenu("&Preferências")
        menu_linguagem = self.menuBar().addMenu("&Linguagem")
        
        # Ações do menu Arquivo
        acao_novo = QAction("&Novo", self)
        acao_novo.setShortcut("Ctrl+N")
        acao_novo.triggered.connect(self.novo_arquivo)
        menu_arquivo.addAction(acao_novo)
        
        acao_abrir = QAction("&Abrir", self)
        acao_abrir.setShortcut("Ctrl+O")
        acao_abrir.triggered.connect(self.selecionar_arquivo)
        menu_arquivo.addAction(acao_abrir)
        
        acao_salvar = QAction("&Salvar", self)
        acao_salvar.setShortcut("Ctrl+S")
        acao_salvar.triggered.connect(self.salvar_arquivo)
        menu_arquivo.addAction(acao_salvar)
        
        menu_arquivo.addSeparator()
        
        acao_sair = QAction("Sai&r", self)
        acao_sair.setShortcut("Ctrl+Q")
        acao_sair.triggered.connect(self.close)
        menu_arquivo.addAction(acao_sair)
        
        # Menu Linguagem
        for linguagem in self.config_linguagens['suportadas'].keys():
            acao = QAction(linguagem.capitalize(), self)
            acao.triggered.connect(lambda checked, l=linguagem: self.definir_linguagem(l))
            menu_linguagem.addAction(acao)
        
        # Submenu Tema
        submenu_tema = menu_preferencias.addMenu("Tema")
        grupo_tema = QActionGroup(self)
        
        for tema in ["light", "dark"]:
            acao = QAction(tema.capitalize(), self, checkable=True)
            acao.setActionGroup(grupo_tema)
            if tema == self.tema_atual:
                acao.setChecked(True)
            acao.triggered.connect(lambda checked, t=tema: self.mudar_tema(t))
            submenu_tema.addAction(acao)
            
        # Submenu Layout
        submenu_layout = menu_preferencias.addMenu("Layout")
        config_layout = self.assistente.config.obter_layout()
        
        for opcao, valor in config_layout.items():
            acao = QAction(opcao.replace("_", " ").title(), self, checkable=True)
            acao.setChecked(valor)
            acao.triggered.connect(lambda checked, o=opcao: self.mudar_layout(o, checked))
            submenu_layout.addAction(acao)
            
        # Submenu Editor
        submenu_editor = menu_preferencias.addMenu("Editor")
        config_editor = self.assistente.config.obter_config_editor()
        
        for opcao, valor in config_editor.items():
            acao = QAction(opcao.replace("_", " ").title(), self, checkable=True)
            acao.setChecked(valor)
            acao.triggered.connect(lambda checked, o=opcao: self.mudar_config_editor(o, checked))
            submenu_editor.addAction(acao)
            
        # Ação Restaurar Padrão
        menu_preferencias.addSeparator()
        acao_restaurar = QAction("Restaurar Padrão", self)
        acao_restaurar.triggered.connect(self.restaurar_configuracoes)
        menu_preferencias.addAction(acao_restaurar)
            
    def mudar_tema(self, tema: str):
        """Muda o tema da interface"""
        self.tema_atual = tema
        self.assistente.definir_tema(tema)
        self.aplicar_tema()
        
    def aplicar_tema(self):
        """Aplica o tema atual à interface"""
        cores = self.assistente.config.obter_tema()
        fonte = self.assistente.config.obter_fonte()
        
        # Aplica fonte
        fonte_app = QFont(fonte["familia"], fonte["tamanho"])
        if fonte["estilo"] == "bold":
            fonte_app.setBold(True)
        elif fonte["estilo"] == "italic":
            fonte_app.setItalic(True)
        QApplication.setFont(fonte_app)
        
        # Aplica cores
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ 
                background-color: {cores["fundo"]};
                color: {cores["texto"]};
            }}
            QTextEdit, QPlainTextEdit {{ 
                background-color: {cores["fundo"]};
                color: {cores["texto"]};
                border: 1px solid {cores["destaque"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {cores["destaque"]};
            }}
            QTabBar::tab {{
                background-color: {cores["fundo"]};
                color: {cores["texto"]};
                padding: 5px;
                border: 1px solid {cores["destaque"]};
            }}
            QTabBar::tab:selected {{
                background-color: {cores["destaque"]};
            }}
            QMenuBar {{
                background-color: {cores["fundo"]};
                color: {cores["texto"]};
            }}
            QMenuBar::item:selected {{
                background-color: {cores["destaque"]};
            }}
            QMenu {{
                background-color: {cores["fundo"]};
                color: {cores["texto"]};
            }}
            QMenu::item:selected {{
                background-color: {cores["destaque"]};
            }}
        """)
        
    def atualizar_interface(self):
        """Atualiza a interface com as configurações atuais"""
        # Atualiza fonte e cores
        self.aplicar_tema()
        
        # Atualiza layout
        config_layout = self.assistente.config.obter_layout()
        for editor in self.arquivos_abertos.values():
            editor.setLineWrapMode(
                QPlainTextEdit.WidgetWidth if config_layout["quebrar_linha"] 
                else QPlainTextEdit.NoWrap
            )
            editor.setShowLineNumbers(config_layout["mostrar_numeros_linha"])
            editor.setHighlightCurrentLine(config_layout["destacar_linha_atual"])
            editor.setShowSpaces(config_layout["mostrar_espacos"])
            
    def atualizar_editores(self):
        """Atualiza as configurações dos editores"""
        config = self.assistente.config.obter_config_editor()
        for editor in self.arquivos_abertos.values():
            editor.setAutoIndentation(config["auto_indentacao"])
            editor.setAutoCompletion(config["auto_completar"])
            editor.setAutoCloseBrackets(config["auto_fechar_chaves"])
            editor.setAutoCloseTags(config["auto_fechar_tags"])
            editor.setSyntaxHighlighting(config["destacar_sintaxe"])
            
    def mudar_layout(self, opcao: str, valor: bool):
        """Muda uma configuração de layout"""
        self.assistente.config.definir_configuracao(
            f"preferencias.interface.layout.{opcao}",
            valor
        )
        
    def mudar_config_editor(self, opcao: str, valor: bool):
        """Muda uma configuração do editor"""
        self.assistente.config.definir_configuracao(
            f"preferencias.editor.{opcao}",
            valor
        )
        
    def restaurar_configuracoes(self):
        """Restaura todas as configurações para o padrão"""
        self.assistente.restaurar_configuracoes_padrao()
        
    def atualizar_sugestoes_personalizadas(self):
        """Atualiza o painel com sugestões personalizadas"""
        sugestoes = self.assistente.obter_sugestoes_personalizadas()
        if sugestoes:
            self.painel_sugestoes.atualizar_sugestoes({
                "Apps mais usados": sugestoes["apps"],
                "Sites frequentes": sugestoes["sites"]
            })
        
    def _linguagem_alterada(self, nova_linguagem: str):
        """Chamado quando a linguagem é alterada no combo box"""
        if self.editor_atual:
            self.editor_atual.definir_linguagem(nova_linguagem)
            
    def definir_linguagem(self, linguagem: str):
        """Define a linguagem atual"""
        self.combo_linguagem.setCurrentText(linguagem)
        if self.editor_atual:
            self.editor_atual.definir_linguagem(linguagem)
            
    def novo_arquivo(self):
        """Cria um novo arquivo"""
        linguagem = self.combo_linguagem.currentText()
        editor = EditorCodigo(linguagem=linguagem)
        nome = f"Novo arquivo.{self.config_linguagens['suportadas'][linguagem]['extensoes'][0]}"
        indice = self.tabs_arquivos.addTab(editor, nome)
        self.tabs_arquivos.setCurrentIndex(indice)
        self.editor_atual = editor
        
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo"""
        # Cria filtro baseado nas extensões suportadas
        filtros = []
        for ling, config in self.config_linguagens['suportadas'].items():
            exts = " ".join(f"*{ext}" for ext in config['extensoes'])
            filtros.append(f"Arquivos {ling.capitalize()} ({exts})")
        filtros.append("Todos os arquivos (*.*)")
        
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir arquivo",
            "",
            ";;".join(filtros)
        )
        if caminho:
            self.abrir_arquivo(caminho)
            
    def abrir_arquivo(self, caminho):
        """Abre um arquivo para edição"""
        if caminho not in self.arquivos_abertos:
            try:
                # Determina a linguagem pela extensão
                ext = Path(caminho).suffix
                linguagem = self.config_linguagens['associacoes_arquivo'].get(ext, 'python')
                
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    
                editor = EditorCodigo(linguagem=linguagem)
                editor.setPlainText(conteudo)
                
                nome_arquivo = os.path.basename(caminho)
                indice = self.tabs_arquivos.addTab(editor, nome_arquivo)
                self.tabs_arquivos.setCurrentIndex(indice)
                
                self.arquivos_abertos[caminho] = editor
                self.editor_atual = editor
                
                # Atualiza combo de linguagem
                self.combo_linguagem.setCurrentText(linguagem)
                
                # Inicia monitoramento
                diretorio = os.path.dirname(caminho)
                self.assistente.iniciar_monitoramento(diretorio)
                self.assistente.arquivos_abertos.add(caminho)
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir arquivo: {e}")
                
    def salvar_arquivo(self):
        """Salva o arquivo atual"""
        if not self.editor_atual:
            return
            
        indice = self.tabs_arquivos.currentIndex()
        caminho = next(
            (k for k, v in self.arquivos_abertos.items() if v == self.editor_atual),
            None
        )
        
        if not caminho:
            # Novo arquivo, precisa escolher local
            linguagem = self.combo_linguagem.currentText()
            ext = self.config_linguagens['suportadas'][linguagem]['extensoes'][0]
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar arquivo",
                f"novo_arquivo{ext}",
                f"Arquivos {linguagem.capitalize()} (*{ext})"
            )
            if not caminho:
                return
                
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(self.editor_atual.toPlainText())
            
            # Atualiza tab se for novo arquivo
            if caminho not in self.arquivos_abertos:
                self.arquivos_abertos[caminho] = self.editor_atual
                self.tabs_arquivos.setTabText(indice, os.path.basename(caminho))
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo: {e}")
        
    def fechar_arquivo(self, indice):
        """Fecha um arquivo aberto"""
        editor = self.tabs_arquivos.widget(indice)
        for caminho, ed in self.arquivos_abertos.items():
            if ed == editor:
                self.arquivos_abertos.pop(caminho)
                self.assistente.arquivos_abertos.remove(caminho)
                break
                
        self.tabs_arquivos.removeTab(indice)
        editor.deleteLater()
        
    def closeEvent(self, evento):
        """Evento chamado ao fechar a janela"""
        self.assistente.finalizar()
        evento.accept() 