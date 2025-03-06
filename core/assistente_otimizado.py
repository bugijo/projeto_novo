from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import importlib
import psutil
import gc
import threading
from queue import Queue
import json
from pathlib import Path
import logging
from .monitor_seguranca import MonitorSeguranca
from .gerenciador_sistema_avancado import GerenciadorSistemaAvancado

@dataclass
class ModuloConfig:
    nome: str
    prioridade: int
    memoria_min: float
    memoria_max: float
    dependencias: List[str]
    sempre_ativo: bool = False
    
    def __post_init__(self):
        if self.dependencias is None:
            self.dependencias = []

class GerenciadorRecursos:
    def __init__(self):
        self.processo = psutil.Process()
        self.limite_memoria = 0.7  # 70% da RAM
        self.modulos_ativos = {}
        self.lock = threading.Lock()
        
    def memoria_disponivel(self) -> float:
        return psutil.virtual_memory().available / psutil.virtual_memory().total
        
    def memoria_processo(self) -> float:
        return self.processo.memory_percent() / 100
        
    def pode_carregar_modulo(self, memoria_necessaria: float) -> bool:
        with self.lock:
            memoria_atual = self.memoria_processo()
            return (memoria_atual + memoria_necessaria) < self.limite_memoria
            
    def otimizar_memoria(self):
        if self.memoria_processo() > self.limite_memoria:
            gc.collect()
            # Descarrega módulos não prioritários
            for modulo in sorted(self.modulos_ativos.values(), 
                               key=lambda m: m.prioridade):
                if not modulo.sempre_ativo:
                    self.descarregar_modulo(modulo.nome)
                    if self.memoria_processo() < self.limite_memoria:
                        break

class AssistenteOtimizado:
    def __init__(self):
        self.config = self._carregar_config()
        self.gerenciador = GerenciadorRecursos()
        self.modulos = {}
        self.contexto = {}
        self.logger = logging.getLogger(__name__)
        self.monitor_seguranca = MonitorSeguranca()
        self.gerenciador_sistema = GerenciadorSistemaAvancado()
        self.monitor_seguranca.iniciar_monitoramento()
        
    def _carregar_config(self) -> dict:
        config_path = Path("config/assistente_config.json")
        with open(config_path) as f:
            return json.load(f)
            
    def _carregar_modulo(self, nome: str) -> bool:
        """Carrega um módulo dinamicamente se houver recursos disponíveis"""
        config = self.config["modulos"][nome]
        modulo = ModuloConfig(
            nome=nome,
            prioridade=config["prioridade"],
            memoria_min=0.05,  # 5% da RAM
            memoria_max=0.15,  # 15% da RAM
            dependencias=config.get("dependencias", []),
            sempre_ativo=config.get("sempre_ativo", False)
        )
        
        if not self.gerenciador.pode_carregar_modulo(modulo.memoria_min):
            self.gerenciador.otimizar_memoria()
            if not self.gerenciador.pode_carregar_modulo(modulo.memoria_min):
                return False
                
        # Carrega dependências
        for dep in modulo.dependencias:
            if dep not in self.modulos:
                if not self._carregar_modulo(dep):
                    return False
                    
        # Importa e inicializa o módulo
        try:
            # Aqui seria a importação dinâmica do módulo
            self.modulos[nome] = modulo
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar módulo {nome}: {e}")
            return False
            
    async def processar_comando(self, comando: str) -> str:
        """Processa um comando do usuário carregando apenas os módulos necessários"""
        # Verifica se é um comando relacionado à segurança
        if any(palavra in comando.lower() for palavra in ["segurança", "vírus", "malware", "status", "desempenho"]):
            return self._processar_comando_seguranca(comando)
            
        # Verifica se é um comando relacionado a otimização do sistema
        if any(palavra in comando.lower() for palavra in ["otimizar", "bios", "configurar", "hardware"]):
            return await self._processar_comando_sistema(comando)
            
        modulos_necessarios = self._identificar_modulos_necessarios(comando)
        
        # Carrega módulos necessários
        for modulo in modulos_necessarios:
            if modulo not in self.modulos:
                if not self._carregar_modulo(modulo):
                    return f"Não foi possível carregar o módulo {modulo}"
                    
        # Processa o comando usando os módulos carregados
        try:
            resultado = self._executar_comando(comando)
            
            # Otimiza recursos após processamento
            if self.config["otimizacao"]["descarregar_apos_uso"]:
                self._otimizar_modulos_carregados()
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar comando: {e}")
            return f"Erro ao processar comando: {str(e)}"
            
    def _processar_comando_seguranca(self, comando: str) -> str:
        """Processa comandos relacionados à segurança"""
        comando = comando.lower()
        
        if "status" in comando or "relatório" in comando:
            relatorio = self.monitor_seguranca.obter_relatorio()
            return self._formatar_relatorio_seguranca(relatorio)
            
        elif "alertas" in comando:
            alertas = self.monitor_seguranca.alertas[-10:]  # últimos 10 alertas
            return self._formatar_alertas(alertas)
            
        elif "limpar alertas" in comando:
            self.monitor_seguranca.limpar_alertas()
            return "Alertas limpos com sucesso"
            
        elif "desempenho" in comando:
            metricas = self.monitor_seguranca.metricas.get("recursos", {})
            return self._formatar_metricas_desempenho(metricas)
            
        return "Comando de segurança não reconhecido"
            
    async def _processar_comando_sistema(self, comando: str) -> str:
        """Processa comandos relacionados a otimização do sistema"""
        comando = comando.lower()
        
        if "otimizar" in comando:
            # Identifica o perfil de otimização
            perfil = "automatico"
            for p in ["gaming", "desenvolvimento", "economia"]:
                if p in comando:
                    perfil = p
                    break
                    
            resultado = await self.gerenciador_sistema.otimizar_sistema(perfil)
            return self._formatar_resultado_otimizacao(resultado)
            
        elif "hardware" in comando or "sistema" in comando:
            relatorio = self.gerenciador_sistema.gerar_relatorio()
            return self._formatar_relatorio_hardware(relatorio)
            
        return "Comando de sistema não reconhecido"
            
    def _formatar_resultado_otimizacao(self, resultado: Dict) -> str:
        """Formata o resultado da otimização do sistema"""
        if resultado["status"] == "erro":
            return f"Erro na otimização: {resultado['mensagem']}"
            
        texto = "=== Resultado da Otimização ===\n\n"
        
        alteracoes = resultado["alteracoes"]
        
        # BIOS
        if alteracoes["bios"]:
            texto += "Alterações na BIOS:\n"
            for chave, valor in alteracoes["bios"].items():
                texto += f"- {chave}: {valor}\n"
                
        # Windows
        if alteracoes["windows"]:
            texto += "\nAlterações no Windows:\n"
            for chave, valor in alteracoes["windows"].items():
                texto += f"- {chave}: {valor}\n"
                
        # Energia
        if alteracoes["energia"]["status"] == "sucesso":
            texto += "\nConfigurações de Energia:\n"
            texto += "- Perfil de alto desempenho ativado\n"
            texto += "- Timeouts ajustados\n"
            
        # Memória
        if alteracoes["memoria"]["status"] == "sucesso":
            texto += "\nOtimizações de Memória:\n"
            texto += "- Arquivo de paginação otimizado\n"
            
        # Armazenamento
        if alteracoes["armazenamento"]["status"] == "sucesso":
            texto += "\nOtimizações de Armazenamento:\n"
            texto += "- Indexação do Windows desativada\n"
            texto += "- Desfragmentação executada (se necessário)\n"
            
        return texto
            
    def _formatar_relatorio_hardware(self, relatorio: Dict) -> str:
        """Formata o relatório de hardware"""
        texto = "=== Relatório de Hardware ===\n\n"
        
        # CPU
        cpu = relatorio["hardware"]["processador"]
        texto += "Processador:\n"
        texto += f"- Modelo: {cpu['nome']}\n"
        texto += f"- Núcleos: {cpu['nucleos']} (Threads: {cpu['threads']})\n"
        texto += f"- Frequência Base: {cpu['frequencia_base']} MHz\n"
        texto += f"- Cache L3: {cpu['cache']} MB\n"
        texto += f"- Virtualização: {'Ativada' if cpu['virtualizacao'] else 'Desativada'}\n"
        
        # Memória
        memorias = relatorio["hardware"]["memoria"]
        texto += "\nMemória RAM:\n"
        for i, mem in enumerate(memorias, 1):
            texto += f"Módulo {i}:\n"
            texto += f"- Capacidade: {mem['capacidade'] / (1024**3):.1f} GB\n"
            texto += f"- Velocidade: {mem['velocidade']} MHz\n"
            texto += f"- Fabricante: {mem['fabricante']}\n"
            texto += f"- Slot: {mem['slot']}\n"
            
        # GPU
        gpus = relatorio["hardware"]["gpu"]
        texto += "\nPlacas de Vídeo:\n"
        for gpu in gpus:
            texto += f"- Modelo: {gpu['nome']}\n"
            if gpu['memoria']:
                texto += f"  * Memória: {gpu['memoria'] / (1024**3):.1f} GB\n"
            texto += f"  * Driver: {gpu['driver_versao']}\n"
            texto += f"  * Resolução: {gpu['resolucao']}\n"
            
        # Armazenamento
        discos = relatorio["hardware"]["armazenamento"]
        texto += "\nArmazenamento:\n"
        for disco in discos:
            texto += f"- {disco['modelo']}\n"
            texto += f"  * Tamanho: {int(disco['tamanho']) / (1024**3):.1f} GB\n"
            texto += f"  * Interface: {disco['interface']}\n"
            for particao in disco['particoes']:
                texto += f"  * Partição {particao['ponto_montagem']}:\n"
                texto += f"    - Total: {particao['total'] / (1024**3):.1f} GB\n"
                texto += f"    - Livre: {particao['livre'] / (1024**3):.1f} GB\n"
                
        # Temperaturas
        temps = relatorio["temperatura"]
        if not isinstance(temps, dict) or "erro" not in temps:
            texto += "\nTemperaturas:\n"
            for componente, temp in temps.items():
                texto += f"- {componente}: {temp}°C\n"
                
        return texto
            
    def _formatar_relatorio_seguranca(self, relatorio: Dict) -> str:
        """Formata o relatório de segurança para exibição"""
        texto = "=== Relatório de Segurança ===\n\n"
        
        # Recursos
        recursos = relatorio["metricas"].get("recursos", {})
        if recursos:
            texto += "Recursos do Sistema:\n"
            cpu = recursos.get("cpu", {})
            texto += f"- CPU: {cpu.get('uso', [0])[0]}% (Freq: {cpu.get('frequencia', 0)} MHz)\n"
            
            memoria = recursos.get("memoria", {})
            texto += f"- Memória: {memoria.get('percentual', 0)}% usado\n"
            
            for disco, info in recursos.get("discos", {}).items():
                texto += f"- Disco {disco}: {info.get('percentual', 0)}% usado\n"
            
        # Alertas
        if relatorio["alertas"]:
            texto += "\nÚltimos Alertas:\n"
            for alerta in relatorio["alertas"][-5:]:  # últimos 5 alertas
                texto += f"- {alerta['mensagem']} ({alerta['timestamp']})\n"
                
        # Processos Suspeitos
        if relatorio["processos_suspeitos"]:
            texto += "\nProcessos Suspeitos:\n"
            for processo in relatorio["processos_suspeitos"]:
                texto += f"- {processo}\n"
                
        # Conexões Suspeitas
        if relatorio["conexoes_suspeitas"]:
            texto += "\nConexões Suspeitas:\n"
            for conexao in relatorio["conexoes_suspeitas"]:
                texto += f"- {conexao}\n"
                
        return texto
        
    def _formatar_alertas(self, alertas: List[Dict]) -> str:
        """Formata a lista de alertas para exibição"""
        if not alertas:
            return "Não há alertas registrados"
            
        texto = "=== Últimos Alertas ===\n\n"
        for alerta in alertas:
            texto += f"[{alerta['timestamp']}] {alerta['tipo']}: {alerta['mensagem']}\n"
        return texto
        
    def _formatar_metricas_desempenho(self, metricas: Dict) -> str:
        """Formata as métricas de desempenho para exibição"""
        if not metricas:
            return "Não há métricas de desempenho disponíveis"
            
        texto = "=== Desempenho do Sistema ===\n\n"
        
        # CPU
        cpu = metricas.get("cpu", {})
        if cpu:
            texto += "CPU:\n"
            for i, uso in enumerate(cpu.get("uso", [])):
                texto += f"- Core {i}: {uso}%\n"
            if cpu.get("frequencia"):
                texto += f"- Frequência: {cpu['frequencia']} MHz\n"
                
        # Memória
        memoria = metricas.get("memoria", {})
        if memoria:
            texto += "\nMemória:\n"
            total_gb = memoria.get("total", 0) / (1024**3)
            disp_gb = memoria.get("disponivel", 0) / (1024**3)
            texto += f"- Total: {total_gb:.1f} GB\n"
            texto += f"- Disponível: {disp_gb:.1f} GB\n"
            texto += f"- Em uso: {memoria.get('percentual', 0)}%\n"
            texto += f"- Swap: {memoria.get('swap_usado', 0)}%\n"
            
        # Discos
        discos = metricas.get("discos", {})
        if discos:
            texto += "\nDiscos:\n"
            for disco, info in discos.items():
                total_gb = info.get("total", 0) / (1024**3)
                livre_gb = info.get("livre", 0) / (1024**3)
                texto += f"- {disco}:\n"
                texto += f"  * Total: {total_gb:.1f} GB\n"
                texto += f"  * Livre: {livre_gb:.1f} GB\n"
                texto += f"  * Em uso: {info.get('percentual', 0)}%\n"
                
        return texto
        
    def _identificar_modulos_necessarios(self, comando: str) -> List[str]:
        """Identifica quais módulos são necessários para processar o comando"""
        modulos = []
        
        # Sempre inclui o módulo NLP para processamento básico
        modulos.append("nlp")
        
        # Análise de palavras-chave para identificar módulos
        if any(palavra in comando.lower() for palavra in ["navegar", "site", "página"]):
            modulos.append("web")
            
        if any(palavra in comando.lower() for palavra in ["clicar", "digitar", "mouse"]):
            modulos.append("automacao")
            
        if any(palavra in comando.lower() for palavra in ["reconhecer", "detectar", "imagem"]):
            modulos.append("visao")
            
        if any(palavra in comando.lower() for palavra in ["programar", "código", "desenvolver"]):
            modulos.append("programacao")
            
        return modulos
        
    def _executar_comando(self, comando: str) -> str:
        """Executa o comando usando os módulos carregados"""
        # Aqui seria a lógica de execução do comando
        # usando os módulos carregados
        return "Comando executado com sucesso"
        
    def _otimizar_modulos_carregados(self):
        """Otimiza os módulos carregados descarregando os não essenciais"""
        modulos_ativos = list(self.modulos.keys())
        for modulo in modulos_ativos:
            if not self.modulos[modulo].sempre_ativo:
                self.descarregar_modulo(modulo)
                
    def descarregar_modulo(self, nome: str):
        """Descarrega um módulo da memória"""
        if nome in self.modulos:
            # Aqui seria a lógica de cleanup do módulo
            del self.modulos[nome]
            gc.collect()  # Força coleta de lixo
            
    def status(self) -> Dict[str, Any]:
        """Retorna o status atual do assistente"""
        status_base = {
            "memoria_uso": self.gerenciador.memoria_processo(),
            "modulos_ativos": list(self.modulos.keys()),
            "memoria_disponivel": self.gerenciador.memoria_disponivel()
        }
        
        # Adiciona informações de segurança
        status_base.update({
            "seguranca": {
                "alertas_ativos": len(self.monitor_seguranca.alertas),
                "processos_suspeitos": len(self.monitor_seguranca.processos_suspeitos),
                "conexoes_suspeitas": len(self.monitor_seguranca.conexoes_suspeitas)
            }
        })
        
        # Adiciona informações do sistema
        status_base.update({
            "sistema": self.gerenciador_sistema.gerar_relatorio()
        })
        
        return status_base
        
    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        if hasattr(self, 'monitor_seguranca'):
            self.monitor_seguranca.parar_monitoramento() 