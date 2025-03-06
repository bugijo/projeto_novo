import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import zipfile
import shutil
from dataclasses import dataclass
from ide_config import IDE_CONFIG, DEFAULT_EXTENSIONS
import logging

@dataclass
class Extension:
    id: str
    name: str
    description: str
    version: str
    author: str
    repository: str
    tags: List[str]
    dependencies: List[str]
    enabled: bool = True
    installed: bool = False
    path: Optional[Path] = None

class ExtensionManager:
    def __init__(self, extensions_dir: Path):
        self.extensions_dir = Path(extensions_dir)
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        self.extensions: Dict[str, Extension] = {}
        self.marketplace_url = "https://marketplace.devassistant.io/api"
        self.load_installed_extensions()
        
    def load_installed_extensions(self):
        """Carrega todas as extensões instaladas"""
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                manifest_path = ext_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                            ext = Extension(
                                id=manifest["id"],
                                name=manifest["name"],
                                description=manifest["description"],
                                version=manifest["version"],
                                author=manifest["author"],
                                repository=manifest["repository"],
                                tags=manifest["tags"],
                                dependencies=manifest["dependencies"],
                                installed=True,
                                enabled=manifest.get("enabled", True)
                            )
                            ext.path = ext_dir
                            self.extensions[ext.name] = ext
                    except Exception as e:
                        logging.error(f"Erro ao carregar extensão {ext_dir}: {e}")
    
    async def search_marketplace(self, query: str) -> List[Dict]:
        """Busca extensões no marketplace"""
        try:
            response = await requests.get(f"{self.marketplace_url}/search", params={"q": query})
            return response.json()["extensions"]
        except Exception as e:
            logging.error(f"Erro ao buscar no marketplace: {e}")
            return []

    async def install_extension(self, ext_id: str) -> bool:
        """Instala uma extensão do marketplace"""
        try:
            # Download da extensão
            response = await requests.get(f"{self.marketplace_url}/download/{ext_id}")
            if not response.ok:
                return False

            # Salvar arquivo temporário
            temp_file = self.extensions_dir / f"{ext_id}.zip"
            with open(temp_file, "wb") as f:
                f.write(response.content)

            # Extrair extensão
            ext_dir = self.extensions_dir / ext_id
            with zipfile.ZipFile(temp_file) as zf:
                zf.extractall(ext_dir)

            # Carregar extensão
            manifest_path = ext_dir / "manifest.json"
            with open(manifest_path) as f:
                manifest = json.load(f)
                ext = Extension(
                    id=manifest["id"],
                    name=manifest["name"],
                    description=manifest["description"],
                    version=manifest["version"],
                    author=manifest["author"],
                    repository=manifest["repository"],
                    tags=manifest["tags"],
                    dependencies=manifest["dependencies"],
                    installed=True,
                    enabled=manifest.get("enabled", True)
                )
                ext.path = ext_dir
                self.extensions[ext.name] = ext

            # Limpar arquivo temporário
            temp_file.unlink()
            return True

        except Exception as e:
            logging.error(f"Erro ao instalar extensão {ext_id}: {e}")
            return False

    def uninstall_extension(self, ext_name: str) -> bool:
        """Desinstala uma extensão"""
        try:
            if ext_name not in self.extensions:
                return False

            ext = self.extensions[ext_name]
            if ext.path and ext.path.exists():
                shutil.rmtree(ext.path)
            del self.extensions[ext_name]
            return True

        except Exception as e:
            logging.error(f"Erro ao desinstalar extensão {ext_name}: {e}")
            return False

    def enable_extension(self, ext_name: str) -> bool:
        """Ativa uma extensão"""
        if ext_name in self.extensions:
            self.extensions[ext_name].enabled = True
            return True
        return False

    def disable_extension(self, ext_name: str) -> bool:
        """Desativa uma extensão"""
        if ext_name in self.extensions:
            self.extensions[ext_name].enabled = False
            return True
        return False

    def get_extension_config(self, ext_name: str) -> Optional[Dict]:
        """Obtém a configuração de uma extensão"""
        if ext_name not in self.extensions:
            return None

        ext = self.extensions[ext_name]
        config_path = ext.path / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Erro ao ler configuração da extensão {ext_name}: {e}")
        return None

    def save_extension_config(self, ext_name: str, config: Dict) -> bool:
        """Salva a configuração de uma extensão"""
        if ext_name not in self.extensions:
            return False

        ext = self.extensions[ext_name]
        config_path = ext.path / "config.json"
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar configuração da extensão {ext_name}: {e}")
            return False
    
    def fetch_available_extensions(self) -> Dict[str, Extension]:
        """Busca extensões disponíveis no marketplace"""
        try:
            response = requests.get(f"{IDE_CONFIG['marketplace_url']}/api/extensions")
            if response.status_code == 200:
                extensions_data = response.json()
                for ext_data in extensions_data:
                    ext = Extension(
                        id=ext_data["id"],
                        name=ext_data["name"],
                        description=ext_data["description"],
                        version=ext_data["version"],
                        author=ext_data["author"],
                        repository=ext_data["repository"],
                        tags=ext_data["tags"],
                        dependencies=ext_data["dependencies"],
                        installed=ext_data["id"] in self.extensions
                    )
                    self.extensions[ext.name] = ext
            return self.extensions
        except Exception as e:
            print(f"Erro ao buscar extensões: {e}")
            return {}
    
    def update_extension(self, extension_id: str) -> bool:
        """Atualiza uma extensão"""
        if extension_id not in self.extensions:
            return False
        
        # Desinstalar versão atual
        if not self.uninstall_extension(extension_id):
            return False
        
        # Instalar nova versão
        return self.install_extension(extension_id)
    
    def get_extension_status(self, extension_id: str) -> Optional[Dict]:
        """Retorna o status de uma extensão"""
        if extension_id in self.extensions:
            ext = self.extensions[extension_id]
            return {
                "installed": True,
                "enabled": ext.enabled,
                "version": ext.version
            }
        return None
    
    def search_extensions(self, query: str) -> List[Extension]:
        """Pesquisa extensões disponíveis"""
        query = query.lower()
        results = []
        
        for ext in self.extensions.values():
            if (query in ext.name.lower() or
                query in ext.description.lower() or
                query in ext.author.lower() or
                any(query in tag.lower() for tag in ext.tags)):
                results.append(ext)
        
        return results
    
    def get_recommended_extensions(self) -> List[Extension]:
        """Retorna extensões recomendadas baseadas no uso"""
        # TODO: Implementar sistema de recomendação baseado em uso
        return list(self.extensions.values())[:5]
    
    def install_default_extensions(self):
        """Instala as extensões padrão"""
        for ext_id, config in DEFAULT_EXTENSIONS.items():
            if config["enabled"] and ext_id not in self.extensions:
                self.install_extension(ext_id) 