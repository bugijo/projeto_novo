import requests
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Optional, Union
import os
from datetime import datetime, timedelta
import feedparser
import tweepy
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GerenciadorIntegracoes:
    def __init__(self):
        # Carrega configurações
        self.config = self._carregar_configuracoes()
        
        # Inicializa clientes
        self.email_client = None
        self.twitter_client = None
        self.youtube_client = None
        
        # Inicializa conexões se credenciais estiverem disponíveis
        self._inicializar_conexoes()

    def _carregar_configuracoes(self) -> dict:
        """Carrega configurações das integrações"""
        config_path = Path("config/integracoes.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "imap_server": "imap.gmail.com",
                "email": "",
                "senha": ""
            },
            "clima": {
                "api_key": "",
                "cidade_padrao": "São Paulo,BR"
            },
            "noticias": {
                "api_key": "",
                "fontes": ["g1", "folha", "estadao"]
            },
            "twitter": {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": ""
            },
            "youtube": {
                "api_key": ""
            }
        }

    def _inicializar_conexoes(self):
        """Inicializa conexões com os serviços"""
        # Inicializa cliente de email
        if self.config["email"]["email"] and self.config["email"]["senha"]:
            self.email_client = {
                "smtp": smtplib.SMTP(self.config["email"]["smtp_server"], 
                                   self.config["email"]["smtp_port"]),
                "imap": imaplib.IMAP4_SSL(self.config["email"]["imap_server"])
            }
            self._conectar_email()
        
        # Inicializa cliente do Twitter
        if all(self.config["twitter"].values()):
            auth = tweepy.OAuthHandler(
                self.config["twitter"]["api_key"],
                self.config["twitter"]["api_secret"]
            )
            auth.set_access_token(
                self.config["twitter"]["access_token"],
                self.config["twitter"]["access_token_secret"]
            )
            self.twitter_client = tweepy.API(auth)
        
        # Inicializa cliente do YouTube
        if self.config["youtube"]["api_key"]:
            self.youtube_client = build('youtube', 'v3', 
                                      developerKey=self.config["youtube"]["api_key"])

    def _conectar_email(self):
        """Estabelece conexão com servidores de email"""
        try:
            # Conexão SMTP
            self.email_client["smtp"].starttls()
            self.email_client["smtp"].login(
                self.config["email"]["email"],
                self.config["email"]["senha"]
            )
            
            # Conexão IMAP
            self.email_client["imap"].login(
                self.config["email"]["email"],
                self.config["email"]["senha"]
            )
            return True
        except Exception as e:
            print(f"Erro ao conectar email: {e}")
            return False

    def enviar_email(self, destinatario: str, assunto: str, corpo: str,
                    html: bool = False) -> bool:
        """Envia um email"""
        if not self.email_client:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["email"]
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            if html:
                msg.attach(MIMEText(corpo, 'html'))
            else:
                msg.attach(MIMEText(corpo, 'plain'))
            
            self.email_client["smtp"].send_message(msg)
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False

    def ler_emails(self, pasta: str = "INBOX", nao_lidos: bool = True,
                  limite: int = 10) -> List[dict]:
        """Lê emails de uma pasta específica"""
        if not self.email_client:
            return []
        
        try:
            self.email_client["imap"].select(pasta)
            criterio = '(UNSEEN)' if nao_lidos else 'ALL'
            _, numeros = self.email_client["imap"].search(None, criterio)
            
            emails = []
            for num in numeros[0].split()[-limite:]:
                _, dados = self.email_client["imap"].fetch(num, '(RFC822)')
                email_body = dados[0][1]
                email_msg = email.message_from_bytes(email_body)
                
                emails.append({
                    'id': num.decode(),
                    'de': email_msg['from'],
                    'para': email_msg['to'],
                    'assunto': email_msg['subject'],
                    'data': email_msg['date'],
                    'corpo': self._extrair_corpo_email(email_msg)
                })
            
            return emails
        except Exception as e:
            print(f"Erro ao ler emails: {e}")
            return []

    def _extrair_corpo_email(self, email_msg) -> str:
        """Extrai o corpo de uma mensagem de email"""
        if email_msg.is_multipart():
            return self._extrair_corpo_email(email_msg.get_payload(0))
        return email_msg.get_payload(None, True).decode()

    def obter_previsao_tempo(self, cidade: str = None) -> Optional[dict]:
        """Obtém previsão do tempo para uma cidade"""
        if not self.config["clima"]["api_key"]:
            return None
        
        cidade = cidade or self.config["clima"]["cidade_padrao"]
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": cidade,
            "appid": self.config["clima"]["api_key"],
            "units": "metric",
            "lang": "pt_br"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            dados = response.json()
            
            return {
                "cidade": dados["name"],
                "temperatura": dados["main"]["temp"],
                "sensacao": dados["main"]["feels_like"],
                "minima": dados["main"]["temp_min"],
                "maxima": dados["main"]["temp_max"],
                "umidade": dados["main"]["humidity"],
                "descricao": dados["weather"][0]["description"],
                "icone": dados["weather"][0]["icon"]
            }
        except Exception as e:
            print(f"Erro ao obter previsão do tempo: {e}")
            return None

    def obter_noticias(self, categoria: str = None, limite: int = 10) -> List[dict]:
        """Obtém notícias das fontes configuradas"""
        if not self.config["noticias"]["api_key"]:
            return []
        
        noticias = []
        for fonte in self.config["noticias"]["fontes"]:
            try:
                feed = feedparser.parse(self._obter_url_feed(fonte))
                for entrada in feed.entries[:limite]:
                    noticias.append({
                        "titulo": entrada.title,
                        "descricao": entrada.description,
                        "link": entrada.link,
                        "data": entrada.published,
                        "fonte": fonte
                    })
            except Exception as e:
                print(f"Erro ao obter notícias de {fonte}: {e}")
        
        return sorted(noticias, key=lambda x: x["data"], reverse=True)[:limite]

    def _obter_url_feed(self, fonte: str) -> str:
        """Retorna a URL do feed RSS da fonte"""
        feeds = {
            "g1": "https://g1.globo.com/rss/g1/",
            "folha": "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
            "estadao": "https://www.estadao.com.br/rss/ultimas.xml"
        }
        return feeds.get(fonte, "")

    def postar_tweet(self, texto: str, imagem: str = None) -> bool:
        """Posta um tweet"""
        if not self.twitter_client:
            return False
        
        try:
            if imagem:
                media = self.twitter_client.media_upload(imagem)
                self.twitter_client.update_status(texto, media_ids=[media.media_id])
            else:
                self.twitter_client.update_status(texto)
            return True
        except Exception as e:
            print(f"Erro ao postar tweet: {e}")
            return False

    def ler_tweets(self, usuario: str = None, limite: int = 10) -> List[dict]:
        """Lê tweets de um usuário ou timeline"""
        if not self.twitter_client:
            return []
        
        try:
            if usuario:
                tweets = self.twitter_client.user_timeline(
                    screen_name=usuario,
                    count=limite
                )
            else:
                tweets = self.twitter_client.home_timeline(count=limite)
            
            return [{
                "id": tweet.id,
                "texto": tweet.text,
                "autor": tweet.user.screen_name,
                "data": tweet.created_at,
                "retweets": tweet.retweet_count,
                "curtidas": tweet.favorite_count
            } for tweet in tweets]
        except Exception as e:
            print(f"Erro ao ler tweets: {e}")
            return []

    def pesquisar_videos(self, termo: str, limite: int = 5) -> List[dict]:
        """Pesquisa vídeos no YouTube"""
        if not self.youtube_client:
            return []
        
        try:
            request = self.youtube_client.search().list(
                q=termo,
                part="snippet",
                maxResults=limite
            )
            response = request.execute()
            
            videos = []
            for item in response["items"]:
                if item["id"]["kind"] == "youtube#video":
                    videos.append({
                        "id": item["id"]["videoId"],
                        "titulo": item["snippet"]["title"],
                        "descricao": item["snippet"]["description"],
                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                        "canal": item["snippet"]["channelTitle"],
                        "data": item["snippet"]["publishedAt"]
                    })
            return videos
        except Exception as e:
            print(f"Erro ao pesquisar vídeos: {e}")
            return []

    def atualizar_configuracoes(self, novas_config: dict):
        """Atualiza as configurações das integrações"""
        self.config.update(novas_config)
        
        # Salva configurações
        config_path = Path("config/integracoes.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
        
        # Reinicializa conexões
        self._inicializar_conexoes()

    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        try:
            if self.email_client:
                self.email_client["smtp"].quit()
                self.email_client["imap"].logout()
        except:
            pass 