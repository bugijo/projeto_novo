from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QProcess, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor, QPalette
import os
import sys
from pathlib import Path

class Terminal(QWidget):
    command_executed = pyqtSignal(str, str)  # comando, saída

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de texto
        self.output = QTextEdit()
        self.output.setReadOnly(False)
        self.layout.addWidget(self.output)
        
        # Configurar fonte e cores
        self.setup_appearance()
        
        # Processo
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        
        # Histórico de comandos
        self.history = []
        self.history_index = 0
        
        # Diretório atual
        self.current_dir = str(Path.home())
        
        # Iniciar shell
        self.start_shell()
        
        # Conectar eventos
        self.output.textChanged.connect(self.handle_text_changed)
        self.output.keyPressEvent = self.handle_key_press
        
    def setup_appearance(self):
        """Configura a aparência do terminal"""
        # Fonte
        font = self.output.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.output.setFont(font)
        
        # Cores
        palette = self.output.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        self.output.setPalette(palette)
        
        # Cursor
        self.output.setTextCursor(QTextCursor(self.output.document()))
        
    def start_shell(self):
        """Inicia o shell apropriado para o sistema"""
        if sys.platform == "win32":
            shell = "powershell.exe"
            args = []
        else:
            shell = os.environ.get("SHELL", "/bin/bash")
            args = ["-i"]
        
        self.process.setWorkingDirectory(self.current_dir)
        self.process.start(shell, args)
        
        # Mostrar prompt inicial
        self.write_prompt()
        
    def write_prompt(self):
        """Escreve o prompt do terminal"""
        self.output.insertPlainText(f"{self.current_dir}> ")
        
    def handle_stdout(self):
        """Processa a saída padrão"""
        data = self.process.readAllStandardOutput().data().decode()
        self.output.insertPlainText(data)
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        
    def handle_stderr(self):
        """Processa a saída de erro"""
        data = self.process.readAllStandardError().data().decode()
        cursor = self.output.textCursor()
        format = cursor.charFormat()
        format.setForeground(QColor("#ff0000"))
        cursor.setCharFormat(format)
        cursor.insertText(data)
        format.setForeground(QColor("#d4d4d4"))
        cursor.setCharFormat(format)
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        
    def handle_finished(self, exit_code, exit_status):
        """Processa o término do comando"""
        if exit_code != 0:
            self.output.insertPlainText(f"\nProcesso terminou com código {exit_code}")
        self.write_prompt()
        
    def handle_text_changed(self):
        """Processa mudanças no texto"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)
        
    def handle_key_press(self, event):
        """Processa teclas pressionadas"""
        cursor = self.output.textCursor()
        
        # Enter: executa comando
        if event.key() == Qt.Key.Key_Return:
            command = self.get_current_command()
            if command:
                self.execute_command(command)
                self.history.append(command)
                self.history_index = len(self.history)
            return
        
        # Seta para cima: histórico anterior
        elif event.key() == Qt.Key.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.set_current_command(self.history[self.history_index])
            return
        
        # Seta para baixo: histórico posterior
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.set_current_command(self.history[self.history_index])
            else:
                self.history_index = len(self.history)
                self.set_current_command("")
            return
        
        # Tab: auto-completar
        elif event.key() == Qt.Key.Key_Tab:
            self.auto_complete()
            return
        
        # Ctrl+C: interromper
        elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.process.kill()
            self.output.insertPlainText("^C\n")
            self.write_prompt()
            return
        
        # Outras teclas: processar normalmente
        QTextEdit.keyPressEvent(self.output, event)
        
    def get_current_command(self):
        """Obtém o comando atual"""
        text = self.output.toPlainText()
        if ">" in text:
            return text.split(">")[-1].strip()
        return ""
        
    def set_current_command(self, command):
        """Define o comando atual"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Apagar comando atual
        current = self.get_current_command()
        for _ in range(len(current)):
            cursor.deletePreviousChar()
            
        # Inserir novo comando
        cursor.insertText(command)
        
    def execute_command(self, command):
        """Executa um comando"""
        self.output.insertPlainText("\n")
        
        # Comandos internos
        if command == "clear":
            self.output.clear()
            self.write_prompt()
            return
        elif command.startswith("cd "):
            path = command[3:].strip()
            path = os.path.expanduser(path)
            if os.path.isdir(path):
                self.current_dir = path
                self.process.setWorkingDirectory(path)
                self.write_prompt()
            else:
                self.output.insertPlainText(f"Diretório não encontrado: {path}\n")
                self.write_prompt()
            return
        
        # Outros comandos
        self.process.write(f"{command}\n".encode())
        
    def auto_complete(self):
        """Auto-completa comandos e caminhos"""
        command = self.get_current_command()
        if not command:
            return
            
        # Completar caminhos
        if " " in command:
            prefix = command.split()[-1]
            if os.path.isdir(os.path.dirname(prefix)):
                matches = []
                for item in os.listdir(os.path.dirname(prefix) or "."):
                    if item.startswith(os.path.basename(prefix)):
                        matches.append(item)
                
                if len(matches) == 1:
                    self.set_current_command(
                        command[:-len(os.path.basename(prefix))] + matches[0]
                    )
                elif len(matches) > 1:
                    self.output.insertPlainText("\n" + " ".join(matches) + "\n")
                    self.write_prompt()
                    self.set_current_command(command)
        
        # Completar comandos
        else:
            # TODO: Implementar auto-complete de comandos 