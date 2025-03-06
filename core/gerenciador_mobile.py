import os
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ConfiguracaoMobile:
    android_sdk_path: str
    ios_sdk_path: str
    flutter_path: str
    react_native_path: str
    gradle_path: str
    xcode_path: str
    emuladores: Dict
    templates: Dict
    configuracoes_build: Dict
    recursos_padrao: Dict

class GerenciadorMobile:
    def __init__(self):
        self.config = self._carregar_configuracao()
        self.sistema = platform.system().lower()
        self.plataformas_disponiveis = self._verificar_plataformas()
        
    def _carregar_configuracao(self) -> ConfiguracaoMobile:
        """Carrega as configurações do arquivo JSON"""
        config_path = Path(__file__).parent.parent / 'config' / 'mobile_config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return ConfiguracaoMobile(**config_data)
    
    def _verificar_plataformas(self) -> Dict[str, bool]:
        """Verifica quais plataformas estão disponíveis para desenvolvimento"""
        status = {
            "android": self._verificar_android(),
            "ios": self._verificar_ios(),
            "flutter": self._verificar_flutter(),
            "react_native": self._verificar_react_native(),
            "gradle": self._verificar_gradle(),
            "xcode": self._verificar_xcode()
        }
        return status
    
    def _verificar_android(self) -> bool:
        """Verifica se o ambiente Android está configurado"""
        return (
            bool(self.config.android_sdk_path) and
            os.path.exists(self.config.android_sdk_path)
        )
    
    def _verificar_ios(self) -> bool:
        """Verifica se o ambiente iOS está configurado"""
        return (
            bool(self.config.ios_sdk_path) and
            os.path.exists(self.config.ios_sdk_path)
        )
    
    def _verificar_flutter(self) -> bool:
        """Verifica se o Flutter está instalado"""
        return (
            bool(self.config.flutter_path) and
            os.path.exists(self.config.flutter_path)
        )
    
    def _verificar_react_native(self) -> bool:
        """Verifica se o React Native está instalado"""
        return (
            bool(self.config.react_native_path) and
            os.path.exists(self.config.react_native_path)
        )
    
    def _verificar_gradle(self) -> bool:
        """Verifica se o Gradle está instalado"""
        try:
            subprocess.run(['gradle', '--version'], check=True, capture_output=True)
            return True
        except:
            return False
    
    def _verificar_xcode(self) -> bool:
        """Verifica se o Xcode está instalado"""
        if self.sistema == 'darwin':
            try:
                subprocess.run(['xcodebuild', '-version'], check=True, capture_output=True)
                return True
            except:
                return False
        return False
    
    def criar_projeto(self, nome: str, framework: str, template: str, caminho: str) -> bool:
        """Cria um novo projeto mobile usando o framework e template especificados"""
        caminho_completo = os.path.join(caminho, nome)
        
        if framework == 'flutter':
            cmd = ['flutter', 'create', '--org', 'com.exemplo', nome]
            if template in self.config.templates['flutter']:
                # Adiciona configurações específicas do template
                pass
        elif framework == 'react_native':
            cmd = ['npx', 'react-native', 'init', nome]
            if template in self.config.templates['react_native']:
                # Adiciona configurações específicas do template
                pass
        else:
            raise ValueError(f'Framework {framework} não suportado')
            
        try:
            subprocess.run(cmd, check=True, cwd=caminho)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def configurar_emulador(self, plataforma: str, nome: str) -> bool:
        """Configura um emulador para a plataforma especificada"""
        if plataforma == 'android':
            # Configura emulador Android
            try:
                cmd = [
                    os.path.join(self.config.android_sdk_path, 'tools', 'bin', 'avdmanager'),
                    'create', 'avd',
                    '--name', nome,
                    '--package', f'system-images;android-30;google_apis;x86_64'
                ]
                subprocess.run(cmd, check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        elif plataforma == 'ios' and self.sistema == 'darwin':
            # No iOS, usa o Simulator que já vem com o Xcode
            return True
        return False
    
    def iniciar_emulador(self, plataforma: str, nome: str) -> bool:
        """Inicia um emulador específico"""
        if plataforma == 'android':
            try:
                cmd = [
                    os.path.join(self.config.android_sdk_path, 'emulator', 'emulator'),
                    '-avd', nome
                ]
                subprocess.Popen(cmd)  # Executa em background
                return True
            except:
                return False
        elif plataforma == 'ios' and self.sistema == 'darwin':
            try:
                subprocess.Popen(['open', '-a', 'Simulator'])
                return True
            except:
                return False
        return False
    
    def compilar_projeto(self, caminho: str, plataforma: str, modo: str = 'debug') -> bool:
        """Compila o projeto para a plataforma especificada"""
        if not os.path.exists(caminho):
            return False
            
        # Detecta o tipo de projeto
        tem_flutter = os.path.exists(os.path.join(caminho, 'pubspec.yaml'))
        tem_react_native = os.path.exists(os.path.join(caminho, 'package.json'))
        
        try:
            if tem_flutter:
                if plataforma == 'android':
                    cmd = ['flutter', 'build', 'apk']
                    if modo == 'release':
                        cmd.append('--release')
                elif plataforma == 'ios' and self.sistema == 'darwin':
                    cmd = ['flutter', 'build', 'ios']
                    if modo == 'release':
                        cmd.append('--release')
                else:
                    return False
                    
            elif tem_react_native:
                if plataforma == 'android':
                    cmd = ['./gradlew', 'assembleRelease' if modo == 'release' else 'assembleDebug']
                elif plataforma == 'ios' and self.sistema == 'darwin':
                    cmd = ['xcodebuild', '-workspace', 'ios/*.xcworkspace', '-scheme', 'scheme_name', '-configuration', 'Release' if modo == 'release' else 'Debug']
                else:
                    return False
            else:
                return False
                
            subprocess.run(cmd, check=True, cwd=caminho)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def gerar_recursos(self, caminho: str, icone: str, splash: str) -> bool:
        """Gera ícones e splash screens para o projeto"""
        try:
            # Implementar geração de ícones e splash screens usando as configurações
            # definidas em self.config.recursos_padrao
            return True
        except:
            return False
    
    def atualizar_versao(self, caminho: str, versao: str, build: str) -> bool:
        """Atualiza a versão do aplicativo"""
        try:
            # Implementar atualização de versão nos arquivos de configuração
            # do Android (build.gradle) e iOS (Info.plist)
            return True
        except:
            return False
    
    def executar_testes(self, caminho: str) -> Dict[str, any]:
        """Executa os testes do projeto"""
        resultados = {
            'unitarios': False,
            'integracao': False,
            'ui': False,
            'cobertura': 0.0
        }
        
        try:
            # Detecta o tipo de projeto
            tem_flutter = os.path.exists(os.path.join(caminho, 'pubspec.yaml'))
            tem_react_native = os.path.exists(os.path.join(caminho, 'package.json'))
            
            if tem_flutter:
                # Executa testes Flutter
                subprocess.run(['flutter', 'test', '--coverage'], check=True, cwd=caminho)
                resultados['unitarios'] = True
                # Calcular cobertura
                
            elif tem_react_native:
                # Executa testes React Native
                subprocess.run(['npm', 'test', '--coverage'], check=True, cwd=caminho)
                resultados['unitarios'] = True
                # Calcular cobertura
                
            return resultados
        except:
            return resultados
    
    def publicar_app(self, caminho: str, plataforma: str, credenciais: Dict) -> bool:
        """Publica o aplicativo na loja correspondente"""
        try:
            if plataforma == 'android':
                # Implementar publicação na Google Play Store
                pass
            elif plataforma == 'ios' and self.sistema == 'darwin':
                # Implementar publicação na App Store
                pass
            return True
        except:
            return False 