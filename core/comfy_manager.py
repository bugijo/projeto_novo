import os
import json
import asyncio
import aiohttp
import websockets
import logging
import subprocess
from typing import Dict, Optional
from pathlib import Path

from config.system_config import COMFY_CONFIG

class ComfyUIManager:
    """Gerenciador para interação com o ComfyUI."""
    
    def __init__(self):
        self.logger = logging.getLogger('ComfyUIManager')
        self.process = None
        self.ws = None
        self.session = None
        self.running = False
    
    async def start_async(self) -> bool:
        """Inicia o ComfyUI em modo assíncrono."""
        try:
            if self.running:
                return True
            
            # Inicia processo do ComfyUI
            comfy_path = Path(COMFY_CONFIG.get('path', 'ComfyUI'))
            if not comfy_path.exists():
                raise FileNotFoundError("Diretório do ComfyUI não encontrado")
            
            cmd = ['python', str(comfy_path / 'main.py')]
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(comfy_path)
            )
            
            # Aguarda ComfyUI iniciar
            await self._wait_for_startup()
            
            # Inicializa sessão HTTP
            self.session = aiohttp.ClientSession()
            
            # Conecta ao WebSocket
            await self._connect_websocket()
            
            self.running = True
            self.logger.info("ComfyUI iniciado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar ComfyUI: {str(e)}")
            await self.stop()
            raise
    
    async def _wait_for_startup(self, timeout: int = 30):
        """Aguarda o ComfyUI iniciar completamente."""
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(COMFY_CONFIG['api_url']) as response:
                        if response.status == 200:
                            return
            except:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError("Timeout aguardando ComfyUI iniciar")
                await asyncio.sleep(1)
    
    async def _connect_websocket(self):
        """Conecta ao WebSocket do ComfyUI."""
        try:
            self.ws = await websockets.connect(COMFY_CONFIG['ws_url'])
            self.logger.info("Conectado ao WebSocket do ComfyUI")
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao WebSocket: {str(e)}")
            raise
    
    async def execute_workflow(self, workflow_path: str, output_dir: Path) -> Dict:
        """Executa um workflow no ComfyUI."""
        try:
            if not self.running:
                raise RuntimeError("ComfyUI não está rodando")
            
            # Carrega workflow
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Envia workflow para execução
            async with self.session.post(
                f"{COMFY_CONFIG['api_url']}/prompt",
                json=workflow
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Erro ao enviar workflow: {await response.text()}")
                
                prompt_id = (await response.json())['prompt_id']
            
            # Aguarda conclusão
            result = await self._wait_for_execution(prompt_id)
            
            # Processa resultado
            if result.get('success'):
                # Salva outputs
                outputs = result.get('outputs', {})
                saved_files = await self._save_outputs(outputs, output_dir)
                result['saved_files'] = saved_files
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao executar workflow: {str(e)}")
            raise
    
    async def _wait_for_execution(self, prompt_id: str) -> Dict:
        """Aguarda a conclusão da execução de um workflow."""
        try:
            while True:
                msg = await self.ws.recv()
                data = json.loads(msg)
                
                if data.get('type') == 'executing':
                    if data.get('data', {}).get('node') is None:
                        # Execução concluída
                        return {
                            'success': True,
                            'outputs': data.get('data', {}).get('outputs', {})
                        }
                elif data.get('type') == 'error':
                    return {
                        'success': False,
                        'error': data.get('message', 'Erro desconhecido')
                    }
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Erro aguardando execução: {str(e)}")
            raise
    
    async def _save_outputs(self, outputs: Dict, output_dir: Path) -> Dict:
        """Salva os outputs do workflow."""
        saved_files = {}
        
        try:
            for node_id, node_outputs in outputs.items():
                for output_name, output_data in node_outputs.items():
                    if isinstance(output_data, str) and output_data.startswith('http'):
                        # Download do arquivo
                        filename = f"{node_id}_{output_name}.png"
                        filepath = output_dir / filename
                        
                        async with self.session.get(output_data) as response:
                            if response.status == 200:
                                content = await response.read()
                                with open(filepath, 'wb') as f:
                                    f.write(content)
                                saved_files[f"{node_id}_{output_name}"] = str(filepath)
            
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar outputs: {str(e)}")
            raise
    
    async def stop_workflow(self, workflow_id: str):
        """Para a execução de um workflow."""
        try:
            if not self.running:
                return
            
            async with self.session.post(
                f"{COMFY_CONFIG['api_url']}/interrupt",
                json={'prompt_id': workflow_id}
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Erro ao parar workflow: {await response.text()}")
                
        except Exception as e:
            self.logger.error(f"Erro ao parar workflow: {str(e)}")
            raise
    
    async def stop(self):
        """Para o ComfyUI e limpa recursos."""
        try:
            self.running = False
            
            # Fecha WebSocket
            if self.ws:
                await self.ws.close()
                self.ws = None
            
            # Fecha sessão HTTP
            if self.session:
                await self.session.close()
                self.session = None
            
            # Para processo do ComfyUI
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.process = None
            
            self.logger.info("ComfyUI parado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar ComfyUI: {str(e)}")
            raise 