// Elementos da interface
const console = document.getElementById('console');
const commandInput = document.getElementById('commandInput');
const btnSend = document.getElementById('btnSend');
const btnConfig = document.getElementById('btnConfig');
const btnUpdate = document.getElementById('btnUpdate');
const configModal = document.getElementById('configModal');
const btnCancelConfig = document.getElementById('btnCancelConfig');
const btnSaveConfig = document.getElementById('btnSaveConfig');
const voiceSelect = document.getElementById('voiceSelect');
const volumeRange = document.getElementById('volumeRange');
const rateRange = document.getElementById('rateRange');
const cpuUsage = document.getElementById('cpuUsage');
const memoryUsage = document.getElementById('memoryUsage');
const recentProjects = document.getElementById('recentProjects');

// WebSocket para comunicação em tempo real
let ws = null;

// Configurações do assistente
let config = {
    voice: null,
    volume: 100,
    rate: 200,
    autoUpdate: false
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    loadConfig();
    initEventListeners();
    initSystemMonitoring();
    loadRecentProjects();
});

// Inicializa WebSocket
function initWebSocket() {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
        addConsoleMessage('Sistema conectado', 'system');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
        addConsoleMessage('Conexão perdida. Tentando reconectar...', 'error');
        setTimeout(initWebSocket, 5000);
    };
}

// Manipula mensagens do WebSocket
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'response':
            addConsoleMessage(data.message, 'system');
            break;
        case 'error':
            addConsoleMessage(data.message, 'error');
            break;
        case 'status':
            updateSystemStatus(data);
            break;
        case 'projects':
            updateRecentProjects(data.projects);
            break;
        case 'update':
            handleSystemUpdate(data);
            break;
    }
}

// Adiciona mensagem ao console
function addConsoleMessage(message, type = 'system') {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.textContent = message;
    console.appendChild(line);
    console.scrollTop = console.scrollHeight;
}

// Envia comando para o backend
function sendCommand(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'command',
            command: command
        }));
        addConsoleMessage(`> ${command}`, 'user');
        commandInput.value = '';
    } else {
        addConsoleMessage('Erro: Sistema não conectado', 'error');
    }
}

// Inicializa event listeners
function initEventListeners() {
    // Envio de comando
    btnSend.addEventListener('click', () => {
        const command = commandInput.value.trim();
        if (command) {
            sendCommand(command);
        }
    });

    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const command = commandInput.value.trim();
            if (command) {
                sendCommand(command);
            }
        }
    });

    // Modal de configurações
    btnConfig.addEventListener('click', () => {
        configModal.classList.remove('hidden');
    });

    btnCancelConfig.addEventListener('click', () => {
        configModal.classList.add('hidden');
    });

    btnSaveConfig.addEventListener('click', () => {
        saveConfig();
        configModal.classList.add('hidden');
    });

    // Atualização do sistema
    btnUpdate.addEventListener('click', () => {
        if (confirm('Deseja verificar atualizações do sistema?')) {
            checkForUpdates();
        }
    });

    // Comandos rápidos
    document.querySelectorAll('.quick-command').forEach(btn => {
        btn.addEventListener('click', () => {
            sendCommand(btn.textContent.trim());
        });
    });
}

// Monitoramento do sistema
function initSystemMonitoring() {
    setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'status_request'
            }));
        }
    }, 5000);
}

// Atualiza status do sistema
function updateSystemStatus(data) {
    cpuUsage.textContent = `${data.cpu}%`;
    memoryUsage.textContent = `${data.memory}%`;

    // Atualiza cores baseado no uso
    const cpuColor = data.cpu > 80 ? '#f44336' : data.cpu > 50 ? '#ff9800' : '#4CAF50';
    const memColor = data.memory > 80 ? '#f44336' : data.memory > 50 ? '#ff9800' : '#4CAF50';
    
    cpuUsage.style.color = cpuColor;
    memoryUsage.style.color = memColor;
}

// Carrega projetos recentes
function loadRecentProjects() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'get_recent_projects'
        }));
    }
}

// Atualiza lista de projetos recentes
function updateRecentProjects(projects) {
    recentProjects.innerHTML = '';
    projects.forEach(project => {
        const card = document.createElement('div');
        card.className = 'project-card bg-gray-700 p-4 rounded-lg';
        card.innerHTML = `
            <h3 class="font-bold">${project.name}</h3>
            <p class="text-sm text-gray-400">${project.type} - ${project.date}</p>
        `;
        card.addEventListener('click', () => {
            sendCommand(`abrir pasta ${project.path}`);
        });
        recentProjects.appendChild(card);
    });
}

// Verifica atualizações
function checkForUpdates() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'check_updates'
        }));
        addConsoleMessage('Verificando atualizações...', 'system');
    }
}

// Manipula atualização do sistema
function handleSystemUpdate(data) {
    if (data.available) {
        if (confirm(`Nova versão disponível: ${data.version}\nDeseja atualizar agora?`)) {
            ws.send(JSON.stringify({
                type: 'update_system'
            }));
        }
    } else {
        addConsoleMessage('Sistema está atualizado!', 'system');
    }
}

// Carrega configurações
function loadConfig() {
    const savedConfig = localStorage.getItem('assistantConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
        volumeRange.value = config.volume;
        rateRange.value = config.rate;
    }
}

// Salva configurações
function saveConfig() {
    config.volume = volumeRange.value;
    config.rate = rateRange.value;
    config.voice = voiceSelect.value;
    
    localStorage.setItem('assistantConfig', JSON.stringify(config));
    
    ws.send(JSON.stringify({
        type: 'update_config',
        config: config
    }));
    
    addConsoleMessage('Configurações salvas com sucesso!', 'system');
} 