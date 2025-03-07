const { createLlamaModel, createLlamaContext } = require('@llama-node/core');
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

        const model = await createLlamaModel({
            modelPath: modelPath,
            contextSize: this.config.models.llama3.context_length,
            batchSize: 512,
            threads: 4,
            backend: LlamaCpp
        });

        const context = await createLlamaContext({ model });
        
        this.models.set('llama3', {
            model,
            context,
            type: 'general',
            tasks: ['text_generation', 'summarization', 'analysis']
        });
    }

    async registerSpecializedModels() {
        const mistralPath = path.join(__dirname, '../../models/mistral.gguf');
        
        if (fs.existsSync(mistralPath)) {
            const model = await createLlamaModel({
                modelPath: mistralPath,
                contextSize: this.config.models.mistral.context_length,
                batchSize: 512,
                threads: 4,
                backend: LlamaCpp
            });

            const context = await createLlamaContext({ model });
            
            this.models.set('mistral', {
                model,
                context,
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
            const { context } = modelInfo;
            const response = await context.completion(request, {
                maxTokens: 2048,
                temperature: 0.7,
                topP: 0.9,
                stopSequences: ['</s>', '\n\n']
            });
            return response.text;
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