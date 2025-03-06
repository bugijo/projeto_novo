import unittest
import sys
import os
from pathlib import Path
import json
import shutil
import tempfile
from datetime import datetime

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, load_config, save_config, load_workflows, save_workflow

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Cria diretórios temporários para testes
        self.test_dir = tempfile.mkdtemp()
        self.workflows_dir = os.path.join(self.test_dir, 'workflows')
        self.templates_dir = os.path.join(self.test_dir, 'templates')
        os.makedirs(self.workflows_dir)
        os.makedirs(self.templates_dir)
        
        # Backup das configurações originais
        self.original_workflows_dir = app.config.get('WORKFLOWS_DIR')
        self.original_templates_dir = app.config.get('TEMPLATES_DIR')
        
        # Define diretórios temporários
        app.config['WORKFLOWS_DIR'] = self.workflows_dir
        app.config['TEMPLATES_DIR'] = self.templates_dir
    
    def tearDown(self):
        """Limpeza após cada teste"""
        # Restaura configurações originais
        app.config['WORKFLOWS_DIR'] = self.original_workflows_dir
        app.config['TEMPLATES_DIR'] = self.original_templates_dir
        
        # Remove diretórios temporários
        shutil.rmtree(self.test_dir)
    
    def test_index_route(self):
        """Testa se a rota principal está funcionando"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_static_files(self):
        """Testa se os arquivos estáticos estão sendo servidos"""
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
    
    def test_process_request(self):
        """Testa o processamento de requisições"""
        test_prompt = "Teste de processamento"
        response = self.app.post('/api/process',
                               json={'prompt': test_prompt},
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertIn('timestamp', data)
    
    def test_workflow_management(self):
        """Testa o gerenciamento de workflows"""
        # Testa criação de workflow
        test_workflow = {
            'name': 'Teste Workflow',
            'description': 'Workflow para teste',
            'type': 'image'
        }
        
        response = self.app.post('/api/workflows',
                               json=test_workflow,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        created_workflow = json.loads(response.data)
        self.assertIn('id', created_workflow)
        
        # Testa listagem de workflows
        response = self.app.get('/api/workflows')
        self.assertEqual(response.status_code, 200)
        workflows = json.loads(response.data)['workflows']
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]['name'], test_workflow['name'])
    
    def test_template_management(self):
        """Testa o gerenciamento de templates"""
        # Cria um template de teste
        test_template = {
            'id': '1',
            'name': 'Template Teste',
            'description': 'Template para teste',
            'type': 'image'
        }
        
        with open(os.path.join(self.templates_dir, 'test.json'), 'w') as f:
            json.dump(test_template, f)
        
        # Testa listagem de templates
        response = self.app.get('/api/templates')
        self.assertEqual(response.status_code, 200)
        templates = json.loads(response.data)['templates']
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]['name'], test_template['name'])
    
    def test_config_management(self):
        """Testa o gerenciamento de configurações"""
        # Testa salvamento de configurações
        test_config = {
            'mainModel': 'test-model',
            'temperature': 0.8,
            'autoSave': False
        }
        
        response = self.app.post('/api/config',
                               json=test_config,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Testa carregamento de configurações
        response = self.app.get('/api/config')
        self.assertEqual(response.status_code, 200)
        config = json.loads(response.data)
        self.assertEqual(config['mainModel'], test_config['mainModel'])
        self.assertEqual(config['temperature'], test_config['temperature'])
    
    def test_history_management(self):
        """Testa o gerenciamento do histórico"""
        # Cria uma entrada no histórico através de uma ação
        test_prompt = "Teste histórico"
        self.app.post('/api/process',
                     json={'prompt': test_prompt},
                     content_type='application/json')
        
        # Testa listagem do histórico
        response = self.app.get('/api/history')
        self.assertEqual(response.status_code, 200)
        history = json.loads(response.data)['history']
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1]['type'], 'chat')
    
    def test_workflow_execution(self):
        """Testa a execução de workflows"""
        # Cria um workflow primeiro
        test_workflow = {
            'name': 'Workflow Execução',
            'description': 'Teste de execução',
            'type': 'image'
        }
        
        response = self.app.post('/api/workflows',
                               json=test_workflow,
                               content_type='application/json')
        
        workflow_id = json.loads(response.data)['id']
        
        # Testa execução do workflow
        response = self.app.post('/api/execute',
                               json={'workflow_id': workflow_id},
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['status'], 'success')
    
    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Testa requisição sem prompt
        response = self.app.post('/api/process',
                               json={},
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Testa execução de workflow sem ID
        response = self.app.post('/api/execute',
                               json={},
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_comfyui_integration(self):
        """Testa a integração com o ComfyUI"""
        try:
            # Tenta importar o módulo main do ComfyUI
            comfy_path = Path("../ComfyUI-master").resolve()
            sys.path.append(str(comfy_path))
            import main as comfy_main
            
            self.assertTrue(True, "ComfyUI importado com sucesso")
        except ImportError as e:
            self.fail(f"Falha ao importar ComfyUI: {str(e)}")
    
    def test_performance(self):
        """Testa o desempenho básico da aplicação"""
        import time
        
        # Testa tempo de resposta da API
        start_time = time.time()
        self.app.get('/')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, "Tempo de resposta maior que 1 segundo")
        
        # Testa múltiplas requisições simultâneas
        import concurrent.futures
        
        def make_request():
            return self.app.post('/api/process',
                               json={'prompt': 'teste'},
                               content_type='application/json')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]
        
        for response in results:
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 