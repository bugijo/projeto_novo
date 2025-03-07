const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { initializeAI } = require('./ai/aiCore');
const { initializeVoice } = require('./voice/voiceSystem');
const { pluginManager } = require('./core/pluginManager');
const { config } = require('./config/config');
const { createLogger } = require('./utils/utils');
const autoBackup = require('./utils/autoBackup');
const cursorConfig = require('./utils/cursorConfig');
const taskManager = require('./utils/taskManager');
const agentManager = require('./utils/agentManager');
const testRunner = require('./utils/testRunner');
const previewManager = require('./utils/previewManager');
const fs = require('fs');
const integratedTestManager = require('./utils/integratedTestManager');
const notificationManager = require('./utils/notificationManager');
const taskExecutor = require('./utils/taskExecutor');

const logger = createLogger('[Main]');
let mainWindow;

// Carregar configurações do Cursor
let cursorSettings = {};
try {
    const cursorConfigPath = path.join(__dirname, '../.cursor/settings.json');
    cursorSettings = JSON.parse(fs.readFileSync(cursorConfigPath, 'utf8'));
} catch (error) {
    logger.warn('Configurações do Cursor não encontradas, usando padrões');
}

function createWindow() {
    const windowConfig = {
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableAutoSave: true, // Sempre ativar auto-save
            // Configurações expandidas
            maxLinesPerView: cursorConfig.config.maxLinesPerView,
            maxSearchResults: cursorConfig.config.maxSearchResults,
            disableLineLimits: cursorConfig.config.disableLineLimits
        },
        frame: false,
        transparent: true
    };

    mainWindow = new BrowserWindow(windowConfig);
    mainWindow.loadFile('src/ui/index.html');
    
    // Remover menu padrão
    mainWindow.setMenu(null);

    // Configurar auto-save e testes integrados
    setupAutoSaveAndTests();

    // Eventos da janela
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function setupAutoSaveAndTests() {
    // Configurar auto-save
    integratedTestManager.setAutoSave(true);

    // Registrar suites de teste padrão
    integratedTestManager.registerTestSuite('core', {
        files: ['src/core/**/*.js'],
        unitTests: [
            // Testes unitários do core
        ],
        integrationTests: [
            // Testes de integração do core
        ],
        autoFix: true
    });

    integratedTestManager.registerTestSuite('ui', {
        files: ['src/ui/**/*.{html,js,css}'],
        uiTests: [
            {
                url: 'file://src/ui/index.html',
                config: {
                    elements: [
                        { selector: '#app', shouldExist: true },
                        { selector: '#preview-container', shouldExist: true }
                    ],
                    styles: [
                        {
                            selector: 'body',
                            properties: {
                                margin: '0px',
                                padding: '0px'
                            }
                        }
                    ]
                }
            }
        ],
        autoFix: true
    });

    // Registrar mais suites conforme necessário
}

async function initialize() {
  try {
    logger.info('Iniciando aplicação...');

    // Iniciar executor de tarefas
    await taskExecutor.start();

    // Inicializar sistemas
    await initializeAI();
    logger.info('Sistema de IA inicializado');

    await initializeVoice();
    logger.info('Sistema de voz inicializado');

    await config.load();
    await pluginManager.initialize();
    logger.info('Sistema de plugins inicializado');

    // Inicia o sistema de backup automático
    autoBackup.startWatching();

    // Criar janela principal
    createWindow();
    logger.info('Interface iniciada');
  } catch (error) {
    logger.error('Erro ao inicializar aplicação:', error);
    app.quit();
  }
}

// Eventos do Electron
app.whenReady().then(initialize);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers
ipcMain.handle('minimize-window', () => {
  mainWindow.minimize();
});

ipcMain.handle('maximize-window', () => {
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.handle('close-window', () => {
  mainWindow.close();
});

// Handlers de plugins
ipcMain.handle('get-plugins', () => {
  return pluginManager.getPluginInfo();
});

ipcMain.handle('execute-plugin-command', async (event, command, args) => {
  return await pluginManager.processCommand(command, args);
});

// Handlers de configuração
ipcMain.handle('get-config', (event, key) => {
  return config.get(key);
});

ipcMain.handle('set-config', (event, key, value) => {
  config.set(key, value);
});

// Adicionar novos handlers para auto-save
ipcMain.handle('watch-file', (event, filePath) => {
    autoBackup.watchFile(filePath);
});

ipcMain.handle('save-file', async (event, filePath) => {
    await integratedTestManager.saveFile(filePath);
});

// Adicionar handlers para configurações do Cursor
ipcMain.handle('get-cursor-config', (event, key) => {
    return cursorConfig.config[key];
});

ipcMain.handle('update-cursor-config', (event, newConfig) => {
    return cursorConfig.updateConfig(newConfig);
});

ipcMain.handle('get-max-lines', (event, commandName) => {
    return cursorConfig.getMaxLines(commandName);
});

ipcMain.handle('get-max-results', (event, commandName) => {
    return cursorConfig.getMaxResults(commandName);
});

// Adicionar handlers para gerenciamento de tarefas
ipcMain.handle('plan-tasks', async (event, tasks, context) => {
    return await agentManager.planTasks(tasks, context);
});

ipcMain.handle('execute-plan', async (event, planId) => {
    return await agentManager.executePlan(planId);
});

ipcMain.handle('get-plan-progress', (event, planId) => {
    return agentManager.getProgress(planId);
});

ipcMain.handle('cancel-plan', (event, planId) => {
    return agentManager.cancelPlan(planId);
});

// Adicionar handlers para tarefas individuais
ipcMain.handle('add-task', (event, task) => {
    return taskManager.addTask(task);
});

ipcMain.handle('get-task-progress', () => {
    return taskManager.getProgress();
});

// Adicionar handlers para testes e preview
ipcMain.handle('open-preview', async (event, filePath, options) => {
    return await previewManager.showPreview(filePath, options);
});

ipcMain.handle('refresh-preview', async () => {
    return await previewManager.refreshPreview();
});

ipcMain.handle('run-tests', async (event, testConfig) => {
    return await previewManager.runTests(testConfig);
});

ipcMain.handle('apply-correction', async (event, correction) => {
    return await previewManager.applyCorrection(correction);
});

ipcMain.handle('set-watch-mode', (event, mode) => {
    previewManager.watchMode = mode;
});

// Adicionar handlers para testes integrados
ipcMain.handle('run-all-tests', async () => {
    const results = await integratedTestManager.runAffectedTests();
    return results;
});

ipcMain.handle('get-test-results', () => {
    return integratedTestManager.getTestResults();
});

// Adicionar handlers para notificações
ipcMain.handle('set-notification-token', async (event, token) => {
    notificationManager.setApiToken(token);
});

ipcMain.handle('test-notification', async () => {
    await notificationManager.sendNotification(
        'Teste de Notificação',
        'Se você recebeu esta mensagem, as notificações estão funcionando corretamente!'
    );
});

// Cleanup ao fechar
app.on('window-all-closed', () => {
    previewManager.cleanup();
    testRunner.cleanup();
    if (process.platform !== 'darwin') {
        app.quit();
    }
}); 