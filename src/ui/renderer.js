const { ipcRenderer } = require('electron');
const { aiCore } = require('../ai/aiCore');
const { voiceSystem } = require('../voice/voiceSystem');

// Elementos da interface
const minimizeBtn = document.getElementById('minimize-btn');
const maximizeBtn = document.getElementById('maximize-btn');
const closeBtn = document.getElementById('close-btn');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const messagesContainer = document.getElementById('messages');

// Controles da janela
minimizeBtn.addEventListener('click', () => {
    ipcRenderer.invoke('minimize-window');
});

maximizeBtn.addEventListener('click', () => {
    ipcRenderer.invoke('maximize-window');
});

closeBtn.addEventListener('click', () => {
    ipcRenderer.invoke('close-window');
});

// Função para adicionar mensagem ao chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll para a última mensagem
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Função para processar input do usuário
async function processUserInput(text) {
    if (!text.trim()) return;
    
    // Adicionar mensagem do usuário
    addMessage(text, true);
    
    try {
        // Gerar resposta da IA
        const response = await aiCore.generateResponse(text);
        
        // Adicionar resposta da IA
        addMessage(response);
        
        // Sintetizar voz da resposta
        await voiceSystem.speak(response);
    } catch (error) {
        console.error('Erro ao processar mensagem:', error);
        addMessage('Desculpe, ocorreu um erro ao processar sua mensagem.', false);
    }
}

// Event listeners para input
sendBtn.addEventListener('click', () => {
    const text = messageInput.value;
    messageInput.value = '';
    processUserInput(text);
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const text = messageInput.value;
        messageInput.value = '';
        processUserInput(text);
    }
});

// Sistema de voz
let isListening = false;

voiceBtn.addEventListener('click', () => {
    if (isListening) {
        voiceSystem.stopListening();
        voiceBtn.style.background = 'var(--primary-color)';
        isListening = false;
    } else {
        voiceSystem.startListening((text) => {
            messageInput.value = text;
            processUserInput(text);
        });
        voiceBtn.style.background = 'var(--error-color)';
        isListening = true;
    }
});

// Navegação
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remover classe active de todos os links
        document.querySelectorAll('nav li').forEach(li => {
            li.classList.remove('active');
        });
        
        // Adicionar classe active ao link clicado
        link.parentElement.classList.add('active');
        
        // TODO: Implementar navegação entre páginas
        console.log('Navegando para:', link.getAttribute('href'));
    });
}); 