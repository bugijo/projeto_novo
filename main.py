import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QDockWidget, QVBoxLayout, QWidget, QMenuBar, QMenu, QFileDialog
from PyQt6.QtCore import Qt
from pathlib import Path
from ide_config import IDE_CONFIG
from editor import CodeEditor
from file_explorer import FileExplorer
from terminal import Terminal

class EditorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.editor = CodeEditor()
        self.layout.addWidget(self.editor)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.file_path = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(IDE_CONFIG["name"])
        self.resize(1200, 800)
        
        # Editor principal com abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Adicionar primeira aba
        self.new_tab()
        
        # Explorador de arquivos
        self.file_explorer = QDockWidget("Explorador", self)
        self.file_tree = FileExplorer(self)
        self.file_explorer.setWidget(self.file_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_explorer)
        
        # Terminal integrado
        self.terminal = QDockWidget("Terminal", self)
        self.terminal_widget = Terminal(self)
        self.terminal.setWidget(self.terminal_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal)
        
        self.setup_menu()
        
    def new_tab(self, file_path=None):
        tab = EditorTab()
        name = Path(file_path).name if file_path else "Novo arquivo"
        index = self.tabs.addTab(tab, name)
        tab.file_path = file_path
        self.tabs.setCurrentIndex(index)
        return tab
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        new_action = file_menu.addAction("Novo")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_tab)
        
        open_action = file_menu.addAction("Abrir")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        
        save_action = file_menu.addAction("Salvar")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        
        save_as_action = file_menu.addAction("Salvar como")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Sair")
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        
        # Menu Editar
        edit_menu = menubar.addMenu("Editar")
        
        undo_action = edit_menu.addAction("Desfazer")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.current_editor().undo())
        
        redo_action = edit_menu.addAction("Refazer")
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.current_editor().redo())
        
        edit_menu.addSeparator()
        
        cut_action = edit_menu.addAction("Recortar")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: self.current_editor().cut())
        
        copy_action = edit_menu.addAction("Copiar")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.current_editor().copy())
        
        paste_action = edit_menu.addAction("Colar")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.current_editor().paste())
        
        # Menu Ver
        view_menu = menubar.addMenu("Ver")
        
        toggle_explorer = view_menu.addAction("Explorador")
        toggle_explorer.setCheckable(True)
        toggle_explorer.setChecked(True)
        toggle_explorer.triggered.connect(lambda checked: self.file_explorer.setVisible(checked))
        
        toggle_terminal = view_menu.addAction("Terminal")
        toggle_terminal.setCheckable(True)
        toggle_terminal.setChecked(True)
        toggle_terminal.triggered.connect(lambda checked: self.terminal.setVisible(checked))
        
        # Menu Ferramentas
        tools_menu = menubar.addMenu("Ferramentas")
        
        run_action = tools_menu.addAction("Executar")
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        
        debug_action = tools_menu.addAction("Debug")
        debug_action.setShortcut("F9")
        # TODO: Implementar debug

    def current_editor(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            return current_tab.editor
        return None

    def open_file(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Abrir arquivo", str(Path.home()),
                "Todos os arquivos (*.*)"
            )
        if file_path:
            # Verificar se o arquivo já está aberto
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if tab.file_path == file_path:
                    self.tabs.setCurrentIndex(i)
                    return
            
            # Criar nova aba
            tab = self.new_tab(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                tab.editor.setPlainText(f.read())

    def save_file(self):
        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return
        
        if not current_tab.file_path:
            return self.save_file_as()
        
        with open(current_tab.file_path, 'w', encoding='utf-8') as f:
            f.write(current_tab.editor.toPlainText())

    def save_file_as(self):
        current_tab = self.tabs.currentWidget()
        if not current_tab:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar como", str(Path.home()),
            "Todos os arquivos (*.*)"
        )
        if file_path:
            current_tab.file_path = file_path
            self.tabs.setTabText(self.tabs.currentIndex(), Path(file_path).name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(current_tab.editor.toPlainText())

    def close_tab(self, index):
        # TODO: Verificar se há alterações não salvas
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()

    def update_tab_path(self, old_path, new_path):
        """Atualiza o caminho do arquivo em uma aba após renomear"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.file_path == old_path:
                tab.file_path = new_path
                self.tabs.setTabText(i, Path(new_path).name)
                break

    def close_tab_by_path(self, path):
        """Fecha uma aba pelo caminho do arquivo"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.file_path == path:
                self.close_tab(i)
                break

    def run_current_file(self):
        """Executa o arquivo atual"""
        current_tab = self.tabs.currentWidget()
        if not current_tab or not current_tab.file_path:
            return
        
        # Salvar arquivo antes de executar
        self.save_file()
        
        # Executar no terminal
        file_path = current_tab.file_path
        if file_path.endswith('.py'):
            self.terminal_widget.execute_command(f"python {file_path}")
        elif file_path.endswith('.js'):
            self.terminal_widget.execute_command(f"node {file_path}")
        # TODO: Adicionar suporte para outras linguagens

def setup_environment():
    """Configura o ambiente necessário para o IDE"""
    for dir_path in [
        IDE_CONFIG["workspace_dir"],
        IDE_CONFIG["temp_dir"],
        IDE_CONFIG["cache_dir"],
        IDE_CONFIG["log_dir"]
    ]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def main():
    """Função principal que inicia o IDE"""
    setup_environment()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    import os
    os.environ['IDE_PORT'] = '5001'
    main() 