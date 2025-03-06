import os
import json
import uuid
import asyncio
from typing import Dict, List, Optional
import logging
from pathlib import Path

from config.system_config import (
    WORKFLOW_CONFIG,
    WORKFLOWS_DIR,
    TEMPLATES_DIR,
    OUTPUT_DIR
)

class WorkflowManager:
    """Gerenciador de workflows do ComfyUI."""
    
    def __init__(self, comfy_manager):
        self.logger = logging.getLogger('WorkflowManager')
        self.comfy_manager = comfy_manager
        self.active_workflows = {}
        self.workflow_templates = self._load_templates()
        
        # Cria diretórios necessários
        WORKFLOWS_DIR.mkdir(exist_ok=True)
        TEMPLATES_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
    
    def _load_templates(self) -> Dict:
        """Carrega templates de workflow do diretório de templates."""
        templates = {}
        try:
            for file in TEMPLATES_DIR.glob('*.json'):
                with open(file, 'r', encoding='utf-8') as f:
                    templates[file.stem] = json.load(f)
            return templates
        except Exception as e:
            self.logger.error(f"Erro ao carregar templates: {str(e)}")
            return {}
    
    async def create_workflow(self, task_type: str, parameters: Dict) -> Dict:
        """Cria um workflow baseado no tipo de tarefa e parâmetros."""
        try:
            # Seleciona template base
            template = self._select_template(task_type)
            if not template:
                raise ValueError(f"Template não encontrado para o tipo de tarefa: {task_type}")
            
            # Customiza workflow
            workflow = await self._customize_workflow(template, parameters)
            
            # Salva workflow
            workflow_id = str(uuid.uuid4())
            workflow_path = WORKFLOWS_DIR / f"{workflow_id}.json"
            
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2)
            
            return {
                'id': workflow_id,
                'path': str(workflow_path),
                'type': task_type,
                'parameters': parameters
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao criar workflow: {str(e)}")
            raise
    
    def _select_template(self, task_type: str) -> Optional[Dict]:
        """Seleciona o template apropriado para o tipo de tarefa."""
        # Mapeamento de tipos de tarefa para templates
        template_mapping = {
            'image_generation': 'image_gen',
            'code_generation': 'code_gen',
            '3d_modeling': '3d_model',
            'app_development': 'app_dev',
            'game_development': 'game_dev'
        }
        
        template_name = template_mapping.get(task_type)
        return self.workflow_templates.get(template_name)
    
    async def _customize_workflow(self, template: Dict, parameters: Dict) -> Dict:
        """Customiza o workflow baseado nos parâmetros."""
        workflow = template.copy()
        
        # Atualiza parâmetros do workflow
        if 'message' in parameters:
            workflow['prompt'] = parameters['message']
        
        if 'style' in parameters:
            workflow['style'] = parameters['style']
        
        # Adiciona nós específicos baseado no tipo de tarefa
        if parameters.get('type') == 'image_generation':
            workflow = await self._add_image_nodes(workflow, parameters)
        elif parameters.get('type') == '3d_modeling':
            workflow = await self._add_3d_nodes(workflow, parameters)
        
        return workflow
    
    async def _add_image_nodes(self, workflow: Dict, parameters: Dict) -> Dict:
        """Adiciona nós específicos para geração de imagem."""
        # Implementar adição de nós para geração de imagem
        return workflow
    
    async def _add_3d_nodes(self, workflow: Dict, parameters: Dict) -> Dict:
        """Adiciona nós específicos para modelagem 3D."""
        # Implementar adição de nós para modelagem 3D
        return workflow
    
    async def execute_workflow(self, workflow: Dict) -> str:
        """Executa um workflow no ComfyUI."""
        try:
            # Verifica limite de workflows concorrentes
            if len(self.active_workflows) >= WORKFLOW_CONFIG['max_concurrent']:
                raise RuntimeError("Limite de workflows concorrentes atingido")
            
            # Inicia execução
            workflow_id = workflow['id']
            self.active_workflows[workflow_id] = {
                'status': 'running',
                'progress': 0,
                'output': None,
                'error': None
            }
            
            # Executa no ComfyUI
            result = await self.comfy_manager.execute_workflow(
                workflow_path=workflow['path'],
                output_dir=OUTPUT_DIR
            )
            
            # Atualiza status
            if result.get('success'):
                self.active_workflows[workflow_id]['status'] = 'completed'
                self.active_workflows[workflow_id]['output'] = result.get('output')
            else:
                self.active_workflows[workflow_id]['status'] = 'failed'
                self.active_workflows[workflow_id]['error'] = result.get('error')
            
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Erro ao executar workflow: {str(e)}")
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]['status'] = 'failed'
                self.active_workflows[workflow_id]['error'] = str(e)
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """Retorna o status de um workflow."""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow não encontrado: {workflow_id}")
        
        return self.active_workflows[workflow_id]
    
    async def stop_workflow(self, workflow_id: str):
        """Para a execução de um workflow."""
        try:
            if workflow_id in self.active_workflows:
                await self.comfy_manager.stop_workflow(workflow_id)
                self.active_workflows[workflow_id]['status'] = 'stopped'
                
        except Exception as e:
            self.logger.error(f"Erro ao parar workflow: {str(e)}")
            raise
    
    async def stop_all(self):
        """Para todos os workflows ativos."""
        try:
            for workflow_id in list(self.active_workflows.keys()):
                await self.stop_workflow(workflow_id)
                
        except Exception as e:
            self.logger.error(f"Erro ao parar todos os workflows: {str(e)}")
            raise
    
    def cleanup_old_workflows(self):
        """Remove workflows antigos do sistema."""
        try:
            # Remove arquivos de workflow antigos
            for file in WORKFLOWS_DIR.glob('*.json'):
                if file.stat().st_mtime < (time.time() - 86400):  # Mais de 24 horas
                    file.unlink()
            
            # Remove outputs antigos
            for file in OUTPUT_DIR.glob('*'):
                if file.stat().st_mtime < (time.time() - 86400):
                    file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Erro na limpeza de workflows: {str(e)}")
            raise 