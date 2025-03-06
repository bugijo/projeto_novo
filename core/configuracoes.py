import json
from pathlib import Path
from typing import Any, Dict, Optional
import copy

class GerenciadorConfiguracoes:
    def __init__(self):
        self.config = self._carregar_configuracoes()
        self.config_padrao = self._obter_config_padrao()
        self.observadores = []
        
    def _carregar_configuracoes(self) -> dict:
        """Carrega as configurações do arquivo"""
        config_path = Path("config/programacao.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._obter_config_padrao()
        
    def _obter_config_padrao(self) -> dict:
        """Retorna as configurações padrão"""
        return {
            "preferencias": {
                "tema": {
                    "padrao": "dark",
                    "opcoes": ["dark", "light"],
                    "atualizar_automaticamente": True
                },
                "interface": {
                    "fonte": {
                        "familia": "Consolas",
                        "tamanho": 12,
                        "estilo": "normal"
                    },
                    "cores": {
                        "dark": {
                            "fundo": "#2b2b2b",
                            "texto": "#ffffff",
                            "destaque": "#4a9eff",
                            "erro": "#ff4a4a",
                            "aviso": "#ffaa4a",
                            "sucesso": "#4aff4a"
                        },
                        "light": {
                            "fundo": "#ffffff",
                            "texto": "#000000",
                            "destaque": "#0066cc",
                            "erro": "#cc0000",
                            "aviso": "#cc6600",
                            "sucesso": "#00cc00"
                        }
                    },
                    "layout": {
                        "mostrar_numeros_linha": True,
                        "quebrar_linha": True,
                        "destacar_linha_atual": True,
                        "mostrar_espacos": True
                    }
                },
                "editor": {
                    "auto_indentacao": True,
                    "auto_completar": True,
                    "auto_fechar_tags": True,
                    "auto_fechar_chaves": True,
                    "destacar_sintaxe": True,
                    "sugestoes_tempo_real": True,
                    "formatacao_ao_salvar": True
                },
                "assistente": {
                    "sugestoes": {
                        "mostrar_automaticamente": True,
                        "max_sugestoes": 5,
                        "ordenar_por": "relevancia",
                        "incluir_exemplos": True
                    },
                    "analise": {
                        "tempo_real": True,
                        "intervalo_analise": 1000,
                        "nivel_detalhe": "alto",
                        "ignorar_arquivos": [
                            "*.pyc",
                            "__pycache__",
                            "venv",
                            "env"
                        ]
                    },
                    "notificacoes": {
                        "erros": True,
                        "avisos": True,
                        "sugestoes": True,
                        "atualizacoes": True
                    }
                },
                "perfil": {
                    "salvar_historico": True,
                    "max_historico": 1000,
                    "sincronizar": True,
                    "backup_automatico": True,
                    "intervalo_backup": 3600
                }
            }
        }
        
    def obter_configuracao(self, caminho: str, padrao: Any = None) -> Any:
        """Obtém uma configuração específica pelo caminho"""
        try:
            valor = self.config
            for chave in caminho.split('.'):
                valor = valor[chave]
            return valor
        except (KeyError, TypeError):
            return padrao
            
    def definir_configuracao(self, caminho: str, valor: Any):
        """Define uma configuração específica pelo caminho"""
        try:
            config = self.config
            chaves = caminho.split('.')
            for chave in chaves[:-1]:
                config = config[chave]
            config[chaves[-1]] = valor
            self._salvar_configuracoes()
            self._notificar_alteracao(caminho, valor)
        except (KeyError, TypeError) as e:
            print(f"Erro ao definir configuração: {e}")
            
    def restaurar_padrao(self, caminho: Optional[str] = None):
        """Restaura configurações para o padrão"""
        if caminho:
            try:
                valor_padrao = self.config_padrao
                for chave in caminho.split('.'):
                    valor_padrao = valor_padrao[chave]
                self.definir_configuracao(caminho, copy.deepcopy(valor_padrao))
            except (KeyError, TypeError) as e:
                print(f"Erro ao restaurar configuração: {e}")
        else:
            self.config = copy.deepcopy(self.config_padrao)
            self._salvar_configuracoes()
            self._notificar_alteracao(None, None)
            
    def adicionar_observador(self, callback):
        """Adiciona um observador para mudanças nas configurações"""
        if callback not in self.observadores:
            self.observadores.append(callback)
            
    def remover_observador(self, callback):
        """Remove um observador"""
        if callback in self.observadores:
            self.observadores.remove(callback)
            
    def _notificar_alteracao(self, caminho: Optional[str], valor: Any):
        """Notifica os observadores sobre alterações"""
        for callback in self.observadores:
            try:
                callback(caminho, valor)
            except Exception as e:
                print(f"Erro ao notificar observador: {e}")
                
    def _salvar_configuracoes(self):
        """Salva as configurações no arquivo"""
        config_path = Path("config/programacao.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
    def obter_tema(self) -> Dict[str, str]:
        """Retorna as cores do tema atual"""
        tema = self.obter_configuracao('preferencias.tema.padrao', 'dark')
        return self.obter_configuracao(f'preferencias.interface.cores.{tema}', {})
        
    def obter_fonte(self) -> Dict[str, Any]:
        """Retorna as configurações de fonte"""
        return self.obter_configuracao('preferencias.interface.fonte', {
            "familia": "Consolas",
            "tamanho": 12,
            "estilo": "normal"
        })
        
    def obter_layout(self) -> Dict[str, bool]:
        """Retorna as configurações de layout"""
        return self.obter_configuracao('preferencias.interface.layout', {
            "mostrar_numeros_linha": True,
            "quebrar_linha": True,
            "destacar_linha_atual": True,
            "mostrar_espacos": True
        })
        
    def obter_config_editor(self) -> Dict[str, bool]:
        """Retorna as configurações do editor"""
        return self.obter_configuracao('preferencias.editor', {
            "auto_indentacao": True,
            "auto_completar": True,
            "auto_fechar_tags": True,
            "auto_fechar_chaves": True,
            "destacar_sintaxe": True,
            "sugestoes_tempo_real": True,
            "formatacao_ao_salvar": True
        })
        
    def obter_config_sugestoes(self) -> Dict[str, Any]:
        """Retorna as configurações de sugestões"""
        return self.obter_configuracao('preferencias.assistente.sugestoes', {
            "mostrar_automaticamente": True,
            "max_sugestoes": 5,
            "ordenar_por": "relevancia",
            "incluir_exemplos": True
        })
        
    def obter_config_analise(self) -> Dict[str, Any]:
        """Retorna as configurações de análise"""
        return self.obter_configuracao('preferencias.assistente.analise', {
            "tempo_real": True,
            "intervalo_analise": 1000,
            "nivel_detalhe": "alto",
            "ignorar_arquivos": [
                "*.pyc",
                "__pycache__",
                "venv",
                "env"
            ]
        })
        
    def obter_config_notificacoes(self) -> Dict[str, bool]:
        """Retorna as configurações de notificações"""
        return self.obter_configuracao('preferencias.assistente.notificacoes', {
            "erros": True,
            "avisos": True,
            "sugestoes": True,
            "atualizacoes": True
        })
        
    def obter_config_perfil(self) -> Dict[str, Any]:
        """Retorna as configurações do perfil"""
        return self.obter_configuracao('preferencias.perfil', {
            "salvar_historico": True,
            "max_historico": 1000,
            "sincronizar": True,
            "backup_automatico": True,
            "intervalo_backup": 3600
        }) 