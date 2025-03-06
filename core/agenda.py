import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional
import threading
import time
from dataclasses import dataclass, asdict
import pytz
from dateutil import parser
import uuid

@dataclass
class Lembrete:
    id: str
    titulo: str
    descricao: str
    data_hora: datetime.datetime
    recorrencia: Optional[str] = None  # diário, semanal, mensal
    prioridade: str = "normal"  # baixa, normal, alta
    categorias: List[str] = None
    notificacao_antecipada: Optional[int] = None  # minutos
    status: str = "pendente"  # pendente, concluído, cancelado
    
    def __post_init__(self):
        if self.categorias is None:
            self.categorias = []
        if isinstance(self.data_hora, str):
            self.data_hora = parser.parse(self.data_hora)

@dataclass
class Evento:
    id: str
    titulo: str
    descricao: str
    inicio: datetime.datetime
    fim: datetime.datetime
    local: Optional[str] = None
    participantes: List[str] = None
    recorrencia: Optional[str] = None
    categorias: List[str] = None
    notificacoes: List[int] = None  # lista de minutos antes
    status: str = "agendado"
    
    def __post_init__(self):
        if self.participantes is None:
            self.participantes = []
        if self.categorias is None:
            self.categorias = []
        if self.notificacoes is None:
            self.notificacoes = [15]  # 15 minutos por padrão
        if isinstance(self.inicio, str):
            self.inicio = parser.parse(self.inicio)
        if isinstance(self.fim, str):
            self.fim = parser.parse(self.fim)

class GerenciadorAgenda:
    def __init__(self):
        self.lembretes: Dict[str, Lembrete] = {}
        self.eventos: Dict[str, Evento] = {}
        self.fuso_horario = pytz.timezone('America/Sao_Paulo')
        self.callbacks_notificacao = []
        self.thread_verificacao = None
        self.executando = False
        
        # Carrega dados salvos
        self._carregar_dados()
        
        # Inicia thread de verificação
        self.iniciar_verificacao()

    def _carregar_dados(self):
        """Carrega lembretes e eventos salvos"""
        dados_path = Path("data/agenda")
        dados_path.mkdir(parents=True, exist_ok=True)
        
        # Carrega lembretes
        lembretes_path = dados_path / "lembretes.json"
        if lembretes_path.exists():
            with open(lembretes_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.lembretes = {
                    id: Lembrete(**lembrete) 
                    for id, lembrete in dados.items()
                }
        
        # Carrega eventos
        eventos_path = dados_path / "eventos.json"
        if eventos_path.exists():
            with open(eventos_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.eventos = {
                    id: Evento(**evento)
                    for id, evento in dados.items()
                }

    def _salvar_dados(self):
        """Salva lembretes e eventos"""
        dados_path = Path("data/agenda")
        dados_path.mkdir(parents=True, exist_ok=True)
        
        # Salva lembretes
        with open(dados_path / "lembretes.json", 'w', encoding='utf-8') as f:
            dados = {id: asdict(lembrete) for id, lembrete in self.lembretes.items()}
            json.dump(dados, f, indent=4, default=str)
        
        # Salva eventos
        with open(dados_path / "eventos.json", 'w', encoding='utf-8') as f:
            dados = {id: asdict(evento) for id, evento in self.eventos.items()}
            json.dump(dados, f, indent=4, default=str)

    def adicionar_lembrete(self, titulo: str, descricao: str, data_hora: datetime.datetime,
                          **kwargs) -> str:
        """Adiciona um novo lembrete"""
        id = str(uuid.uuid4())
        lembrete = Lembrete(
            id=id,
            titulo=titulo,
            descricao=descricao,
            data_hora=data_hora,
            **kwargs
        )
        self.lembretes[id] = lembrete
        self._salvar_dados()
        return id

    def adicionar_evento(self, titulo: str, descricao: str, inicio: datetime.datetime,
                        fim: datetime.datetime, **kwargs) -> str:
        """Adiciona um novo evento"""
        id = str(uuid.uuid4())
        evento = Evento(
            id=id,
            titulo=titulo,
            descricao=descricao,
            inicio=inicio,
            fim=fim,
            **kwargs
        )
        self.eventos[id] = evento
        self._salvar_dados()
        return id

    def atualizar_lembrete(self, id: str, **kwargs) -> bool:
        """Atualiza um lembrete existente"""
        if id in self.lembretes:
            lembrete = self.lembretes[id]
            for key, value in kwargs.items():
                if hasattr(lembrete, key):
                    setattr(lembrete, key, value)
            self._salvar_dados()
            return True
        return False

    def atualizar_evento(self, id: str, **kwargs) -> bool:
        """Atualiza um evento existente"""
        if id in self.eventos:
            evento = self.eventos[id]
            for key, value in kwargs.items():
                if hasattr(evento, key):
                    setattr(evento, key, value)
            self._salvar_dados()
            return True
        return False

    def remover_lembrete(self, id: str) -> bool:
        """Remove um lembrete"""
        if id in self.lembretes:
            del self.lembretes[id]
            self._salvar_dados()
            return True
        return False

    def remover_evento(self, id: str) -> bool:
        """Remove um evento"""
        if id in self.eventos:
            del self.eventos[id]
            self._salvar_dados()
            return True
        return False

    def buscar_lembretes(self, filtros: dict = None) -> List[Lembrete]:
        """Busca lembretes com filtros"""
        resultados = []
        for lembrete in self.lembretes.values():
            if self._aplicar_filtros(lembrete, filtros):
                resultados.append(lembrete)
        return resultados

    def buscar_eventos(self, filtros: dict = None) -> List[Evento]:
        """Busca eventos com filtros"""
        resultados = []
        for evento in self.eventos.values():
            if self._aplicar_filtros(evento, filtros):
                resultados.append(evento)
        return resultados

    def _aplicar_filtros(self, item, filtros: dict) -> bool:
        """Aplica filtros em um item"""
        if not filtros:
            return True
        
        for key, value in filtros.items():
            if hasattr(item, key):
                item_value = getattr(item, key)
                
                # Tratamento especial para datas
                if isinstance(value, (datetime.date, datetime.datetime)):
                    if isinstance(item_value, datetime.datetime):
                        item_value = item_value.date()
                    if value != item_value:
                        return False
                
                # Tratamento para listas
                elif isinstance(value, list):
                    if not isinstance(item_value, list):
                        return False
                    if not all(v in item_value for v in value):
                        return False
                
                # Comparação direta
                elif value != item_value:
                    return False
        
        return True

    def registrar_callback_notificacao(self, callback: callable):
        """Registra uma função para receber notificações"""
        self.callbacks_notificacao.append(callback)

    def _notificar(self, tipo: str, item: Union[Lembrete, Evento]):
        """Envia notificações para os callbacks registrados"""
        for callback in self.callbacks_notificacao:
            try:
                callback(tipo, item)
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")

    def iniciar_verificacao(self):
        """Inicia a thread de verificação de lembretes e eventos"""
        if self.thread_verificacao is None or not self.thread_verificacao.is_alive():
            self.executando = True
            self.thread_verificacao = threading.Thread(target=self._verificar_periodicamente)
            self.thread_verificacao.daemon = True
            self.thread_verificacao.start()

    def parar_verificacao(self):
        """Para a thread de verificação"""
        self.executando = False
        if self.thread_verificacao:
            self.thread_verificacao.join()

    def _verificar_periodicamente(self):
        """Verifica periodicamente lembretes e eventos"""
        while self.executando:
            agora = datetime.datetime.now(self.fuso_horario)
            
            # Verifica lembretes
            for lembrete in self.lembretes.values():
                if lembrete.status == "pendente":
                    # Verifica notificação antecipada
                    if lembrete.notificacao_antecipada:
                        tempo_notificacao = lembrete.data_hora - \
                            datetime.timedelta(minutes=lembrete.notificacao_antecipada)
                        if agora >= tempo_notificacao:
                            self._notificar("lembrete_antecipado", lembrete)
                            
                    # Verifica hora do lembrete
                    if agora >= lembrete.data_hora:
                        self._notificar("lembrete", lembrete)
                        if not lembrete.recorrencia:
                            lembrete.status = "concluído"
                        else:
                            # Atualiza para próxima ocorrência
                            nova_data = self._calcular_proxima_ocorrencia(
                                lembrete.data_hora,
                                lembrete.recorrencia
                            )
                            lembrete.data_hora = nova_data
            
            # Verifica eventos
            for evento in self.eventos.values():
                if evento.status == "agendado":
                    # Verifica notificações antecipadas
                    for minutos in evento.notificacoes:
                        tempo_notificacao = evento.inicio - \
                            datetime.timedelta(minutes=minutos)
                        if agora >= tempo_notificacao:
                            self._notificar("evento_antecipado", evento)
                    
                    # Verifica início do evento
                    if agora >= evento.inicio:
                        self._notificar("evento_inicio", evento)
                    
                    # Verifica fim do evento
                    if agora >= evento.fim:
                        self._notificar("evento_fim", evento)
                        if not evento.recorrencia:
                            evento.status = "concluído"
                        else:
                            # Atualiza para próxima ocorrência
                            novo_inicio = self._calcular_proxima_ocorrencia(
                                evento.inicio,
                                evento.recorrencia
                            )
                            duracao = evento.fim - evento.inicio
                            evento.inicio = novo_inicio
                            evento.fim = novo_inicio + duracao
            
            # Salva alterações
            self._salvar_dados()
            
            # Aguarda próxima verificação
            time.sleep(60)  # Verifica a cada minuto

    def _calcular_proxima_ocorrencia(self, data: datetime.datetime, 
                                   recorrencia: str) -> datetime.datetime:
        """Calcula a próxima ocorrência baseada na recorrência"""
        if recorrencia == "diário":
            return data + datetime.timedelta(days=1)
        elif recorrencia == "semanal":
            return data + datetime.timedelta(weeks=1)
        elif recorrencia == "mensal":
            # Tenta manter o mesmo dia do mês
            proximo_mes = data + datetime.timedelta(days=32)
            return proximo_mes.replace(day=min(data.day, 28))
        return data

    def exportar_calendario(self, formato: str = "ics") -> str:
        """Exporta eventos e lembretes em formato de calendário"""
        if formato == "ics":
            return self._gerar_ics()
        else:
            raise ValueError(f"Formato '{formato}' não suportado")

    def _gerar_ics(self) -> str:
        """Gera arquivo ICS com eventos e lembretes"""
        linhas = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//AssistenteVirtual//PT-BR"
        ]
        
        # Adiciona eventos
        for evento in self.eventos.values():
            linhas.extend([
                "BEGIN:VEVENT",
                f"UID:{evento.id}",
                f"SUMMARY:{evento.titulo}",
                f"DESCRIPTION:{evento.descricao}",
                f"DTSTART:{evento.inicio.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{evento.fim.strftime('%Y%m%dT%H%M%S')}",
                "END:VEVENT"
            ])
        
        # Adiciona lembretes
        for lembrete in self.lembretes.values():
            linhas.extend([
                "BEGIN:VEVENT",
                f"UID:{lembrete.id}",
                f"SUMMARY:{lembrete.titulo}",
                f"DESCRIPTION:{lembrete.descricao}",
                f"DTSTART:{lembrete.data_hora.strftime('%Y%m%dT%H%M%S')}",
                "END:VEVENT"
            ])
        
        linhas.append("END:VCALENDAR")
        return "\n".join(linhas)

    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        self.parar_verificacao()
        self._salvar_dados() 