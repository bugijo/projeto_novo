import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@dataclass
class RequisitosProjeto:
    tipo: str
    descricao: str
    elementos_visuais: Dict[str, Any] = None
    funcionalidades: List[str] = None
    cores: Dict[str, str] = None
    layout: Dict[str, Any] = None
    responsividade: bool = True
    acessibilidade: bool = True
    
    def __post_init__(self):
        if self.elementos_visuais is None:
            self.elementos_visuais = {}
        if self.funcionalidades is None:
            self.funcionalidades = []
        if self.cores is None:
            self.cores = {}
        if self.layout is None:
            self.layout = {}

class AssistenteProjetoInterativo:
    def __init__(self):
        self.perguntas_frontend = {
            "layout": [
                "Como você gostaria que fosse o layout geral do site?",
                "Prefere um design mais minimalista ou mais elaborado?",
                "Qual a disposição dos elementos principais (menu, conteúdo, rodapé)?",
                "O site deve ser responsivo para diferentes dispositivos?"
            ],
            "cores": [
                "Quais cores você gostaria de usar no site?",
                "Tem alguma paleta de cores específica em mente?",
                "Prefere cores mais vibrantes ou mais suaves?",
                "Qual a cor principal que representa melhor o tema do site?"
            ],
            "elementos": [
                "Quais elementos visuais você gostaria de incluir?",
                "Como você imagina a navegação entre as páginas?",
                "Gostaria de incluir algum elemento interativo específico?",
                "Que tipo de mídia (imagens, vídeos) você planeja usar?"
            ],
            "conteudo": [
                "Como você gostaria de organizar o conteúdo?",
                "Que tipo de informações serão mais importantes?",
                "Gostaria de recursos específicos para o conteúdo?",
                "Como você imagina a hierarquia da informação?"
            ]
        }
        
        self.perguntas_tecnicas = {
            "funcionalidades": [
                "Quais funcionalidades específicas o site deve ter?",
                "Precisa de algum tipo de interação com banco de dados?",
                "Haverá necessidade de autenticação de usuários?",
                "Precisa integrar com algum serviço externo?"
            ],
            "performance": [
                "Qual o nível de performance esperado?",
                "Existe expectativa de número de usuários simultâneos?",
                "Precisa de otimizações específicas para algum recurso?"
            ],
            "seguranca": [
                "Existem requisitos específicos de segurança?",
                "Será necessário implementar níveis de acesso?",
                "Como os dados sensíveis devem ser tratados?"
            ]
        }
        
        self.driver = None
        self.requisitos = None
        
    def iniciar_coleta_requisitos(self, tipo_projeto: str, descricao_inicial: str) -> RequisitosProjeto:
        """Inicia o processo de coleta de requisitos através de perguntas interativas"""
        print(f"\nÓtimo! Vou ajudar você a criar um {tipo_projeto}. Vou fazer algumas perguntas para entender melhor o que você precisa.")
        
        self.requisitos = RequisitosProjeto(tipo=tipo_projeto, descricao=descricao_inicial)
        
        # Coleta informações sobre frontend
        self._coletar_informacoes_frontend()
        
        # Coleta informações técnicas
        self._coletar_informacoes_tecnicas()
        
        # Valida se há lacunas nas informações
        self._validar_e_complementar_informacoes()
        
        return self.requisitos
    
    def _coletar_informacoes_frontend(self):
        """Coleta informações sobre o frontend através de perguntas interativas"""
        print("\nVamos falar sobre o design e aparência do site:")
        
        for categoria, perguntas in self.perguntas_frontend.items():
            print(f"\n{categoria.upper()}:")
            respostas = []
            for pergunta in perguntas:
                resposta = input(f"{pergunta}\nSua resposta: ").strip()
                if not resposta:
                    continue
                respostas.append(resposta)
                
                # Análise da resposta para gerar perguntas complementares
                perguntas_complementares = self._gerar_perguntas_complementares(categoria, resposta)
                for pergunta_comp in perguntas_complementares:
                    resposta_comp = input(f"{pergunta_comp}\nSua resposta: ").strip()
                    if resposta_comp:
                        respostas.append(resposta_comp)
            
            # Atualiza os requisitos com as respostas
            if categoria == "layout":
                self.requisitos.layout = self._processar_respostas_layout(respostas)
            elif categoria == "cores":
                self.requisitos.cores = self._processar_respostas_cores(respostas)
            elif categoria == "elementos":
                self.requisitos.elementos_visuais = self._processar_respostas_elementos(respostas)
    
    def _coletar_informacoes_tecnicas(self):
        """Coleta informações técnicas através de perguntas interativas"""
        print("\nAgora vamos falar sobre aspectos técnicos:")
        
        for categoria, perguntas in self.perguntas_tecnicas.items():
            print(f"\n{categoria.upper()}:")
            for pergunta in perguntas:
                resposta = input(f"{pergunta}\nSua resposta: ").strip()
                if not resposta:
                    continue
                
                if categoria == "funcionalidades":
                    self.requisitos.funcionalidades.append(resposta)
                
                # Gera perguntas complementares baseadas na resposta
                perguntas_complementares = self._gerar_perguntas_complementares(categoria, resposta)
                for pergunta_comp in perguntas_complementares:
                    resposta_comp = input(f"{pergunta_comp}\nSua resposta: ").strip()
                    if resposta_comp:
                        self.requisitos.funcionalidades.append(resposta_comp)
    
    def _gerar_perguntas_complementares(self, categoria: str, resposta: str) -> List[str]:
        """Gera perguntas complementares baseadas na resposta do usuário"""
        perguntas = []
        
        # Análise contextual da resposta
        palavras_chave = resposta.lower().split()
        
        if categoria == "layout":
            if "menu" in palavras_chave:
                perguntas.append("Como você gostaria que o menu se comportasse em dispositivos móveis?")
            if "responsivo" in palavras_chave:
                perguntas.append("Quais dispositivos são mais importantes para seu público?")
                
        elif categoria == "cores":
            if any(cor in palavras_chave for cor in ["claro", "escuro", "light", "dark"]):
                perguntas.append("Gostaria de implementar um alternador de tema claro/escuro?")
                
        elif categoria == "elementos":
            if "imagem" in palavras_chave or "imagens" in palavras_chave:
                perguntas.append("Gostaria de implementar uma galeria ou carrossel de imagens?")
            if "vídeo" in palavras_chave or "videos" in palavras_chave:
                perguntas.append("Os vídeos serão hospedados localmente ou em plataformas como YouTube?")
                
        elif categoria == "funcionalidades":
            if "login" in palavras_chave or "usuário" in palavras_chave:
                perguntas.append("Quais informações serão necessárias no cadastro de usuários?")
            if "busca" in palavras_chave:
                perguntas.append("Que tipos de filtros serão necessários na busca?")
        
        return perguntas
    
    def _validar_e_complementar_informacoes(self):
        """Valida se há lacunas nas informações e faz perguntas complementares"""
        lacunas = []
        
        # Verifica layout
        if not self.requisitos.layout:
            lacunas.append("Preciso de mais informações sobre o layout do site.")
        
        # Verifica cores
        if not self.requisitos.cores:
            lacunas.append("Não tenho informações suficientes sobre as cores do site.")
        
        # Verifica elementos visuais
        if not self.requisitos.elementos_visuais:
            lacunas.append("Preciso entender melhor quais elementos visuais você deseja.")
        
        # Verifica funcionalidades
        if not self.requisitos.funcionalidades:
            lacunas.append("Preciso saber mais sobre as funcionalidades necessárias.")
        
        # Solicita informações faltantes
        for lacuna in lacunas:
            print(f"\n{lacuna}")
            resposta = input("Pode me fornecer mais detalhes? ").strip()
            self._processar_resposta_lacuna(lacuna, resposta)
    
    def _processar_respostas_layout(self, respostas: List[str]) -> Dict[str, Any]:
        """Processa as respostas sobre layout"""
        layout = {
            "tipo": "responsivo" if any("responsiv" in r.lower() for r in respostas) else "fixo",
            "estilo": "minimalista" if any("minimal" in r.lower() for r in respostas) else "elaborado",
            "estrutura": {}
        }
        
        # Analisa estrutura do layout
        for resposta in respostas:
            if "menu" in resposta.lower():
                layout["estrutura"]["menu"] = resposta
            if "conteúdo" in resposta.lower() or "content" in resposta.lower():
                layout["estrutura"]["conteudo"] = resposta
            if "rodapé" in resposta.lower() or "footer" in resposta.lower():
                layout["estrutura"]["rodape"] = resposta
        
        return layout
    
    def _processar_respostas_cores(self, respostas: List[str]) -> Dict[str, str]:
        """Processa as respostas sobre cores"""
        cores = {}
        
        for resposta in respostas:
            resp_lower = resposta.lower()
            
            # Identifica cores mencionadas
            cores_basicas = ["azul", "vermelho", "verde", "amarelo", "roxo", "laranja", "preto", "branco"]
            for cor in cores_basicas:
                if cor in resp_lower:
                    cores[cor] = self._converter_cor_para_hex(cor)
            
            # Identifica tons
            if "claro" in resp_lower:
                cores["tom"] = "claro"
            elif "escuro" in resp_lower:
                cores["tom"] = "escuro"
            
            # Identifica esquema
            if "monocromático" in resp_lower:
                cores["esquema"] = "monocromatico"
            elif "complementar" in resp_lower:
                cores["esquema"] = "complementar"
        
        return cores
    
    def _processar_respostas_elementos(self, respostas: List[str]) -> Dict[str, Any]:
        """Processa as respostas sobre elementos visuais"""
        elementos = {
            "navegacao": {},
            "midia": {},
            "interacao": {}
        }
        
        for resposta in respostas:
            resp_lower = resposta.lower()
            
            # Elementos de navegação
            if "menu" in resp_lower:
                elementos["navegacao"]["menu"] = True
                if "hamburguer" in resp_lower:
                    elementos["navegacao"]["tipo"] = "hamburger"
                elif "lateral" in resp_lower:
                    elementos["navegacao"]["tipo"] = "sidebar"
                else:
                    elementos["navegacao"]["tipo"] = "top"
            
            # Elementos de mídia
            if "imagem" in resp_lower or "foto" in resp_lower:
                elementos["midia"]["imagens"] = True
                if "galeria" in resp_lower:
                    elementos["midia"]["galeria"] = True
                if "carrossel" in resp_lower or "slider" in resp_lower:
                    elementos["midia"]["carrossel"] = True
            
            if "vídeo" in resp_lower or "video" in resp_lower:
                elementos["midia"]["videos"] = True
                if "youtube" in resp_lower:
                    elementos["midia"]["plataforma"] = "youtube"
            
            # Elementos de interação
            if "formulário" in resp_lower or "form" in resp_lower:
                elementos["interacao"]["formularios"] = True
            if "botão" in resp_lower or "button" in resp_lower:
                elementos["interacao"]["botoes"] = True
            if "modal" in resp_lower or "popup" in resp_lower:
                elementos["interacao"]["modais"] = True
        
        return elementos
    
    def _processar_resposta_lacuna(self, lacuna: str, resposta: str):
        """Processa respostas para lacunas identificadas"""
        if "layout" in lacuna.lower():
            self.requisitos.layout.update(self._processar_respostas_layout([resposta]))
        elif "cor" in lacuna.lower():
            self.requisitos.cores.update(self._processar_respostas_cores([resposta]))
        elif "elementos visuais" in lacuna.lower():
            self.requisitos.elementos_visuais.update(self._processar_respostas_elementos([resposta]))
        elif "funcionalidades" in lacuna.lower():
            self.requisitos.funcionalidades.append(resposta)
    
    def _converter_cor_para_hex(self, cor: str) -> str:
        """Converte nome de cor para código hexadecimal"""
        cores = {
            "azul": "#007bff",
            "vermelho": "#dc3545",
            "verde": "#28a745",
            "amarelo": "#ffc107",
            "roxo": "#6f42c1",
            "laranja": "#fd7e14",
            "preto": "#000000",
            "branco": "#ffffff"
        }
        return cores.get(cor.lower(), "#000000")
    
    def iniciar_testes_automatizados(self, url: str):
        """Inicia os testes automatizados do site"""
        try:
            if not self.driver:
                self.driver = webdriver.Chrome()
            
            print("\nIniciando testes automatizados...")
            self.driver.get(url)
            
            # Testa responsividade
            self._testar_responsividade()
            
            # Testa navegação
            self._testar_navegacao()
            
            # Testa elementos visuais
            self._testar_elementos_visuais()
            
            # Testa funcionalidades
            self._testar_funcionalidades()
            
            print("\nTestes automatizados concluídos com sucesso!")
            
        except Exception as e:
            print(f"\nErro durante os testes: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _testar_responsividade(self):
        """Testa a responsividade do site"""
        tamanhos = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 812)     # Mobile
        ]
        
        for largura, altura in tamanhos:
            print(f"\nTestando resolução {largura}x{altura}")
            self.driver.set_window_size(largura, altura)
            time.sleep(2)  # Aguarda o redimensionamento
            
            # Verifica overflow horizontal
            overflow = self.driver.execute_script(
                "return document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            if overflow:
                print(f"Alerta: Detectado overflow horizontal em {largura}x{altura}")
    
    def _testar_navegacao(self):
        """Testa a navegação do site"""
        print("\nTestando navegação...")
        
        # Encontra todos os links
        links = self.driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                if link.is_displayed() and link.is_enabled():
                    href = link.get_attribute("href")
                    if href and not href.startswith("javascript"):
                        print(f"Testando link: {href}")
                        link.click()
                        time.sleep(2)
                        self.driver.back()
            except Exception as e:
                print(f"Erro ao testar link: {str(e)}")
    
    def _testar_elementos_visuais(self):
        """Testa os elementos visuais do site"""
        print("\nTestando elementos visuais...")
        
        # Testa imagens
        imagens = self.driver.find_elements(By.TAG_NAME, "img")
        for img in imagens:
            if img.is_displayed():
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if not alt:
                    print(f"Alerta: Imagem sem atributo alt: {src}")
        
        # Testa vídeos
        videos = self.driver.find_elements(By.TAG_NAME, "video")
        for video in videos:
            if video.is_displayed():
                if not video.get_attribute("controls"):
                    print("Alerta: Vídeo sem controles")
    
    def _testar_funcionalidades(self):
        """Testa as funcionalidades do site"""
        print("\nTestando funcionalidades...")
        
        # Testa formulários
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        for form in forms:
            if form.is_displayed():
                inputs = form.find_elements(By.TAG_NAME, "input")
                for input_elem in inputs:
                    if input_elem.is_displayed() and input_elem.is_enabled():
                        tipo = input_elem.get_attribute("type")
                        if tipo == "text":
                            input_elem.send_keys("Teste")
                        elif tipo == "email":
                            input_elem.send_keys("teste@teste.com")
                        elif tipo == "number":
                            input_elem.send_keys("123")
                
                # Limpa os campos após o teste
                for input_elem in inputs:
                    if input_elem.is_displayed() and input_elem.is_enabled():
                        input_elem.clear()
    
    def simular_interacao_usuario(self):
        """Simula interações de usuário usando PyAutoGUI"""
        print("\nSimulando interações de usuário...")
        
        # Configuração de segurança do PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1
        
        try:
            # Simula movimento do mouse
            print("Movendo mouse pela página...")
            screen_width, screen_height = pyautogui.size()
            
            # Move para diferentes áreas da página
            pontos = [
                (screen_width // 4, screen_height // 4),
                (screen_width // 4 * 3, screen_height // 4),
                (screen_width // 2, screen_height // 2),
                (screen_width // 4, screen_height // 4 * 3),
                (screen_width // 4 * 3, screen_height // 4 * 3)
            ]
            
            for x, y in pontos:
                pyautogui.moveTo(x, y, duration=0.5)
                time.sleep(0.5)
            
            # Simula rolagem
            print("Testando rolagem...")
            pyautogui.scroll(-500)  # Rola para baixo
            time.sleep(1)
            pyautogui.scroll(500)   # Rola para cima
            
            # Simula cliques
            print("Testando cliques...")
            elementos_clicaveis = pyautogui.locateAllOnScreen("botoes.png")
            for elem in elementos_clicaveis:
                pyautogui.click(elem)
                time.sleep(0.5)
            
        except Exception as e:
            print(f"Erro durante a simulação: {str(e)}")
        
        print("Simulação de interação concluída!") 