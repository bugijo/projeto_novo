from typing import List, Dict, Optional
import json
from pathlib import Path

class SeletorLinguagem:
    def __init__(self):
        self.criterios = {
            "web": {
                "frontend": ["javascript", "typescript", "html", "css"],
                "backend": ["python", "nodejs", "java", "php"]
            },
            "desktop": {
                "interface": ["python", "java", "cpp"],
                "jogos": ["cpp", "python", "java"],
                "automacao": ["python", "javascript"]
            },
            "mobile": {
                "android": ["kotlin", "java"],
                "ios": ["swift"],
                "hibrido": ["javascript", "dart"]
            },
            "dados": {
                "analise": ["python", "r"],
                "bigdata": ["python", "scala", "java"],
                "ml": ["python", "r"]
            },
            "sistemas": {
                "baixo_nivel": ["cpp", "rust", "c"],
                "scripts": ["python", "bash", "powershell"],
                "servicos": ["java", "cpp", "rust"]
            }
        }
        
        self.caracteristicas_linguagens = {
            "python": {
                "facilidade": 9,
                "performance": 6,
                "ecosystem": 9,
                "multiplataforma": 9,
                "gui": 7,
                "web": 8,
                "dados": 10
            },
            "javascript": {
                "facilidade": 8,
                "performance": 7,
                "ecosystem": 9,
                "multiplataforma": 9,
                "gui": 8,
                "web": 10,
                "dados": 7
            },
            "java": {
                "facilidade": 6,
                "performance": 8,
                "ecosystem": 9,
                "multiplataforma": 9,
                "gui": 8,
                "web": 8,
                "dados": 7
            },
            "cpp": {
                "facilidade": 5,
                "performance": 10,
                "ecosystem": 8,
                "multiplataforma": 8,
                "gui": 7,
                "web": 5,
                "dados": 6
            }
        }

    def analisar_requisitos(self, descricao: str) -> Dict[str, float]:
        """Analisa a descrição do projeto e retorna pontuações para cada aspecto"""
        pontuacoes = {
            "facilidade": 0.0,
            "performance": 0.0,
            "ecosystem": 0.0,
            "multiplataforma": 0.0,
            "gui": 0.0,
            "web": 0.0,
            "dados": 0.0
        }
        
        # Análise de palavras-chave
        if "iniciante" in descricao.lower() or "básico" in descricao.lower():
            pontuacoes["facilidade"] = 1.0
            
        if "rápido" in descricao.lower() or "performance" in descricao.lower():
            pontuacoes["performance"] = 1.0
            
        if "interface" in descricao.lower() or "gui" in descricao.lower():
            pontuacoes["gui"] = 1.0
            
        if "web" in descricao.lower() or "site" in descricao.lower():
            pontuacoes["web"] = 1.0
            
        if "dados" in descricao.lower() or "análise" in descricao.lower():
            pontuacoes["dados"] = 1.0
            
        if "multiplataforma" in descricao.lower():
            pontuacoes["multiplataforma"] = 1.0
            
        return pontuacoes

    def sugerir_linguagem(self, descricao: str) -> List[Dict[str, any]]:
        """Sugere as melhores linguagens para o projeto baseado na descrição"""
        requisitos = self.analisar_requisitos(descricao)
        pontuacoes = {}
        
        # Calcula pontuação para cada linguagem
        for linguagem, caracteristicas in self.caracteristicas_linguagens.items():
            pontuacao = 0
            for aspecto, peso in requisitos.items():
                if peso > 0:
                    pontuacao += caracteristicas[aspecto] * peso
            
            if pontuacao > 0:
                pontuacoes[linguagem] = pontuacao
        
        # Ordena linguagens por pontuação
        linguagens_ordenadas = sorted(
            [{"linguagem": k, "pontuacao": v} for k, v in pontuacoes.items()],
            key=lambda x: x["pontuacao"],
            reverse=True
        )
        
        return linguagens_ordenadas[:3]  # Retorna as 3 melhores opções

    def obter_frameworks(self, linguagem: str, tipo_projeto: str) -> List[str]:
        """Retorna frameworks recomendados para a linguagem e tipo de projeto"""
        frameworks = {
            "python": {
                "web": ["Django", "Flask", "FastAPI"],
                "gui": ["PyQt", "Tkinter", "wxPython"],
                "dados": ["Pandas", "NumPy", "Scikit-learn"],
                "automacao": ["Selenium", "Pyautogui", "Requests"]
            },
            "javascript": {
                "web": ["React", "Vue.js", "Angular"],
                "backend": ["Node.js", "Express", "NestJS"],
                "mobile": ["React Native", "Ionic"],
                "desktop": ["Electron"]
            },
            "java": {
                "web": ["Spring Boot", "Jakarta EE"],
                "gui": ["JavaFX", "Swing"],
                "android": ["Android SDK"],
                "dados": ["Spring Data", "Hibernate"]
            },
            "cpp": {
                "gui": ["Qt", "wxWidgets"],
                "jogos": ["SDL", "SFML"],
                "sistemas": ["Boost", "STL"]
            }
        }
        
        return frameworks.get(linguagem, {}).get(tipo_projeto, []) 