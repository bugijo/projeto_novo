import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    T5ForConditionalGeneration,
    T5Tokenizer
)
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
import re
import json
from pathlib import Path

class ProcessadorLinguagem:
    def __init__(self):
        # Carrega modelos e recursos
        self.nlp = spacy.load("pt_core_news_lg")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('portuguese'))
        
        # Carrega modelo de geração de texto
        self.modelo_conversa = self._carregar_modelo_conversa()
        self.tokenizer_conversa = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        
        # Modelo T5 para tarefas específicas
        self.t5_model = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.t5_tokenizer = T5Tokenizer.from_pretrained("t5-base")
        
        # Pipeline de classificação de intenções
        self.classificador_intencoes = pipeline("zero-shot-classification")
        
        # Histórico de conversas
        self.historico = []
        self.max_historico = 10
        
        # Carrega base de conhecimento
        self.conhecimento = self._carregar_conhecimento()

    def _carregar_modelo_conversa(self):
        """Carrega o modelo de conversação"""
        try:
            return AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        except Exception as e:
            print(f"Erro ao carregar modelo de conversação: {e}")
            return None

    def _carregar_conhecimento(self):
        """Carrega a base de conhecimento do assistente"""
        conhecimento_path = Path("data/conhecimento.json")
        if conhecimento_path.exists():
            with open(conhecimento_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "fatos": {},
            "regras": {},
            "contexto": {}
        }

    def processar_entrada(self, texto):
        """Processa a entrada do usuário"""
        # Análise básica
        doc = self.nlp(texto)
        
        # Extrai informações
        analise = {
            "texto_original": texto,
            "tokens": [token.text for token in doc],
            "entidades": [(ent.text, ent.label_) for ent in doc.ents],
            "sentimento": self.analisar_sentimento(texto),
            "intencao": self.classificar_intencao(texto),
            "tempo_verbal": self._identificar_tempo_verbal(doc),
            "substantivos": [token.text for token in doc if token.pos_ == "NOUN"],
            "verbos": [token.text for token in doc if token.pos_ == "VERB"]
        }
        
        return analise

    def analisar_sentimento(self, texto):
        """Analisa o sentimento do texto"""
        scores = self.sentiment_analyzer.polarity_scores(texto)
        
        # Determina o sentimento predominante
        if scores['compound'] >= 0.05:
            sentimento = 'positivo'
        elif scores['compound'] <= -0.05:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'
            
        return {
            "sentimento": sentimento,
            "scores": scores
        }

    def classificar_intencao(self, texto):
        """Classifica a intenção do usuário"""
        intencoes = [
            "pergunta",
            "comando",
            "informação",
            "cumprimento",
            "despedida",
            "agradecimento",
            "reclamação"
        ]
        
        resultado = self.classificador_intencoes(texto, intencoes)
        return {
            "intencao": resultado["labels"][0],
            "confianca": resultado["scores"][0]
        }

    def gerar_resposta(self, texto, contexto=None):
        """Gera uma resposta baseada no texto de entrada e contexto"""
        # Adiciona ao histórico
        self.historico.append(texto)
        if len(self.historico) > self.max_historico:
            self.historico.pop(0)
        
        # Prepara o contexto
        if contexto:
            prompt = f"Contexto: {contexto}\nPergunta: {texto}\nResposta:"
        else:
            prompt = texto
        
        # Tokeniza
        inputs = self.tokenizer_conversa.encode(prompt, return_tensors="pt")
        
        # Gera resposta
        outputs = self.modelo_conversa.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        resposta = self.tokenizer_conversa.decode(outputs[0], skip_special_tokens=True)
        return resposta

    def resumir_texto(self, texto):
        """Gera um resumo do texto"""
        inputs = self.t5_tokenizer.encode("summarize: " + texto, 
                                        return_tensors="pt", 
                                        max_length=512, 
                                        truncation=True)
        
        outputs = self.t5_model.generate(inputs, 
                                       max_length=150, 
                                       min_length=40, 
                                       length_penalty=2.0, 
                                       num_beams=4)
        
        return self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)

    def extrair_palavras_chave(self, texto):
        """Extrai palavras-chave do texto"""
        doc = self.nlp(texto)
        palavras = []
        
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN", "ADJ"] and 
                token.text.lower() not in self.stop_words):
                palavras.append({
                    "palavra": token.text,
                    "tipo": token.pos_,
                    "importancia": token.prob
                })
        
        return sorted(palavras, key=lambda x: x["importancia"], reverse=True)

    def _identificar_tempo_verbal(self, doc):
        """Identifica o tempo verbal predominante"""
        tempos = {
            "presente": 0,
            "passado": 0,
            "futuro": 0
        }
        
        for token in doc:
            if token.pos_ == "VERB":
                morph = token.morph.get("Tense")
                if morph:
                    if "Pres" in morph:
                        tempos["presente"] += 1
                    elif "Past" in morph:
                        tempos["passado"] += 1
                    elif "Fut" in morph:
                        tempos["futuro"] += 1
        
        return max(tempos.items(), key=lambda x: x[1])[0]

    def adicionar_conhecimento(self, tipo, chave, valor):
        """Adiciona informação à base de conhecimento"""
        if tipo in self.conhecimento:
            self.conhecimento[tipo][chave] = valor
            self._salvar_conhecimento()
            return True
        return False

    def buscar_conhecimento(self, tipo, chave):
        """Busca informação na base de conhecimento"""
        return self.conhecimento.get(tipo, {}).get(chave)

    def _salvar_conhecimento(self):
        """Salva a base de conhecimento em disco"""
        conhecimento_path = Path("data/conhecimento.json")
        conhecimento_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(conhecimento_path, 'w', encoding='utf-8') as f:
            json.dump(self.conhecimento, f, ensure_ascii=False, indent=4)

    def analisar_similaridade(self, texto1, texto2):
        """Calcula a similaridade entre dois textos"""
        doc1 = self.nlp(texto1)
        doc2 = self.nlp(texto2)
        return doc1.similarity(doc2)

    def corrigir_texto(self, texto):
        """Corrige erros básicos no texto"""
        # Implementação básica - pode ser expandida
        correcoes = {
            # Adicione correções comuns aqui
            "nao": "não",
            "tbm": "também",
            "vc": "você",
            "pq": "porque"
        }
        
        palavras = texto.split()
        corrigido = [correcoes.get(palavra.lower(), palavra) for palavra in palavras]
        return " ".join(corrigido)

    def identificar_idioma(self, texto):
        """Identifica o idioma do texto"""
        doc = self.nlp(texto)
        return doc.lang_

    def extrair_dados_estruturados(self, texto):
        """Extrai dados estruturados do texto (datas, valores, etc)"""
        doc = self.nlp(texto)
        dados = {
            "datas": [],
            "valores": [],
            "emails": [],
            "telefones": [],
            "urls": []
        }
        
        # Expressões regulares
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        telefone_pattern = r'\b\d{2}[\s-]?\d{4,5}[\s-]?\d{4}\b'
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        # Extrai entidades nomeadas
        for ent in doc.ents:
            if ent.label_ == "DATE":
                dados["datas"].append(ent.text)
            elif ent.label_ == "MONEY":
                dados["valores"].append(ent.text)
        
        # Extrai padrões
        dados["emails"] = re.findall(email_pattern, texto)
        dados["telefones"] = re.findall(telefone_pattern, texto)
        dados["urls"] = re.findall(url_pattern, texto)
        
        return dados 