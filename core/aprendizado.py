import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import json
from pathlib import Path
import datetime
import pickle
from typing import Dict, List, Optional, Union, Tuple

class AssistenteAprendizado:
    def __init__(self):
        # Inicializa vetorizador e classificador
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = MultinomialNB()
        
        # Carrega dados de treinamento
        self.dados_treinamento = self._carregar_dados_treinamento()
        
        # Histórico de interações
        self.historico = []
        self.max_historico = 1000
        
        # Preferências do usuário
        self.preferencias = self._carregar_preferencias()
        
        # Padrões aprendidos
        self.padroes = self._carregar_padroes()
        
        # Treina o modelo inicial
        self._treinar_modelo()

    def _carregar_dados_treinamento(self) -> pd.DataFrame:
        """Carrega dados de treinamento do assistente"""
        dados_path = Path("data/treinamento.csv")
        if dados_path.exists():
            return pd.read_csv(dados_path)
        return pd.DataFrame(columns=['comando', 'contexto', 'resultado', 'feedback'])

    def _carregar_preferencias(self) -> dict:
        """Carrega preferências do usuário"""
        pref_path = Path("data/preferencias.json")
        if pref_path.exists():
            with open(pref_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "horarios_ativos": [],
            "comandos_favoritos": {},
            "configuracoes_personalizadas": {},
            "notificacoes": {
                "ativas": True,
                "tipos": ["importante", "lembrete"]
            }
        }

    def _carregar_padroes(self) -> dict:
        """Carrega padrões de comportamento aprendidos"""
        padroes_path = Path("data/padroes.json")
        if padroes_path.exists():
            with open(padroes_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "sequencias_comuns": {},
            "horarios_pico": {},
            "correlacoes": {}
        }

    def _treinar_modelo(self):
        """Treina o modelo de classificação"""
        if len(self.dados_treinamento) > 0:
            X = self.vectorizer.fit_transform(self.dados_treinamento['comando'])
            y = self.dados_treinamento['resultado']
            self.classifier.fit(X, y)

    def registrar_interacao(self, comando: str, contexto: str, resultado: str, 
                          feedback: Optional[str] = None):
        """Registra uma nova interação para aprendizado"""
        # Adiciona ao histórico
        interacao = {
            'comando': comando,
            'contexto': contexto,
            'resultado': resultado,
            'feedback': feedback,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.historico.append(interacao)
        
        # Mantém tamanho máximo do histórico
        if len(self.historico) > self.max_historico:
            self.historico.pop(0)
        
        # Adiciona aos dados de treinamento
        nova_linha = pd.DataFrame([{
            'comando': comando,
            'contexto': contexto,
            'resultado': resultado,
            'feedback': feedback
        }])
        self.dados_treinamento = pd.concat([self.dados_treinamento, nova_linha], 
                                         ignore_index=True)
        
        # Atualiza padrões
        self._atualizar_padroes(interacao)
        
        # Retreina o modelo periodicamente
        if len(self.dados_treinamento) % 100 == 0:
            self._treinar_modelo()
            self._salvar_modelo()

    def prever_comando(self, entrada: str, contexto: str) -> List[Tuple[str, float]]:
        """Prevê o melhor comando baseado na entrada e contexto"""
        if len(self.dados_treinamento) == 0:
            return []
        
        # Vetoriza a entrada
        X = self.vectorizer.transform([entrada])
        
        # Obtém probabilidades para cada classe
        probs = self.classifier.predict_proba(X)[0]
        classes = self.classifier.classes_
        
        # Retorna as 3 melhores previsões
        previsoes = [(classe, prob) for classe, prob in zip(classes, probs)]
        return sorted(previsoes, key=lambda x: x[1], reverse=True)[:3]

    def atualizar_preferencias(self, novas_prefs: dict):
        """Atualiza as preferências do usuário"""
        self.preferencias.update(novas_prefs)
        self._salvar_preferencias()

    def _atualizar_padroes(self, interacao: dict):
        """Atualiza os padrões aprendidos com nova interação"""
        hora = datetime.datetime.fromisoformat(interacao['timestamp']).hour
        
        # Atualiza horários de pico
        self.padroes["horarios_pico"][str(hora)] = \
            self.padroes["horarios_pico"].get(str(hora), 0) + 1
        
        # Atualiza sequências comuns
        if len(self.historico) > 1:
            comando_anterior = self.historico[-2]['comando']
            comando_atual = interacao['comando']
            seq_key = f"{comando_anterior} -> {comando_atual}"
            self.padroes["sequencias_comuns"][seq_key] = \
                self.padroes["sequencias_comuns"].get(seq_key, 0) + 1
        
        # Salva padrões atualizados
        self._salvar_padroes()

    def sugerir_proxima_acao(self) -> List[str]:
        """Sugere próximas ações baseadas em padrões"""
        if not self.historico:
            return []
        
        ultimo_comando = self.historico[-1]['comando']
        sugestoes = []
        
        # Busca sequências comuns
        for seq, freq in self.padroes["sequencias_comuns"].items():
            if seq.startswith(f"{ultimo_comando} ->"):
                proximo = seq.split(" -> ")[1]
                sugestoes.append((proximo, freq))
        
        # Ordena por frequência
        sugestoes.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in sugestoes[:3]]

    def identificar_horario_ativo(self) -> bool:
        """Verifica se o horário atual é um horário ativo do usuário"""
        hora_atual = datetime.datetime.now().hour
        horarios_ordenados = sorted(
            self.padroes["horarios_pico"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        # Considera os 5 horários mais ativos
        horarios_ativos = [int(h[0]) for h in horarios_ordenados[:5]]
        return hora_atual in horarios_ativos

    def analisar_desempenho(self) -> dict:
        """Analisa o desempenho do assistente"""
        if len(self.dados_treinamento) < 100:
            return {"status": "Dados insuficientes para análise"}
        
        # Divide dados para teste
        X = self.vectorizer.transform(self.dados_treinamento['comando'])
        y = self.dados_treinamento['resultado']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Treina e avalia
        self.classifier.fit(X_train, y_train)
        score = self.classifier.score(X_test, y_test)
        
        # Análise de feedback
        feedback_positivo = self.dados_treinamento['feedback'].str.contains('positivo').sum()
        total_feedback = self.dados_treinamento['feedback'].notna().sum()
        
        return {
            "acuracia": score,
            "total_interacoes": len(self.dados_treinamento),
            "feedback_positivo": feedback_positivo / total_feedback if total_feedback > 0 else 0
        }

    def _salvar_modelo(self):
        """Salva o modelo treinado"""
        modelo_path = Path("models")
        modelo_path.mkdir(exist_ok=True)
        
        with open(modelo_path / "vectorizer.pkl", 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(modelo_path / "classifier.pkl", 'wb') as f:
            pickle.dump(self.classifier, f)

    def _salvar_preferencias(self):
        """Salva as preferências do usuário"""
        pref_path = Path("data/preferencias.json")
        pref_path.parent.mkdir(exist_ok=True)
        
        with open(pref_path, 'w', encoding='utf-8') as f:
            json.dump(self.preferencias, f, indent=4)

    def _salvar_padroes(self):
        """Salva os padrões aprendidos"""
        padroes_path = Path("data/padroes.json")
        padroes_path.parent.mkdir(exist_ok=True)
        
        with open(padroes_path, 'w', encoding='utf-8') as f:
            json.dump(self.padroes, f, indent=4)

    def exportar_dados(self, formato: str = 'json') -> Union[str, pd.DataFrame]:
        """Exporta dados de treinamento em diferentes formatos"""
        if formato == 'json':
            return self.dados_treinamento.to_json(orient='records')
        elif formato == 'csv':
            return self.dados_treinamento.to_csv(index=False)
        elif formato == 'dataframe':
            return self.dados_treinamento
        else:
            raise ValueError(f"Formato '{formato}' não suportado")

    def importar_dados(self, dados: Union[str, pd.DataFrame], formato: str = 'json'):
        """Importa dados de treinamento de diferentes fontes"""
        if formato == 'json':
            novos_dados = pd.read_json(dados)
        elif formato == 'csv':
            novos_dados = pd.read_csv(dados)
        elif formato == 'dataframe':
            novos_dados = dados
        else:
            raise ValueError(f"Formato '{formato}' não suportado")
        
        # Concatena com dados existentes
        self.dados_treinamento = pd.concat([self.dados_treinamento, novos_dados], 
                                         ignore_index=True)
        # Retreina o modelo
        self._treinar_modelo()

    def __del__(self):
        """Salva todos os dados antes de destruir o objeto"""
        try:
            self._salvar_modelo()
            self._salvar_preferencias()
            self._salvar_padroes()
            self.dados_treinamento.to_csv("data/treinamento.csv", index=False)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}") 