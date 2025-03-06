import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

from config.system_config import AI_CONFIG

@dataclass
class TaskContext:
    """Contexto da tarefa para manter estado da conversa."""
    task_type: str
    requirements: List[str]
    platform: Optional[str] = None
    framework: Optional[str] = None
    style: Optional[str] = None
    features: List[str] = None
    dependencies: List[str] = None
    current_step: str = "initial"
    
    def __post_init__(self):
        self.features = self.features or []
        self.dependencies = self.dependencies or []

class TaskAnalyzer:
    """Analisador de tarefas que entende requisições do usuário."""
    
    def __init__(self):
        self.logger = logging.getLogger('TaskAnalyzer')
        self.contexts = {}  # Mantém contexto por usuário
        
        # Padrões de reconhecimento de tarefas
        self.task_patterns = {
            'app_development': r'\b(criar|desenvolver|fazer)\b.*(app|aplicativo|aplicação|sistema)\b',
            'game_development': r'\b(criar|desenvolver|fazer)\b.*(jogo|game)\b',
            'image_generation': r'\b(criar|gerar|fazer)\b.*(imagem|figura|arte|desenho)\b',
            '3d_modeling': r'\b(criar|gerar|modelar)\b.*(3d|modelo|personagem)\b',
            'code_analysis': r'\b(analisar|revisar|verificar)\b.*(código|programa|sistema)\b',
            'email_management': r'\b(ver|ler|gerenciar)\b.*(email|e-mail|gmail)\b',
            'calendar_management': r'\b(agendar|marcar|ver)\b.*(compromisso|evento|reunião)\b',
        }
        
        # Questões por tipo de tarefa
        self.task_questions = {
            'app_development': [
                "Para qual plataforma você quer desenvolver (Android, iOS, Web, Desktop)?",
                "Qual o objetivo principal do aplicativo?",
                "Quais funcionalidades principais você precisa?",
                "Tem preferência por alguma tecnologia ou framework?",
                "Como você quer que seja a interface do usuário?",
                "Precisa de alguma integração específica (banco de dados, APIs)?",
                "O app precisa funcionar offline?",
                "Tem requisitos de segurança específicos?"
            ],
            'game_development': [
                "Que tipo de jogo você quer criar (2D, 3D, gênero)?",
                "Para qual plataforma (PC, Mobile, Web)?",
                "Qual é a história ou conceito principal do jogo?",
                "Quais mecânicas principais o jogo deve ter?",
                "Como deve ser o estilo visual?",
                "Precisa de sistema de salvamento?",
                "Terá multiplayer?",
                "Quais são os objetivos do jogador?"
            ],
            'image_generation': [
                "Que tipo de imagem você quer gerar?",
                "Qual o estilo artístico desejado?",
                "Quais elementos principais devem aparecer?",
                "Tem preferência de cores ou tema?",
                "Qual o propósito da imagem (arte conceitual, marketing, etc)?",
                "Qual resolução você precisa?"
            ],
            '3d_modeling': [
                "O que você quer modelar em 3D?",
                "Qual o nível de detalhe necessário?",
                "Precisa de texturização?",
                "Vai precisar de animação?",
                "Qual o propósito do modelo (jogo, renderização, impressão 3D)?"
            ]
        }
    
    async def analyze_request(self, message: str, user_id: str) -> Tuple[str, Optional[List[str]]]:
        """Analisa a requisição do usuário e retorna o tipo de tarefa e possíveis perguntas."""
        try:
            # Verifica se já existe um contexto para o usuário
            context = self.contexts.get(user_id)
            
            if context:
                # Continua conversa existente
                return await self._continue_conversation(message, context, user_id)
            else:
                # Inicia nova conversa
                return await self._start_new_conversation(message, user_id)
                
        except Exception as e:
            self.logger.error(f"Erro ao analisar requisição: {str(e)}")
            raise
    
    async def _start_new_conversation(self, message: str, user_id: str) -> Tuple[str, List[str]]:
        """Inicia uma nova conversa identificando o tipo de tarefa."""
        task_type = self._identify_task_type(message)
        
        if not task_type:
            return 'unknown', ["Desculpe, não entendi exatamente o que você quer fazer. Pode explicar melhor?"]
        
        # Cria novo contexto
        context = TaskContext(
            task_type=task_type,
            requirements=[],
            current_step="requirements"
        )
        self.contexts[user_id] = context
        
        # Retorna primeiras perguntas
        return task_type, self.task_questions.get(task_type, [])
    
    async def _continue_conversation(self, message: str, context: TaskContext, user_id: str) -> Tuple[str, Optional[List[str]]]:
        """Continua uma conversa existente."""
        # Atualiza contexto com a resposta
        self._update_context(context, message)
        
        # Verifica se tem todas as informações necessárias
        if self._is_context_complete(context):
            # Remove contexto e retorna resultado final
            del self.contexts[user_id]
            return context.task_type, None
        
        # Retorna próximas perguntas baseado no contexto atual
        return context.task_type, self._get_next_questions(context)
    
    def _identify_task_type(self, message: str) -> str:
        """Identifica o tipo de tarefa baseado na mensagem."""
        message = message.lower()
        
        for task_type, pattern in self.task_patterns.items():
            if re.search(pattern, message):
                return task_type
        
        return 'unknown'
    
    def _update_context(self, context: TaskContext, message: str):
        """Atualiza o contexto com a resposta do usuário."""
        if context.current_step == "requirements":
            context.requirements.append(message)
            
            # Identifica informações específicas na resposta
            if "android" in message.lower() or "ios" in message.lower():
                context.platform = "mobile"
            if "react" in message.lower():
                context.framework = "react"
            if "moderno" in message.lower() or "minimalista" in message.lower():
                context.style = message
        
        # Atualiza o passo atual baseado nas respostas
        if len(context.requirements) >= 3:
            context.current_step = "details"
    
    def _is_context_complete(self, context: TaskContext) -> bool:
        """Verifica se tem informações suficientes para executar a tarefa."""
        if context.task_type in ['app_development', 'game_development']:
            return (
                len(context.requirements) >= 3 and
                context.platform is not None
            )
        
        return len(context.requirements) >= 2
    
    def _get_next_questions(self, context: TaskContext) -> List[str]:
        """Retorna as próximas perguntas baseado no contexto atual."""
        questions = self.task_questions.get(context.task_type, [])
        
        if context.current_step == "requirements":
            return questions[:2]  # Primeiras perguntas
        elif context.current_step == "details":
            return questions[2:4]  # Perguntas de detalhes
        
        return []

    def get_task_summary(self, context: TaskContext) -> Dict:
        """Gera um resumo da tarefa baseado no contexto."""
        return {
            'type': context.task_type,
            'requirements': context.requirements,
            'platform': context.platform,
            'framework': context.framework,
            'style': context.style,
            'features': context.features,
            'dependencies': context.dependencies
        } 