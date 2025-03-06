from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QTreeView, QTextEdit,
    QDockWidget, QToolBar, QStatusBar, QFileSystemModel
)
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QIcon
import sys
from pathlib import Path
from ide_config import *
from extension_window import ExtensionWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(IDE_CONFIG["name"])
        self.setup_ui()
        
    def setup_ui(self):
        # Configurar a janela principal
        self.resize(1200, 800)
        
        # Criar barra de ferramentas
        self.setup_toolbar()
        
        # Criar widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Criar splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Configurar explorador de arquivos
        self.setup_file_explorer(main_splitter)
        
        # Configurar área principal
        self.setup_main_area(main_splitter)
        
        # Configurar terminal e output
        self.setup_bottom_area()
        
        # Configurar assistente IA
        self.setup_ai_assistant()
        
        # Configurar barra de status
        self.setup_status_bar()
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Adicionar ações
        new_action = QAction("Novo", self)
        new_action.setShortcut(SHORTCUTS["new_file"])
        toolbar.addAction(new_action)
        
        open_action = QAction("Abrir", self)
        open_action.setShortcut(SHORTCUTS["open_file"])
        toolbar.addAction(open_action)
        
        save_action = QAction("Salvar", self)
        save_action.setShortcut(SHORTCUTS["save_file"])
        toolbar.addAction(save_action)
        
        run_action = QAction("Executar", self)
        run_action.setShortcut(SHORTCUTS["run_code"])
        toolbar.addAction(run_action)
        
        debug_action = QAction("Debug", self)
        debug_action.setShortcut(SHORTCUTS["debug"])
        toolbar.addAction(debug_action)
        
        # Adicionar separador
        toolbar.addSeparator()
        
        # Adicionar botão de extensões
        extensions_action = QAction("Extensões", self)
        extensions_action.triggered.connect(self.show_extensions)
        toolbar.addAction(extensions_action)
        
    def setup_file_explorer(self, parent):
        # Criar dock widget para o explorador
        file_dock = QDockWidget("Explorador", self)
        file_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                 Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Criar tree view para arquivos
        file_view = QTreeView()
        model = QFileSystemModel()
        model.setRootPath(QDir.currentPath())
        file_view.setModel(model)
        file_view.setRootIndex(model.index(QDir.currentPath()))
        
        file_dock.setWidget(file_view)
        parent.addWidget(file_dock)
        
    def setup_main_area(self, parent):
        # Criar widget de abas para editores
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # Adicionar editor padrão
        editor = QTextEdit()
        editor.setFontFamily(EDITOR_CONFIG["font_family"])
        editor.setFontPointSize(EDITOR_CONFIG["font_size"])
        self.tab_widget.addTab(editor, "Sem título")
        
        parent.addWidget(self.tab_widget)
        
    def setup_bottom_area(self):
        # Criar dock widget para terminal e output
        bottom_dock = QDockWidget("Terminal", self)
        bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        
        # Criar terminal
        terminal = QTextEdit()
        terminal.setFontFamily(TERMINAL_CONFIG["font_family"])
        terminal.setFontPointSize(TERMINAL_CONFIG["font_size"])
        terminal.setReadOnly(True)
        
        bottom_dock.setWidget(terminal)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)
        
    def setup_ai_assistant(self):
        # Criar dock widget para assistente IA
        ai_dock = QDockWidget("Assistente IA", self)
        ai_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Criar widget do assistente
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        
        # Área de chat
        chat_area = QTextEdit()
        chat_area.setReadOnly(True)
        ai_layout.addWidget(chat_area)
        
        # Campo de entrada
        input_field = QTextEdit()
        input_field.setMaximumHeight(100)
        ai_layout.addWidget(input_field)
        
        ai_dock.setWidget(ai_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, ai_dock)
        
    def setup_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Pronto")
        
    def show_extensions(self):
        """Abre a janela do gerenciador de extensões"""
        extension_window = ExtensionWindow(self)
        extension_window.exec() 