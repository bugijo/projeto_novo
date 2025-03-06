import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

from config.system_config import (
    AI_CONFIG,
    COMFYUI_CONFIG,
    WORKFLOW_CONFIG,
    SECURITY_CONFIG,
    LOG_CONFIG
)

from transformers import pipeline

class SystemManager:
    """Gerenciador principal do sistema."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.comfy_manager = None
        self.workflow_manager = None
        self.task_analyzer = None
        self.running = False
        self.tasks = {}
        self.model = None
        self.is_running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Configura o sistema de logging."""
        logger = logging.getLogger('SystemManager')
        logger.setLevel(LOG_CONFIG['level'])
        
        formatter = logging.Formatter(LOG_CONFIG['format'])
        
        file_handler = logging.FileHandler(LOG_CONFIG['file'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    async def start(self):
        """Inicia o sistema."""
        try:
            self.logger.info("Iniciando sistema...")
            self.running = True
            
            # Inicia ComfyUI em background
            await self._start_comfy_ui()
            
            # Inicializa gerenciadores
            await self._initialize_managers()
            
            # Inicializa o modelo usando pipeline
            self.model = pipeline('text-generation', model='gpt2-medium')
            self.is_running = True
            
            self.logger.info("Sistema iniciado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sistema: {str(e)}")
            return False
    
    async def _start_comfy_ui(self):
        """Inicia o ComfyUI em background."""
        try:
            from comfy_manager import ComfyUIManager
            self.comfy_manager = ComfyUIManager()
            success = await self.comfy_manager.start_async()
            
            if not success:
                raise Exception("Falha ao iniciar ComfyUI")
                
        except Exception as e:
            self.logger.error(f"Erro ao iniciar ComfyUI: {str(e)}")
            raise
    
    async def _initialize_managers(self):
        """Inicializa os gerenciadores do sistema."""
        from workflow_manager import WorkflowManager
        from task_analyzer import TaskAnalyzer
        
        self.workflow_manager = WorkflowManager(self.comfy_manager)
        self.task_analyzer = TaskAnalyzer()
    
    async def process_request(self, message: str, user_id: str = "admin") -> Dict:
        """Processa uma requisição do usuário."""
        try:
            if not self.is_running:
                return {"error": "Sistema não iniciado"}
            
            # Simula uma resposta para teste
            response = f"Resposta do sistema para: {message}"
            
            return {"message": response, "status": "success"}
            
        except Exception as e:
            print(f"Erro ao processar requisição: {str(e)}")
            return {"error": "Erro ao processar requisição"}
    
    async def get_task_status(self, task_id: str) -> Dict:
        """Retorna o status de uma tarefa."""
        try:
            if task_id not in self.tasks:
                return {'error': 'Tarefa não encontrada'}
            
            status = await self.workflow_manager.get_workflow_status(task_id)
            return {
                'status': status,
                'workflow': self.tasks[task_id]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status da tarefa: {str(e)}")
            return {'error': str(e)}
    
    def _check_auth(self, user_id: str) -> bool:
        """Verifica se o usuário está autorizado."""
        return user_id in SECURITY_CONFIG['allowed_users']
    
    async def stop(self):
        """Para o sistema."""
        try:
            self.logger.info("Parando sistema...")
            self.running = False
            
            # Para workflows em execução
            if self.workflow_manager:
                await self.workflow_manager.stop_all()
            
            # Para ComfyUI
            if self.comfy_manager:
                await self.comfy_manager.stop()
            
            self.is_running = False
            self.logger.info("Sistema parado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar sistema: {str(e)}")
            return False
    
    async def optimize(self):
        """Executa otimizações do sistema."""
        try:
            self.logger.info("Iniciando otimização do sistema...")
            
            # Limpa cache antigo
            await self._clean_cache()
            
            # Analisa métricas
            metrics = await self._analyze_metrics()
            
            # Gera sugestões de otimização
            suggestions = await self._generate_optimization_suggestions(metrics)
            
            return {
                'metrics': metrics,
                'suggestions': suggestions
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante otimização: {str(e)}")
            return {'error': str(e)}
    
    async def _clean_cache(self):
        """Limpa cache antigo do sistema."""
        # Implementar limpeza de cache
        pass
    
    async def _analyze_metrics(self) -> Dict:
        """Analisa métricas do sistema."""
        # Implementar análise de métricas
        return {}
    
    async def _generate_optimization_suggestions(self, metrics: Dict) -> List:
        """Gera sugestões de otimização baseadas nas métricas."""
        # Implementar geração de sugestões
        return []

# Instância global do gerenciador
system_manager = SystemManager() 