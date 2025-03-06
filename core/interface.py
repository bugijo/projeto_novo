from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QComboBox, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QPixmap
import sys
import json
from pathlib import Path
from typing import Optional

class InterfaceGrafica(QMainWindow):
    comando_enviado = pyqtSignal(str)

    def __init__(self, assistente):
        super().__init__()
        self.assistente = assistente
        self.inicializar_ui()
        self.carregar_configuracoes()
        self.criar_tray_icon()

    def inicializar_ui(self):
        """Inicializa a interface gráfica"""
        self.setWindowTitle(f"Assistente Virtual - {self.assistente.config.nome}")
        self.setGeometry(100, 100, 800, 600)

        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)

        # Área do avatar
        self.area_avatar = QLabel()
        self.atualizar_avatar()
        layout_principal.addWidget(self.area_avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Área de histórico
        self.historico = QTextEdit()
        self.historico.setReadOnly(True)
        layout_principal.addWidget(self.historico)

        # Área de entrada de comando
        layout_comando = QHBoxLayout()
        self.entrada_comando = QTextEdit()
        self.entrada_comando.setMaximumHeight(50)
        layout_comando.addWidget(self.entrada_comando)

        botao_enviar = QPushButton("Enviar")
        botao_enviar.clicked.connect(self.enviar_comando)
        layout_comando.addWidget(botao_enviar)

        layout_principal.addLayout(layout_comando)

        # Barra de status
        self.statusBar().showMessage("Pronto")

        # Menu de configurações
        self.criar_menu()

    def criar_menu(self):
        """Cria o menu da aplicação"""
        menu_bar = self.menuBar()
        
        # Menu Configurações
        menu_config = menu_bar.addMenu("Configurações")
        
        # Submenu Aparência
        submenu_aparencia = menu_config.addMenu("Aparência")
        
        # Opções de tema
        acao_tema_claro = submenu_aparencia.addAction("Tema Claro")
        acao_tema_claro.triggered.connect(lambda: self.mudar_tema("light"))
        
        acao_tema_escuro = submenu_aparencia.addAction("Tema Escuro")
        acao_tema_escuro.triggered.connect(lambda: self.mudar_tema("dark"))

        # Submenu Avatar
        submenu_avatar = menu_config.addMenu("Avatar")
        for avatar in self.listar_avatares():
            acao = submenu_avatar.addAction(avatar)
            acao.triggered.connect(lambda checked, a=avatar: self.mudar_avatar(a))

        # Submenu Voz
        submenu_voz = menu_config.addMenu("Voz")
        for voz in self.listar_vozes():
            acao = submenu_voz.addAction(voz)
            acao.triggered.connect(lambda checked, v=voz: self.mudar_voz(v))

    def criar_tray_icon(self):
        """Cria o ícone na bandeja do sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icon.png"))
        
        # Menu do tray icon
        tray_menu = QMenu()
        
        mostrar_acao = tray_menu.addAction("Mostrar")
        mostrar_acao.triggered.connect(self.show)
        
        ocultar_acao = tray_menu.addAction("Ocultar")
        ocultar_acao.triggered.connect(self.hide)
        
        sair_acao = tray_menu.addAction("Sair")
        sair_acao.triggered.connect(self.fechar_aplicacao)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def carregar_configuracoes(self):
        """Carrega as configurações da interface"""
        config_path = Path("config/interface.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.aplicar_configuracoes(config)

    def aplicar_configuracoes(self, config):
        """Aplica as configurações carregadas"""
        if "tema" in config:
            self.mudar_tema(config["tema"])
        if "avatar" in config:
            self.mudar_avatar(config["avatar"])

    def atualizar_historico(self, texto: str):
        """Atualiza o histórico de conversas"""
        self.historico.append(texto)

    def atualizar_status(self, mensagem: str):
        """Atualiza a mensagem de status"""
        self.statusBar().showMessage(mensagem)

    def enviar_comando(self):
        """Envia o comando digitado para processamento"""
        comando = self.entrada_comando.toPlainText().strip()
        if comando:
            self.entrada_comando.clear()
            self.atualizar_historico(f"Você: {comando}")
            self.comando_enviado.emit(comando)

    def atualizar_avatar(self):
        """Atualiza o avatar do assistente"""
        avatar_path = Path(f"assets/avatars/{self.assistente.config.avatar}.png")
        if avatar_path.exists():
            pixmap = QPixmap(str(avatar_path))
            self.area_avatar.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def mudar_tema(self, tema: str):
        """Muda o tema da interface"""
        if tema == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QTextEdit { background-color: #3b3b3b; color: #ffffff; }
                QPushButton { background-color: #4b4b4b; color: #ffffff; }
                QLabel { color: #ffffff; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #ffffff; }
                QTextEdit { background-color: #f0f0f0; color: #000000; }
                QPushButton { background-color: #e0e0e0; color: #000000; }
                QLabel { color: #000000; }
            """)
        self.assistente.config.tema_interface = tema

    def mudar_avatar(self, avatar: str):
        """Muda o avatar do assistente"""
        self.assistente.config.avatar = avatar
        self.atualizar_avatar()

    def mudar_voz(self, voz_id: str):
        """Muda a voz do assistente"""
        self.assistente.config.voz_id = voz_id
        self.assistente.configurar_voz()

    def listar_avatares(self):
        """Lista os avatares disponíveis"""
        pasta_avatares = Path("assets/avatars")
        if not pasta_avatares.exists():
            return ["default"]
        return [f.stem for f in pasta_avatares.glob("*.png")]

    def listar_vozes(self):
        """Lista as vozes disponíveis"""
        return [voice.id for voice in self.assistente.engine.getProperty('voices')]

    def fechar_aplicacao(self):
        """Fecha a aplicação"""
        self.assistente.executando = False
        QApplication.quit()

    def closeEvent(self, event):
        """Trata o evento de fechar a janela"""
        event.ignore()
        self.hide()

    def iniciar(self):
        """Inicia a interface gráfica"""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        self.show()
        QApplication.instance().exec() 