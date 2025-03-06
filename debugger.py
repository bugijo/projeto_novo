import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging
import json
from PyQt6.QtCore import QObject, pyqtSignal
import debugpy

@dataclass
class Breakpoint:
    file: str
    line: int
    condition: Optional[str] = None
    hit_count: int = 0
    enabled: bool = True

class Debugger(QObject):
    # Sinais
    breakpoint_hit = pyqtSignal(str, int, dict)  # arquivo, linha, variáveis
    debug_output = pyqtSignal(str)  # mensagem de saída
    debug_error = pyqtSignal(str)   # mensagem de erro
    debug_stopped = pyqtSignal()    # quando o debug termina
    variable_updated = pyqtSignal(str, Any)  # nome da variável, novo valor

    def __init__(self):
        super().__init__()
        self.breakpoints: Dict[str, List[Breakpoint]] = {}
        self.current_frame = None
        self.is_running = False
        self.debug_port = 5678

    def start_debugging(self, file_path: str):
        """Inicia a sessão de debug"""
        try:
            # Configurar debugpy
            debugpy.configure(python=sys.executable)
            debugpy.listen(("localhost", self.debug_port))
            
            # Adicionar breakpoints existentes
            for file, bps in self.breakpoints.items():
                for bp in bps:
                    if bp.enabled:
                        debugpy.breakpoint(file, bp.line, condition=bp.condition)
            
            # Iniciar programa
            self.is_running = True
            debugpy.launch(file_path)
            
        except Exception as e:
            self.debug_error.emit(f"Erro ao iniciar debug: {str(e)}")
            self.is_running = False

    def stop_debugging(self):
        """Para a sessão de debug"""
        try:
            if self.is_running:
                debugpy.stop()
                self.is_running = False
                self.debug_stopped.emit()
        except Exception as e:
            self.debug_error.emit(f"Erro ao parar debug: {str(e)}")

    def add_breakpoint(self, file: str, line: int, condition: Optional[str] = None):
        """Adiciona um breakpoint"""
        try:
            bp = Breakpoint(file=file, line=line, condition=condition)
            
            if file not in self.breakpoints:
                self.breakpoints[file] = []
            
            self.breakpoints[file].append(bp)
            
            if self.is_running:
                debugpy.breakpoint(file, line, condition=condition)
                
            return True
        except Exception as e:
            self.debug_error.emit(f"Erro ao adicionar breakpoint: {str(e)}")
            return False

    def remove_breakpoint(self, file: str, line: int):
        """Remove um breakpoint"""
        try:
            if file in self.breakpoints:
                self.breakpoints[file] = [bp for bp in self.breakpoints[file] if bp.line != line]
                
                if self.is_running:
                    debugpy.clear_breakpoint(file, line)
                
            return True
        except Exception as e:
            self.debug_error.emit(f"Erro ao remover breakpoint: {str(e)}")
            return False

    def toggle_breakpoint(self, file: str, line: int):
        """Ativa/desativa um breakpoint"""
        try:
            if file in self.breakpoints:
                for bp in self.breakpoints[file]:
                    if bp.line == line:
                        bp.enabled = not bp.enabled
                        
                        if self.is_running:
                            if bp.enabled:
                                debugpy.breakpoint(file, line, condition=bp.condition)
                            else:
                                debugpy.clear_breakpoint(file, line)
                        
                        return True
            return False
        except Exception as e:
            self.debug_error.emit(f"Erro ao alternar breakpoint: {str(e)}")
            return False

    def step_over(self):
        """Avança uma linha"""
        try:
            if self.is_running:
                debugpy.step_over()
        except Exception as e:
            self.debug_error.emit(f"Erro ao avançar linha: {str(e)}")

    def step_into(self):
        """Entra na função"""
        try:
            if self.is_running:
                debugpy.step_into()
        except Exception as e:
            self.debug_error.emit(f"Erro ao entrar na função: {str(e)}")

    def step_out(self):
        """Sai da função"""
        try:
            if self.is_running:
                debugpy.step_out()
        except Exception as e:
            self.debug_error.emit(f"Erro ao sair da função: {str(e)}")

    def continue_execution(self):
        """Continua a execução"""
        try:
            if self.is_running:
                debugpy.continue_execution()
        except Exception as e:
            self.debug_error.emit(f"Erro ao continuar execução: {str(e)}")

    def get_variable_value(self, name: str) -> Optional[Any]:
        """Obtém o valor de uma variável"""
        try:
            if self.current_frame:
                return self.current_frame.f_locals.get(name)
            return None
        except Exception as e:
            self.debug_error.emit(f"Erro ao obter valor da variável: {str(e)}")
            return None

    def get_call_stack(self) -> List[Dict]:
        """Obtém a pilha de chamadas"""
        try:
            if not self.current_frame:
                return []
            
            stack = []
            frame = self.current_frame
            
            while frame:
                stack.append({
                    'file': frame.f_code.co_filename,
                    'function': frame.f_code.co_name,
                    'line': frame.f_lineno,
                    'locals': {k: str(v) for k, v in frame.f_locals.items()}
                })
                frame = frame.f_back
            
            return stack
        except Exception as e:
            self.debug_error.emit(f"Erro ao obter pilha de chamadas: {str(e)}")
            return []

    def evaluate_expression(self, expression: str) -> Optional[Any]:
        """Avalia uma expressão no contexto atual"""
        try:
            if self.current_frame:
                return eval(expression, self.current_frame.f_globals, self.current_frame.f_locals)
            return None
        except Exception as e:
            self.debug_error.emit(f"Erro ao avaliar expressão: {str(e)}")
            return None

    def save_breakpoints(self, file_path: str):
        """Salva os breakpoints em um arquivo"""
        try:
            data = {
                file: [{
                    'line': bp.line,
                    'condition': bp.condition,
                    'enabled': bp.enabled
                } for bp in bps]
                for file, bps in self.breakpoints.items()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            return True
        except Exception as e:
            self.debug_error.emit(f"Erro ao salvar breakpoints: {str(e)}")
            return False

    def load_breakpoints(self, file_path: str):
        """Carrega breakpoints de um arquivo"""
        try:
            if not Path(file_path).exists():
                return False
                
            with open(file_path) as f:
                data = json.load(f)
                
            self.breakpoints.clear()
            
            for file, bps in data.items():
                self.breakpoints[file] = [
                    Breakpoint(
                        file=file,
                        line=bp['line'],
                        condition=bp.get('condition'),
                        enabled=bp.get('enabled', True)
                    )
                    for bp in bps
                ]
                
            return True
        except Exception as e:
            self.debug_error.emit(f"Erro ao carregar breakpoints: {str(e)}")
            return False 