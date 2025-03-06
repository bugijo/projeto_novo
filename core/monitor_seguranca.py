import psutil
import platform
import subprocess
import threading
import time
import logging
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MonitorSeguranca:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executando = False
        self.threads = []
        self.alertas = []
        self.metricas = {}
        self.processos_suspeitos = set()
        self.conexoes_suspeitas = set()
        
    def iniciar_monitoramento(self):
        """Inicia todas as threads de monitoramento"""
        self.executando = True
        
        # Thread de monitoramento de recursos
        thread_recursos = threading.Thread(target=self._monitorar_recursos)
        thread_recursos.daemon = True
        self.threads.append(thread_recursos)
        
        # Thread de monitoramento de processos
        thread_processos = threading.Thread(target=self._monitorar_processos)
        thread_processos.daemon = True
        self.threads.append(thread_processos)
        
        # Thread de monitoramento de rede
        thread_rede = threading.Thread(target=self._monitorar_rede)
        thread_rede.daemon = True
        self.threads.append(thread_rede)
        
        # Thread de verificação de segurança
        thread_seguranca = threading.Thread(target=self._verificar_seguranca)
        thread_seguranca.daemon = True
        self.threads.append(thread_seguranca)
        
        # Inicia todas as threads
        for thread in self.threads:
            thread.start()
            
        self.logger.info("Monitoramento de segurança iniciado")
        
    def parar_monitoramento(self):
        """Para todas as threads de monitoramento"""
        self.executando = False
        for thread in self.threads:
            thread.join()
        self.logger.info("Monitoramento de segurança parado")
        
    def _monitorar_recursos(self):
        """Monitora uso de CPU, memória e disco"""
        while self.executando:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
                cpu_freq = psutil.cpu_freq()
                
                # Memória
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                # Disco
                discos = psutil.disk_partitions()
                uso_discos = {}
                for disco in discos:
                    try:
                        uso = psutil.disk_usage(disco.mountpoint)
                        uso_discos[disco.mountpoint] = {
                            "total": uso.total,
                            "usado": uso.used,
                            "livre": uso.free,
                            "percentual": uso.percent
                        }
                    except Exception:
                        continue
                
                self.metricas["recursos"] = {
                    "cpu": {
                        "uso": cpu_percent,
                        "frequencia": cpu_freq.current if cpu_freq else None
                    },
                    "memoria": {
                        "total": mem.total,
                        "disponivel": mem.available,
                        "percentual": mem.percent,
                        "swap_usado": swap.percent
                    },
                    "discos": uso_discos
                }
                
                # Verifica uso excessivo
                self._verificar_uso_excessivo()
                
            except Exception as e:
                self.logger.error(f"Erro ao monitorar recursos: {e}")
                
            time.sleep(5)  # Intervalo de 5 segundos
            
    def _monitorar_processos(self):
        """Monitora processos em execução"""
        while self.executando:
            try:
                processos = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                               'memory_percent', 'status']):
                    try:
                        info = proc.info
                        # Verifica comportamento suspeito
                        if (info['cpu_percent'] > 80 or 
                            info['memory_percent'] > 80):
                            self.processos_suspeitos.add(info['name'])
                            self._registrar_alerta(
                                "processo_suspeito",
                                f"Processo {info['name']} com uso elevado de recursos"
                            )
                        processos.append(info)
                    except Exception:
                        continue
                        
                self.metricas["processos"] = processos
                
            except Exception as e:
                self.logger.error(f"Erro ao monitorar processos: {e}")
                
            time.sleep(10)  # Intervalo de 10 segundos
            
    def _monitorar_rede(self):
        """Monitora conexões de rede"""
        while self.executando:
            try:
                conexoes = []
                for conn in psutil.net_connections():
                    try:
                        if conn.status == 'ESTABLISHED':
                            # Verifica conexões suspeitas
                            if self._verificar_conexao_suspeita(conn):
                                self.conexoes_suspeitas.add(
                                    f"{conn.laddr.ip}:{conn.laddr.port} -> "
                                    f"{conn.raddr.ip}:{conn.raddr.port}"
                                )
                                self._registrar_alerta(
                                    "conexao_suspeita",
                                    f"Conexão suspeita detectada: {conn.laddr.ip} -> {conn.raddr.ip}"
                                )
                            conexoes.append({
                                "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                                "remoto": f"{conn.raddr.ip}:{conn.raddr.port}",
                                "status": conn.status,
                                "pid": conn.pid
                            })
                    except Exception:
                        continue
                        
                self.metricas["rede"] = {
                    "conexoes": conexoes,
                    "bytes_enviados": psutil.net_io_counters().bytes_sent,
                    "bytes_recebidos": psutil.net_io_counters().bytes_recv
                }
                
            except Exception as e:
                self.logger.error(f"Erro ao monitorar rede: {e}")
                
            time.sleep(15)  # Intervalo de 15 segundos
            
    def _verificar_seguranca(self):
        """Verifica aspectos de segurança do sistema"""
        while self.executando:
            try:
                # Verifica atualizações do sistema
                self._verificar_atualizacoes()
                
                # Verifica firewall
                self._verificar_firewall()
                
                # Verifica antivírus
                self._verificar_antivirus()
                
                # Verifica portas abertas
                self._verificar_portas()
                
                # Verifica permissões de arquivos
                self._verificar_permissoes()
                
            except Exception as e:
                self.logger.error(f"Erro ao verificar segurança: {e}")
                
            time.sleep(3600)  # Verifica a cada hora
            
    def _verificar_uso_excessivo(self):
        """Verifica uso excessivo de recursos"""
        recursos = self.metricas.get("recursos", {})
        
        # Verifica CPU
        cpu = recursos.get("cpu", {})
        if any(uso > 90 for uso in cpu.get("uso", [])):
            self._registrar_alerta(
                "cpu_alta",
                "Uso de CPU acima de 90%"
            )
            
        # Verifica Memória
        memoria = recursos.get("memoria", {})
        if memoria.get("percentual", 0) > 90:
            self._registrar_alerta(
                "memoria_alta",
                "Uso de memória acima de 90%"
            )
            
        # Verifica Disco
        discos = recursos.get("discos", {})
        for disco, info in discos.items():
            if info.get("percentual", 0) > 90:
                self._registrar_alerta(
                    "disco_cheio",
                    f"Disco {disco} com mais de 90% de uso"
                )
                
    def _verificar_conexao_suspeita(self, conexao) -> bool:
        """Verifica se uma conexão é suspeita"""
        try:
            # Lista de portas comumente usadas por malware
            portas_suspeitas = {22, 23, 25, 3389, 4444, 5900}
            
            # Verifica se a porta remota é suspeita
            if conexao.raddr and conexao.raddr.port in portas_suspeitas:
                return True
                
            # Verifica IP em lista negra (exemplo)
            if conexao.raddr:
                response = requests.get(
                    f"https://api.abuseipdb.com/api/v2/check?ipAddress={conexao.raddr.ip}",
                    headers={"Key": "SEU_API_KEY"}  # Necessário configurar
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data", {}).get("abuseConfidenceScore", 0) > 80:
                        return True
                        
        except Exception as e:
            self.logger.error(f"Erro ao verificar conexão suspeita: {e}")
            
        return False
        
    def _verificar_atualizacoes(self):
        """Verifica atualizações pendentes do sistema"""
        try:
            if platform.system() == "Windows":
                # Verifica atualizações do Windows usando PowerShell
                cmd = "powershell Get-WUList"
                resultado = subprocess.run(cmd, capture_output=True, text=True)
                if "KB" in resultado.stdout:
                    self._registrar_alerta(
                        "atualizacoes_pendentes",
                        "Existem atualizações do Windows pendentes"
                    )
            else:
                # Para sistemas Linux
                cmd = "apt list --upgradable"
                resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if "upgradable" in resultado.stdout:
                    self._registrar_alerta(
                        "atualizacoes_pendentes",
                        "Existem atualizações do sistema pendentes"
                    )
        except Exception as e:
            self.logger.error(f"Erro ao verificar atualizações: {e}")
            
    def _verificar_firewall(self):
        """Verifica status do firewall"""
        try:
            if platform.system() == "Windows":
                cmd = "netsh advfirewall show allprofiles"
                resultado = subprocess.run(cmd, capture_output=True, text=True)
                if "OFF" in resultado.stdout:
                    self._registrar_alerta(
                        "firewall_desativado",
                        "Firewall do Windows está desativado"
                    )
        except Exception as e:
            self.logger.error(f"Erro ao verificar firewall: {e}")
            
    def _verificar_antivirus(self):
        """Verifica status do antivírus"""
        try:
            if platform.system() == "Windows":
                cmd = "powershell Get-MpComputerStatus"
                resultado = subprocess.run(cmd, capture_output=True, text=True)
                if "False" in resultado.stdout:
                    self._registrar_alerta(
                        "antivirus_desativado",
                        "Windows Defender está desativado"
                    )
        except Exception as e:
            self.logger.error(f"Erro ao verificar antivírus: {e}")
            
    def _verificar_portas(self):
        """Verifica portas abertas"""
        try:
            for conn in psutil.net_connections():
                if conn.status == "LISTEN":
                    # Lista de portas que não deveriam estar abertas
                    portas_perigosas = {21, 23, 445, 3389}
                    if conn.laddr.port in portas_perigosas:
                        self._registrar_alerta(
                            "porta_perigosa",
                            f"Porta perigosa aberta: {conn.laddr.port}"
                        )
        except Exception as e:
            self.logger.error(f"Erro ao verificar portas: {e}")
            
    def _verificar_permissoes(self):
        """Verifica permissões de arquivos sensíveis"""
        diretorios_sensiveis = [
            Path.home(),
            Path.home() / "Documents",
            Path.home() / "Downloads"
        ]
        
        try:
            for diretorio in diretorios_sensiveis:
                if diretorio.exists():
                    for arquivo in diretorio.glob("**/*"):
                        try:
                            if arquivo.is_file():
                                # Verifica permissões muito abertas
                                if arquivo.stat().st_mode & 0o777 == 0o777:
                                    self._registrar_alerta(
                                        "permissao_insegura",
                                        f"Arquivo com permissões inseguras: {arquivo}"
                                    )
                        except Exception:
                            continue
        except Exception as e:
            self.logger.error(f"Erro ao verificar permissões: {e}")
            
    def _registrar_alerta(self, tipo: str, mensagem: str):
        """Registra um novo alerta"""
        alerta = {
            "tipo": tipo,
            "mensagem": mensagem,
            "timestamp": datetime.now().isoformat()
        }
        self.alertas.append(alerta)
        self.logger.warning(f"Alerta de segurança: {mensagem}")
        
    def obter_relatorio(self) -> Dict:
        """Retorna um relatório completo do estado do sistema"""
        return {
            "metricas": self.metricas,
            "alertas": self.alertas[-50:],  # últimos 50 alertas
            "processos_suspeitos": list(self.processos_suspeitos),
            "conexoes_suspeitas": list(self.conexoes_suspeitas),
            "timestamp": datetime.now().isoformat()
        }
        
    def limpar_alertas(self):
        """Limpa a lista de alertas"""
        self.alertas.clear()
        self.processos_suspeitos.clear()
        self.conexoes_suspeitas.clear()
        
    def __del__(self):
        """Garante que todas as threads sejam encerradas"""
        self.parar_monitoramento() 