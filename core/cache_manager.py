import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from config.system_config import CACHE_CONFIG

class CacheManager:
    """Gerenciador de cache para otimizar o desempenho."""
    
    def __init__(self):
        self.logger = logging.getLogger('CacheManager')
        self.cache_dir = Path(CACHE_CONFIG.get('dir', 'cache'))
        self.max_size = CACHE_CONFIG.get('max_size', 1024 * 1024 * 1024)  # 1GB
        self.ttl = CACHE_CONFIG.get('ttl', 3600)  # 1 hora
        
        # Cria diretório de cache
        self.cache_dir.mkdir(exist_ok=True)
        
        # Carrega metadados do cache
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Carrega metadados do cache."""
        metadata_path = self.cache_dir / 'metadata.json'
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Salva metadados do cache."""
        metadata_path = self.cache_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_key(self, data: Any) -> str:
        """Gera uma chave única para os dados."""
        if isinstance(data, dict):
            # Ordena o dicionário para garantir consistência
            data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """Recupera dados do cache."""
        try:
            cache_key = self._generate_key(key)
            
            # Verifica se existe no cache
            if cache_key not in self.metadata:
                return None
            
            # Verifica TTL
            entry = self.metadata[cache_key]
            if time.time() - entry['timestamp'] > self.ttl:
                self._remove_entry(cache_key)
                return None
            
            # Carrega dados
            cache_path = self.cache_dir / f"{cache_key}.json"
            if not cache_path.exists():
                self._remove_entry(cache_key)
                return None
            
            with open(cache_path, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar do cache: {str(e)}")
            return None
    
    def set(self, key: Any, value: Any) -> bool:
        """Armazena dados no cache."""
        try:
            cache_key = self._generate_key(key)
            
            # Verifica tamanho do cache
            self._ensure_cache_size()
            
            # Salva dados
            cache_path = self.cache_dir / f"{cache_key}.json"
            with open(cache_path, 'w') as f:
                json.dump(value, f)
            
            # Atualiza metadados
            self.metadata[cache_key] = {
                'timestamp': time.time(),
                'size': cache_path.stat().st_size
            }
            self._save_metadata()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar no cache: {str(e)}")
            return False
    
    def _ensure_cache_size(self):
        """Garante que o cache não exceda o tamanho máximo."""
        current_size = sum(entry['size'] for entry in self.metadata.values())
        
        if current_size > self.max_size:
            # Remove entradas antigas até atingir 80% do tamanho máximo
            target_size = self.max_size * 0.8
            
            # Ordena por timestamp
            entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            for cache_key, _ in entries:
                self._remove_entry(cache_key)
                current_size = sum(entry['size'] for entry in self.metadata.values())
                if current_size <= target_size:
                    break
    
    def _remove_entry(self, cache_key: str):
        """Remove uma entrada do cache."""
        try:
            # Remove arquivo
            cache_path = self.cache_dir / f"{cache_key}.json"
            if cache_path.exists():
                cache_path.unlink()
            
            # Remove dos metadados
            if cache_key in self.metadata:
                del self.metadata[cache_key]
                self._save_metadata()
                
        except Exception as e:
            self.logger.error(f"Erro ao remover entrada do cache: {str(e)}")
    
    def clear(self):
        """Limpa todo o cache."""
        try:
            # Remove todos os arquivos
            for file in self.cache_dir.glob('*.json'):
                file.unlink()
            
            # Limpa metadados
            self.metadata = {}
            self._save_metadata()
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache."""
        try:
            total_size = sum(entry['size'] for entry in self.metadata.values())
            total_entries = len(self.metadata)
            oldest_entry = min(
                entry['timestamp'] for entry in self.metadata.values()
            ) if self.metadata else 0
            newest_entry = max(
                entry['timestamp'] for entry in self.metadata.values()
            ) if self.metadata else 0
            
            return {
                'total_size': total_size,
                'total_entries': total_entries,
                'size_limit': self.max_size,
                'ttl': self.ttl,
                'oldest_entry': oldest_entry,
                'newest_entry': newest_entry,
                'usage_percent': (total_size / self.max_size) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
            return {} 