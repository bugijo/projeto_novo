const { Ollama } = require('node-ollama');
const path = require('path');
const fs = require('fs');

class AICore {
  constructor() {
    this.ollama = new Ollama();
    this.modelName = 'phi';
    this.context = [];
    this.isInitialized = false;
  }

  async initialize() {
    try {
      // Verificar se o Ollama está instalado
      await this.checkOllamaInstallation();
      
      // Carregar o modelo
      await this.loadModel();
      
      // Inicializar sistema de cache
      this.initializeCache();
      
      this.isInitialized = true;
      console.log('Sistema de IA inicializado com sucesso');
    } catch (error) {
      console.error('Erro ao inicializar sistema de IA:', error);
      throw error;
    }
  }

  async checkOllamaInstallation() {
    try {
      await this.ollama.list();
    } catch (error) {
      console.error('Ollama não encontrado. Por favor, instale o Ollama primeiro.');
      throw new Error('Ollama não instalado');
    }
  }

  async loadModel() {
    try {
      // Verificar se o modelo já está baixado
      const models = await this.ollama.list();
      const modelExists = models.some(m => m.name === this.modelName);

      if (!modelExists) {
        console.log('Baixando modelo...');
        await this.ollama.pull(this.modelName);
      }

      console.log('Modelo carregado com sucesso');
    } catch (error) {
      console.error('Erro ao carregar modelo:', error);
      throw error;
    }
  }

  initializeCache() {
    // Implementar sistema de cache
    this.cache = new Map();
    
    // Criar diretório de cache se não existir
    const cacheDir = path.join(__dirname, '../../cache');
    if (!fs.existsSync(cacheDir)) {
      fs.mkdirSync(cacheDir);
    }
  }

  async generateResponse(input) {
    if (!this.isInitialized) {
      throw new Error('Sistema de IA não inicializado');
    }

    try {
      // Verificar cache
      const cacheKey = input.trim().toLowerCase();
      if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }

      // Gerar resposta
      const response = await this.ollama.generate({
        model: this.modelName,
        prompt: input,
        context: this.context
      });

      // Atualizar contexto
      this.context = response.context;

      // Cachear resposta
      this.cache.set(cacheKey, response.text);

      return response.text;
    } catch (error) {
      console.error('Erro ao gerar resposta:', error);
      throw error;
    }
  }
}

const aiCore = new AICore();

async function initializeAI() {
  await aiCore.initialize();
}

module.exports = {
  initializeAI,
  aiCore
}; 