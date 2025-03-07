const { LlamaModel, LlamaContext, LlamaChatSession } = require('@llama-node/core');
const { LlamaCpp } = require('@llama-node/llama-cpp');
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
            this.registerSpecializedModels();
            
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

        const model = new LlamaModel({
            modelPath: modelPath,
            contextSize: this.config.models.llama3.context_length,
            batchSize: 512,
            threads: 4
        });

        const context = new LlamaContext({ model });
        const session = new LlamaChatSession({ context });

        this.models.set('llama3', {
            model,
            context,
            session,
            type: 'general',
            tasks: ['text_generation', 'summarization', 'analysis']
        });
    }

    registerSpecializedModels() {
        const mistralPath = path.join(__dirname, '../../models/mistral.gguf');
        
        if (fs.existsSync(mistralPath)) {
            const model = new LlamaModel({
                modelPath: mistralPath,
                contextSize: this.config.models.mistral.context_length,
                batchSize: 512,
                threads: 4
            });

            const context = new LlamaContext({ model });
            const session = new LlamaChatSession({ context });

            this.models.set('mistral', {
                model,
                context,
                session,
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
        const selectedModel = this.selectBestModel(taskType);
        
        return await this.executeTask(selectedModel, request);
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
            const { session } = modelInfo;
            const response = await session.prompt(request);
            return response;
        } catch (error) {
            console.error('Erro ao executar tarefa:', error);
            throw error;
        }
    }

    async createText(prompt) {
        return this.processRequest(`Gerar texto: ${prompt}`);
    }

    async createAppointment(details) {
        return this.processRequest(`Criar compromisso: ${JSON.stringify(details)}`);
    }

    async analyzeCode(code) {
        return this.processRequest(`Analisar código: ${code}`);
    }

    async cleanup() {
        for (const [_, modelInfo] of this.models) {
            if (modelInfo.context) {
                await modelInfo.context.free();
            }
            if (modelInfo.model) {
                await modelInfo.model.free();
            }
        }
        this.models.clear();
        this.initialized = false;
    }
}

module.exports = new AIManager(); 