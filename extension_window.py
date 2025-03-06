from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from extension_manager import ExtensionManager, Extension
from typing import List, Optional

class ExtensionWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, manager: ExtensionManager, action: str, extension_id: str):
        super().__init__()
        self.manager = manager
        self.action = action
        self.extension_id = extension_id
    
    def run(self):
        try:
            result = False
            if self.action == "install":
                result = self.manager.install_extension(self.extension_id)
            elif self.action == "uninstall":
                result = self.manager.uninstall_extension(self.extension_id)
            elif self.action == "update":
                result = self.manager.update_extension(self.extension_id)
            elif self.action == "enable":
                result = self.manager.enable_extension(self.extension_id)
            elif self.action == "disable":
                result = self.manager.disable_extension(self.extension_id)
            
            self.finished.emit(result, self.extension_id)
        except Exception as e:
            self.finished.emit(False, str(e))

class ExtensionItem(QListWidgetItem):
    def __init__(self, extension: Extension):
        super().__init__()
        self.extension = extension
        self.update_text()
    
    def update_text(self):
        status = "✓" if self.extension.installed else " "
        enabled = "(Ativo)" if self.extension.enabled else "(Inativo)"
        self.setText(f"{status} {self.extension.name} v{self.extension.version} {enabled}\n"
                    f"   {self.extension.description}")

class ExtensionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ExtensionManager()
        self.setup_ui()
        self.load_extensions()
    
    def setup_ui(self):
        self.setWindowTitle("Gerenciador de Extensões")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Barra de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar extensões...")
        self.search_input.textChanged.connect(self.filter_extensions)
        search_layout.addWidget(self.search_input)
        
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.load_extensions)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Abas
        self.tab_widget = QTabWidget()
        
        # Aba de extensões disponíveis
        available_tab = QWidget()
        available_layout = QVBoxLayout(available_tab)
        self.available_list = QListWidget()
        self.available_list.itemClicked.connect(self.show_extension_details)
        available_layout.addWidget(self.available_list)
        
        # Aba de extensões instaladas
        installed_tab = QWidget()
        installed_layout = QVBoxLayout(installed_tab)
        self.installed_list = QListWidget()
        self.installed_list.itemClicked.connect(self.show_extension_details)
        installed_layout.addWidget(self.installed_list)
        
        # Aba de recomendados
        recommended_tab = QWidget()
        recommended_layout = QVBoxLayout(recommended_tab)
        self.recommended_list = QListWidget()
        self.recommended_list.itemClicked.connect(self.show_extension_details)
        recommended_layout.addWidget(self.recommended_list)
        
        self.tab_widget.addTab(available_tab, "Disponíveis")
        self.tab_widget.addTab(installed_tab, "Instalados")
        self.tab_widget.addTab(recommended_tab, "Recomendados")
        
        layout.addWidget(self.tab_widget)
        
        # Área de detalhes
        details_layout = QVBoxLayout()
        
        self.details_label = QLabel()
        self.details_label.setWordWrap(True)
        details_layout.addWidget(self.details_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        details_layout.addWidget(self.progress_bar)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.install_button = QPushButton("Instalar")
        self.install_button.clicked.connect(self.install_extension)
        button_layout.addWidget(self.install_button)
        
        self.uninstall_button = QPushButton("Desinstalar")
        self.uninstall_button.clicked.connect(self.uninstall_extension)
        button_layout.addWidget(self.uninstall_button)
        
        self.enable_button = QPushButton("Ativar")
        self.enable_button.clicked.connect(self.enable_extension)
        button_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton("Desativar")
        self.disable_button.clicked.connect(self.disable_extension)
        button_layout.addWidget(self.disable_button)
        
        details_layout.addLayout(button_layout)
        layout.addLayout(details_layout)
        
        self.current_extension: Optional[Extension] = None
        self.update_buttons()
    
    def load_extensions(self):
        """Carrega todas as extensões"""
        # Limpar listas
        self.available_list.clear()
        self.installed_list.clear()
        self.recommended_list.clear()
        
        # Carregar extensões disponíveis
        available = self.manager.fetch_available_extensions()
        for ext in available.values():
            item = ExtensionItem(ext)
            self.available_list.addItem(item)
        
        # Carregar extensões instaladas
        for ext in self.manager.installed_extensions.values():
            item = ExtensionItem(ext)
            self.installed_list.addItem(item)
        
        # Carregar recomendações
        recommended = self.manager.get_recommended_extensions()
        for ext in recommended:
            item = ExtensionItem(ext)
            self.recommended_list.addItem(item)
    
    def filter_extensions(self, text: str):
        """Filtra as extensões baseado na pesquisa"""
        results = self.manager.search_extensions(text)
        
        self.available_list.clear()
        for ext in results:
            item = ExtensionItem(ext)
            self.available_list.addItem(item)
    
    def show_extension_details(self, item: ExtensionItem):
        """Mostra os detalhes da extensão selecionada"""
        self.current_extension = item.extension
        
        details = f"""
        <h2>{item.extension.name} v{item.extension.version}</h2>
        <p><b>Autor:</b> {item.extension.author}</p>
        <p><b>Descrição:</b> {item.extension.description}</p>
        <p><b>Tags:</b> {', '.join(item.extension.tags)}</p>
        <p><b>Dependências:</b> {', '.join(item.extension.dependencies)}</p>
        <p><b>Repositório:</b> <a href="{item.extension.repository}">{item.extension.repository}</a></p>
        """
        
        self.details_label.setText(details)
        self.update_buttons()
    
    def update_buttons(self):
        """Atualiza o estado dos botões baseado na extensão selecionada"""
        if self.current_extension:
            is_installed = self.current_extension.installed
            is_enabled = self.current_extension.enabled
            
            self.install_button.setEnabled(not is_installed)
            self.uninstall_button.setEnabled(is_installed)
            self.enable_button.setEnabled(is_installed and not is_enabled)
            self.disable_button.setEnabled(is_installed and is_enabled)
        else:
            self.install_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
            self.enable_button.setEnabled(False)
            self.disable_button.setEnabled(False)
    
    def start_operation(self, action: str):
        """Inicia uma operação em uma extensão"""
        if not self.current_extension:
            return
        
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        
        worker = ExtensionWorker(self.manager, action, self.current_extension.id)
        worker.finished.connect(self.operation_finished)
        worker.start()
    
    def operation_finished(self, success: bool, message: str):
        """Callback quando uma operação termina"""
        self.progress_bar.hide()
        
        if success:
            self.load_extensions()
            QMessageBox.information(self, "Sucesso", "Operação concluída com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", f"Erro na operação: {message}")
    
    def install_extension(self):
        self.start_operation("install")
    
    def uninstall_extension(self):
        self.start_operation("uninstall")
    
    def enable_extension(self):
        self.start_operation("enable")
    
    def disable_extension(self):
        self.start_operation("disable") 