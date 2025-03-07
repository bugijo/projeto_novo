const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { initializeAI } = require('./ai/aiCore');
const { initializeVoice } = require('./voice/voiceSystem');
const { pluginManager } = require('./core/pluginManager');
const { config } = require('./config/config');
const { createLogger } = require('./utils/utils');

const logger = createLogger('[Main]');
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    frame: false,
    transparent: true
  });

  mainWindow.loadFile('src/ui/index.html');
  
  // Remover menu padrão
  mainWindow.setMenu(null);

  // Eventos da janela
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

async function initialize() {
  try {
    logger.info('Iniciando aplicação...');

    // Inicializar sistemas
    await initializeAI();
    logger.info('Sistema de IA inicializado');

    await initializeVoice();
    logger.info('Sistema de voz inicializado');

    await pluginManager.initialize();
    logger.info('Sistema de plugins inicializado');

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