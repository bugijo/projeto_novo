import wmi
import subprocess
import psutil
import winreg
from typing import Dict, List, Optional, Union
import logging
from pathlib import Path
import json
import requests
from dataclasses import dataclass
import ctypes
import sys

@dataclass
class ConfiguracaoBIOS:
    fabricante: str
    modelo: str
    versao: str
    configuracoes: Dict[str, any]
    perfis_otimizacao: Dict[str, Dict[str, any]]

class GerenciadorSistemaAvancado:
    def __init__(self):
        self.wmi = wmi.WMI()
        self.logger = logging.getLogger(__name__)
        self.deepseek_api_key = self._carregar_api_key()
        self._carregar_configuracoes()
        self.tem_admin = self._verificar_admin()

    def _carregar_api_key(self) -> str:
        """Carrega as chaves de API do arquivo de configuração"""
        try:
            with open("config/api_keys.json", "r") as f:
                keys = json.load(f)
                if not keys["deepseek_api_key"]:
                    print("\nAtenção: Chave API do Deepseek não configurada!")
                    print("Por favor, obtenha sua chave em https://deepseek.ai")
                    print("E adicione no arquivo config/api_keys.json")
                return keys["deepseek_api_key"]
        except Exception as e:
            print(f"\nErro ao carregar chaves API: {e}")
            print("Verifique se o arquivo config/api_keys.json existe e está correto")
            return ""

    def verificar_apis(self) -> Dict[str, bool]:
        """Verifica o status de todas as APIs necessárias"""
        try:
            with open("config/api_keys.json", "r") as f:
                keys = json.load(f)
            
            status = {
                "deepseek": bool(keys.get("deepseek_api_key")),
                "virustotal": bool(keys.get("virustotal_api_key")),
                "abuseipdb": bool(keys.get("abuseipdb_api_key"))
            }

            if not all(status.values()):
                print("\nAlgumas chaves API estão faltando:")
                if not status["deepseek"]:
                    print("- Deepseek: https://deepseek.ai")
                if not status["virustotal"]:
                    print("- VirusTotal: https://www.virustotal.com")
                if not status["abuseipdb"]:
                    print("- AbuseIPDB: https://www.abuseipdb.com")
                print("\nAdicione as chaves no arquivo config/api_keys.json")

            return status
        except Exception as e:
            print(f"\nErro ao verificar APIs: {e}")
            return {"erro": str(e)}

    def _carregar_configuracoes(self):
        """Carrega configurações do sistema"""
        self.info_sistema = {
            "processador": self._obter_info_cpu(),
            "memoria": self._obter_info_memoria(),
            "placa_mae": self._obter_info_placa_mae(),
            "gpu": self._obter_info_gpu(),
            "armazenamento": self._obter_info_armazenamento()
        }

    def _obter_info_cpu(self) -> Dict:
        """Obtém informações detalhadas do processador"""
        cpu = self.wmi.Win32_Processor()[0]
        return {
            "nome": cpu.Name,
            "nucleos": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "frequencia_base": cpu.MaxClockSpeed,
            "cache": cpu.L3CacheSize,
            "virtualizacao": cpu.VirtualizationFirmwareEnabled
        }

    def _obter_info_memoria(self) -> Dict:
        """Obtém informações detalhadas da memória"""
        memorias = self.wmi.Win32_PhysicalMemory()
        return [{
            "capacidade": mem.Capacity,
            "velocidade": mem.Speed,
            "fabricante": mem.Manufacturer,
            "tipo": mem.MemoryType,
            "slot": mem.DeviceLocator
        } for mem in memorias]

    def _obter_info_placa_mae(self) -> Dict:
        """Obtém informações da placa-mãe"""
        placa = self.wmi.Win32_BaseBoard()[0]
        bios = self.wmi.Win32_BIOS()[0]
        return {
            "fabricante": placa.Manufacturer,
            "modelo": placa.Product,
            "versao_bios": bios.Version,
            "data_bios": bios.ReleaseDate
        }

    def _obter_info_gpu(self) -> List[Dict]:
        """Obtém informações das GPUs"""
        gpus = self.wmi.Win32_VideoController()
        return [{
            "nome": gpu.Name,
            "memoria": gpu.AdapterRAM if gpu.AdapterRAM else 0,
            "driver_versao": gpu.DriverVersion,
            "resolucao": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}"
        } for gpu in gpus]

    def _obter_info_armazenamento(self) -> List[Dict]:
        """Obtém informações dos dispositivos de armazenamento"""
        discos = self.wmi.Win32_DiskDrive()
        return [{
            "modelo": disco.Model,
            "tamanho": disco.Size,
            "interface": disco.InterfaceType,
            "particoes": self._obter_particoes(disco.DeviceID)
        } for disco in discos]

    def _obter_particoes(self, disco_id: str) -> List[Dict]:
        """Obtém informações das partições de um disco"""
        particoes = []
        for particao in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(particao.mountpoint)
                particoes.append({
                    "ponto_montagem": particao.mountpoint,
                    "sistema_arquivos": particao.fstype,
                    "total": uso.total,
                    "usado": uso.used,
                    "livre": uso.free
                })
            except:
                continue
        return particoes

    def _verificar_admin(self) -> bool:
        """Verifica se o programa está rodando como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def solicitar_admin(self) -> bool:
        """Solicita privilégios de administrador se necessário"""
        if not self.tem_admin:
            try:
                if sys.platform == 'win32':
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, " ".join(sys.argv), None, 1
                    )
                    return True
                else:
                    print("Por favor, execute o programa como administrador (sudo)")
                    return False
            except Exception as e:
                print(f"Erro ao solicitar privilégios de administrador: {e}")
                return False
        return True

    async def otimizar_sistema(self, perfil: str = "automatico") -> Dict[str, any]:
        """Otimiza o sistema com base no perfil selecionado"""
        if not self.tem_admin and not self.solicitar_admin():
            return {"erro": "Privilégios de administrador necessários para otimização"}
        try:
            # Consulta o Deepseek para recomendações
            recomendacoes = await self._consultar_deepseek_otimizacao(perfil)
            
            resultados = {
                "bios": await self._otimizar_bios(recomendacoes.get("bios", {})),
                "windows": self._otimizar_windows(recomendacoes.get("windows", {})),
                "energia": self._configurar_energia(recomendacoes.get("energia", {})),
                "memoria": self._otimizar_memoria(recomendacoes.get("memoria", {})),
                "armazenamento": self._otimizar_armazenamento(recomendacoes.get("armazenamento", {}))
            }
            
            return {
                "status": "sucesso",
                "alteracoes": resultados
            }
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
            return {"status": "erro", "mensagem": str(e)}

    async def _consultar_deepseek_otimizacao(self, perfil: str) -> Dict:
        """Consulta o Deepseek para recomendações de otimização"""
        if not self.deepseek_api_key:
            raise ValueError("Chave API do Deepseek não configurada")

        prompt = self._gerar_prompt_otimizacao(perfil)
        
        # Aqui você implementaria a chamada real à API do Deepseek
        # Por enquanto, retornamos recomendações básicas
        return {
            "bios": {
                "virtualizacao": True,
                "xmp": True,
                "performance_mode": True
            },
            "windows": {
                "servicos": ["superfetch", "sysmain"],
                "startup": ["desnecessarios"],
                "atualizacoes": "otimizado"
            },
            "energia": {
                "perfil": "alto_desempenho",
                "timeout_disco": 0,
                "timeout_monitor": 15
            }
        }

    def _gerar_prompt_otimizacao(self, perfil: str) -> str:
        """Gera o prompt para o Deepseek baseado no perfil e hardware"""
        return f"""
        Analise o seguinte sistema e sugira otimizações para o perfil '{perfil}':
        
        CPU: {self.info_sistema['processador']['nome']}
        RAM: {self.info_sistema['memoria']}
        GPU: {self.info_sistema['gpu']}
        Placa-mãe: {self.info_sistema['placa_mae']['modelo']}
        
        Considere:
        1. Configurações de BIOS seguras
        2. Otimizações do Windows
        3. Gerenciamento de energia
        4. Configurações de memória
        5. Otimizações de armazenamento
        """

    async def _otimizar_bios(self, recomendacoes: Dict) -> Dict:
        """Aplica otimizações na BIOS através de ferramentas do fabricante"""
        # Implementação depende do fabricante da placa-mãe
        # Retorna as alterações realizadas
        return {"status": "não implementado"}

    def _otimizar_windows(self, recomendacoes: Dict) -> Dict:
        """Aplica otimizações no Windows"""
        alteracoes = {}
        
        # Otimiza serviços
        for servico in recomendacoes.get("servicos", []):
            try:
                subprocess.run(["sc", "config", servico, "start=disabled"])
                alteracoes[f"servico_{servico}"] = "desativado"
            except:
                alteracoes[f"servico_{servico}"] = "erro"

        # Otimiza registro
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management", 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 1)
                alteracoes["large_system_cache"] = "ativado"
        except:
            alteracoes["large_system_cache"] = "erro"

        return alteracoes

    def _configurar_energia(self, recomendacoes: Dict) -> Dict:
        """Configura as opções de energia do Windows"""
        try:
            # Ativa o perfil de alto desempenho
            subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
            
            # Configura timeouts
            subprocess.run(["powercfg", "/change", "monitor-timeout-ac", str(recomendacoes.get("timeout_monitor", 15))])
            subprocess.run(["powercfg", "/change", "disk-timeout-ac", str(recomendacoes.get("timeout_disco", 0))])
            
            return {"status": "sucesso"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}

    def _otimizar_memoria(self, recomendacoes: Dict) -> Dict:
        """Otimiza configurações de memória"""
        try:
            # Ajusta arquivo de paginação
            subprocess.run(["wmic", "computersystem", "where", "name='%computername%'", 
                          "set", "AutomaticManagedPagefile=False"])
            
            # Configura tamanho do arquivo de paginação
            memoria_total = psutil.virtual_memory().total
            tamanho_pagefile = int(memoria_total * 1.5)
            
            subprocess.run(["wmic", "pagefileset", "where", "name='C:\\\\pagefile.sys'", 
                          "set", f"InitialSize={tamanho_pagefile},MaximumSize={tamanho_pagefile}"])
            
            return {"status": "sucesso"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}

    def _otimizar_armazenamento(self, recomendacoes: Dict) -> Dict:
        """Otimiza configurações de armazenamento"""
        try:
            # Desativa indexação
            subprocess.run(["sc", "config", "WSearch", "start=disabled"])
            subprocess.run(["net", "stop", "WSearch"])
            
            # Executa desfragmentação (para HDDs)
            for disco in self._obter_info_armazenamento():
                if disco["interface"] == "IDE":  # HDD
                    subprocess.run(["defrag", "/C", "/H", "/M"])
            
            return {"status": "sucesso"}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}

    def gerar_relatorio(self) -> Dict:
        """Gera um relatório completo do sistema"""
        return {
            "hardware": {
                "cpu": self._obter_info_cpu(),
                "memoria": self._obter_info_memoria(),
                "placa_mae": self._obter_info_placa_mae(),
                "gpu": self._obter_info_gpu(),
                "armazenamento": self._obter_info_armazenamento()
            },
            "temperaturas": self._obter_temperaturas(),
            "energia": self._obter_status_energia(),
            "desempenho": {
                "cpu_uso": psutil.cpu_percent(interval=1),
                "memoria_uso": psutil.virtual_memory().percent,
                "disco_uso": psutil.disk_usage('/').percent
            },
            "seguranca": {
                "admin": self.tem_admin,
                "atualizacoes_pendentes": self._verificar_atualizacoes_pendentes(),
                "firewall_ativo": self._verificar_firewall_ativo(),
                "antivirus_ativo": self._verificar_antivirus_ativo()
            }
        }

    def _verificar_atualizacoes_pendentes(self) -> bool:
        """Verifica se existem atualizações pendentes"""
        try:
            resultado = subprocess.run(
                ["powershell", "Get-WUList"], 
                capture_output=True, 
                text=True
            )
            return "Updates are available" in resultado.stdout
        except:
            return False

    def _verificar_firewall_ativo(self) -> bool:
        """Verifica se o firewall está ativo"""
        try:
            resultado = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles"], 
                capture_output=True, 
                text=True
            )
            return "State                                 ON" in resultado.stdout
        except:
            return False

    def _verificar_antivirus_ativo(self) -> bool:
        """Verifica se existe antivírus ativo"""
        try:
            av_produtos = self.wmi.Win32_Product(Name='Windows Defender')
            return len(av_produtos) > 0 and av_produtos[0].Status == 'OK'
        except:
            return False

    def _obter_temperaturas(self) -> Dict[str, float]:
        """Obtém temperaturas dos componentes"""
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensores = w.Sensor()
            temps = {}
            for sensor in sensores:
                if sensor.SensorType == 'Temperature':
                    temps[sensor.Name] = sensor.Value
            return temps
        except:
            return {"erro": "OpenHardwareMonitor não encontrado"}

    def _obter_status_energia(self) -> Dict:
        """Obtém informações sobre energia do sistema"""
        try:
            bateria = psutil.sensors_battery()
            if bateria:
                return {
                    "conectado": bateria.power_plugged,
                    "porcentagem": bateria.percent,
                    "tempo_restante": bateria.secsleft
                }
            return {"conectado": True}  # Desktop
        except:
            return {"erro": "Não foi possível obter informações de energia"} 