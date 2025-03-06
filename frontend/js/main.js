// Gerenciador do chat
const chat = {
    modeloSelecionado: 'llama2', // Começamos com llama2 já que é o único disponível
    statusServidor: false,

    init() {
        this.bindEvents();
        this.verificarStatus();
        setInterval(() => this.verificarStatus(), 5000);
    },

    bindEvents() {
        document.getElementById('btnSend').addEventListener('click', () => this.enviarMensagem());
        
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.enviarMensagem();
            }
        });

        document.querySelectorAll('.modelo-card').forEach(card => {
            card.addEventListener('click', () => {
                const modelo = card.dataset.modelo;
                const statusModelo = card.querySelector('.status-modelo');
                if (statusModelo.textContent === 'Indisponível') {
                    this.mostrarNotificacao('Modelo indisponível no momento', 'error');
                    return;
                }
                this.selecionarModelo(modelo);
            });
        });
    },

    async verificarStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            this.statusServidor = data.online;
            const statusEl = document.getElementById('statusServidor');
            const statusDot = statusEl.querySelector('span:first-child');
            const statusText = statusEl.querySelector('.status-text');
            
            if (data.online) {
                statusEl.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-full bg-green-500 bg-opacity-20 text-sm font-medium text-green-500';
                statusDot.className = 'h-2 w-2 rounded-full bg-green-500';
                statusText.textContent = 'Servidor Online';
                
                data.modelos.forEach(modelo => {
                    const modeloEl = document.querySelector(`[data-modelo="${modelo.nome}"] .status-modelo`);
                    if (modeloEl) {
                        const disponivel = modelo.status;
                        modeloEl.textContent = disponivel ? 'Disponível' : 'Indisponível';
                        modeloEl.className = `status-modelo text-xs mt-2 inline-block px-2 py-1 rounded-full ${
                            disponivel ? 'bg-green-500 bg-opacity-20 text-green-500' : 'bg-red-500 bg-opacity-20 text-red-500'
                        }`;
                    }
                });
            } else {
                statusEl.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-full bg-red-500 bg-opacity-20 text-sm font-medium text-red-500';
                statusDot.className = 'h-2 w-2 rounded-full bg-red-500';
                statusText.textContent = 'Servidor Offline';
            }
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            const statusEl = document.getElementById('statusServidor');
            statusEl.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-full bg-yellow-500 bg-opacity-20 text-sm font-medium text-yellow-500';
            statusEl.querySelector('span:first-child').className = 'h-2 w-2 rounded-full bg-yellow-500';
            statusEl.querySelector('.status-text').textContent = 'Erro ao verificar status';
        }
    },

    selecionarModelo(modelo) {
        document.querySelectorAll('.modelo-card').forEach(card => {
            card.classList.remove('selecionado', 'ring-2', 'ring-blue-500');
        });
        
        const card = document.querySelector(`[data-modelo="${modelo}"]`);
        if (card) {
            card.classList.add('selecionado');
            this.modeloSelecionado = modelo;
            this.mostrarNotificacao(`Modelo alterado para: ${modelo}`, 'info');
        }
    },

    mostrarNotificacao(mensagem, tipo = 'info') {
        const notificacao = document.createElement('div');
        notificacao.className = `message p-4 rounded-lg text-center ${
            tipo === 'error' ? 'bg-red-500 bg-opacity-20 text-red-500' :
            tipo === 'info' ? 'bg-blue-500 bg-opacity-20 text-blue-500' :
            'bg-gray-500 bg-opacity-20 text-gray-500'
        }`;
        notificacao.textContent = mensagem;
        
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.appendChild(notificacao);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        setTimeout(() => {
            notificacao.style.opacity = '0';
            setTimeout(() => notificacao.remove(), 300);
        }, 3000);
    },

    async enviarMensagem() {
        const input = document.getElementById('messageInput');
        const mensagem = input.value.trim();
        
        if (!mensagem) return;
        
        this.adicionarMensagem(mensagem, 'user');
        input.value = '';
        input.focus();
        
        this.adicionarIndicadorDigitacao();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: mensagem,
                    model: this.modeloSelecionado
                })
            });
            
            const data = await response.json();
            this.removerIndicadorDigitacao();
            
            if (data.erro) {
                this.mostrarNotificacao(data.erro, 'error');
            } else {
                this.adicionarMensagem(data.resposta, 'assistant');
            }
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.removerIndicadorDigitacao();
            this.mostrarNotificacao('Erro ao enviar mensagem. Tente novamente.', 'error');
        }
    },

    adicionarMensagem(texto, tipo) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        
        const isUser = tipo === 'user';
        messageDiv.className = `message flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;
        
        const iconDiv = document.createElement('div');
        iconDiv.className = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'order-2 bg-blue-500' : 'bg-[#2D2D2D] border border-[#333333]'
        }`;
        iconDiv.innerHTML = isUser ? 
            '<i class="fas fa-user text-white text-sm"></i>' : 
            '<i class="fas fa-robot text-blue-500 text-sm"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = `flex-1 ${isUser ? 'order-1' : ''} max-w-2xl`;
        
        const textDiv = document.createElement('div');
        textDiv.className = `p-4 rounded-lg ${
            isUser ? 'bg-blue-600 text-white' : 'bg-[#2D2D2D] border border-[#333333]'
        }`;
        textDiv.textContent = texto;
        
        contentDiv.appendChild(textDiv);
        messageDiv.appendChild(iconDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },

    adicionarIndicadorDigitacao() {
        const chatMessages = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'message flex items-start space-x-3';
        
        const iconDiv = document.createElement('div');
        iconDiv.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-[#2D2D2D] border border-[#333333] flex items-center justify-center';
        iconDiv.innerHTML = '<i class="fas fa-robot text-blue-500 text-sm"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'flex-1 max-w-2xl';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'p-4 rounded-lg bg-[#2D2D2D] border border-[#333333] typing-dots';
        textDiv.textContent = 'Pensando';
        
        contentDiv.appendChild(textDiv);
        typingDiv.appendChild(iconDiv);
        typingDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },

    removerIndicadorDigitacao() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => chat.init()); 