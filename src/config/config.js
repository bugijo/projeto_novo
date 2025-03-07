const path = require('path');
const fs = require('fs');

class Config {
    constructor() {
        this.configPath = path.join(__dirname, '../../config.json');
        this.config = this.loadConfig();
    }

    loadConfig() {
        try {
            if (fs.existsSync(this.configPath)) {
                const data = fs.readFileSync(this.configPath, 'utf8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.error('Erro ao carregar configuração:', error);
        }

        // Configuração padrão
        return {
            assistant: {
                name: 'Assistente',
                voice: {
                    language: 'pt-BR',
                    model: 'base',
                    speaker: 'pt_br_female'
                }
            },
            ai: {
                model: 'phi',
                contextSize: 2048,
                temperature: 0.7,
                maxTokens: 1000
            },
            ui: {
                theme: 'dark',
                animations: true,
                fontSize: 14
            },
            cache: {
                enabled: true,
                maxSize: 100 * 1024 * 1024 // 100MB
            },
            plugins: {
                enabled: true,
                directory: path.join(__dirname, '../../plugins')
            }
        };
    }

    saveConfig() {
        try {
            fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
        } catch (error) {
            console.error('Erro ao salvar configuração:', error);
        }
    }

    get(key) {
        return key.split('.').reduce((obj, k) => obj && obj[k], this.config);
    }

    set(key, value) {
        const keys = key.split('.');
        const lastKey = keys.pop();
        const obj = keys.reduce((obj, k) => obj[k] = obj[k] || {}, this.config);
        obj[lastKey] = value;
        this.saveConfig();
    }

    reset() {
        this.config = this.loadConfig();
        this.saveConfig();
    }
}

const config = new Config();

module.exports = {
    config
}; 