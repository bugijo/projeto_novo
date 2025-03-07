const { LLM } = require('llama-node');
const { LLamaCpp } = require('@llama-node/llama-cpp');
const path = require('path');
const fs = require('fs');

class AIManager {
    constructor() {
        this.models = new Map();
        this.initialized = false;
        this.config = require('./config.json');
    }

    async initialize() {
        try {
            // Configurar modelo base (Llama 3)
            await this.setupBaseModel();
            
            // Registrar modelos especializados
            await this.registerSpecializedModels();
            
            this.initialized = true;
            console.log('AIManager inicializado com sucesso');
        } catch (error) {
            console.error('Erro ao inicializar AIManager:', error);
            throw error;
        }
    }

    async setupBaseModel() {
        const modelPath = path.join(__dirname, '../../models/llama-3.gguf');
        
        if (!fs.existsSync(modelPath)) {
            throw new Error('Modelo base não encontrado. Execute setup_ai.js primeiro.');
        }

        const llama = new LLM(LLamaCpp);
        await llama.load({
            modelPath: modelPath,
            enableLogging: true,
            nCtx: this.config.models.llama3.context_length,
            seed: 0,
            f16Kv: false,
            logitsAll: false,
            vocabOnly: false,
            useMlock: false,
            embedding: false,
            useMmap: true,
            nGpuLayers: 0
        });

        this.models.set('llama3', {
            llm: llama,
            type: 'general',
            tasks: ['text_generation', 'summarization', 'analysis']
        });
    }

    async registerSpecializedModels() {
        const mistralPath = path.join(__dirname, '../../models/mistral.gguf');
        
        if (fs.existsSync(mistralPath)) {
            const llama = new LLM(LLamaCpp);
            await llama.load({
                modelPath: mistralPath,
                enableLogging: true,
                nCtx: this.config.models.mistral.context_length,
                seed: 0,
                f16Kv: false,
                logitsAll: false,
                vocabOnly: false,
                useMlock: false,
                embedding: false,
                useMmap: true,
                nGpuLayers: 0
            });

            this.models.set('mistral', {
                llm: llama,
                type: 'specialized',
                tasks: ['code_generation', 'code_review']
            });
        }
    }

    async processRequest(request) {
        if (!this.initialized) {
            throw new Error('AIManager não foi inicializado');
        }

        const taskType = this.analyzeTaskType(request);
        const modelInfo = this.selectBestModel(taskType);
        
        return await this.executeTask(modelInfo, request);
    }

    analyzeTaskType(request) {
        if (request.includes('código') || request.includes('programar')) {
            return 'code';
        }
        return 'text';
    }

    selectBestModel(taskType) {
        const modelInfo = taskType === 'code' && this.models.has('mistral') 
            ? this.models.get('mistral')
            : this.models.get('llama3');

        if (!modelInfo) {
            throw new Error('Nenhum modelo disponível para a tarefa');
        }

        return modelInfo;
    }

    async executeTask(modelInfo, request) {
        try {
            const { llm } = modelInfo;
            let response = '';

            await llm.createCompletion({
                nThreads: 4,
                nTokPredict: 2048,
                topK: 40,
                topP: 0.1,
                temp: 0.7,
                repeatPenalty: 1,
                prompt: request
            }, (token) => {
                response += token;
            });

            return response;
        } catch (error) {
            console.error('Erro ao executar tarefa:', error);
            throw error;
        }
    }

    async createText(prompt) {
        return this.processRequest(`A chat between a user and an assistant.
USER: ${prompt}
ASSISTANT:`);
    }

    async createAppointment(details) {
        return this.processRequest(`A chat between a user and an assistant.
USER: Create an appointment with these details: ${JSON.stringify(details)}
ASSISTANT:`);
    }

    async analyzeCode(code) {
        return this.processRequest(`A chat between a user and an assistant.
USER: Analyze this code:
${code}
ASSISTANT:`);
    }

    async cleanup() {
        for (const [_, modelInfo] of this.models) {
            if (modelInfo.llm) {
                // O llama-node não tem método de cleanup explícito
                modelInfo.llm = null;
            }
        }
        this.models.clear();
        this.initialized = false;
    }
}

module.exports = new AIManager(); 