const { createLogger } = require('../utils/utils');
const path = require('path');
const fs = require('fs');

const logger = createLogger('[Config]');

class Config {
    constructor() {
        this.configPath = path.join(__dirname, '../../config/config.json');
        this.config = {};
    }

    async load() {
        try {
            if (fs.existsSync(this.configPath)) {
                this.config = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
            }
            logger.info('Configurações carregadas');
            return true;
        } catch (error) {
            logger.error('Erro ao carregar configurações:', error);
            return false;
        }
    }

    get(key) {
        return key.split('.').reduce((obj, k) => obj && obj[k], this.config);
    }

    set(key, value) {
        const keys = key.split('.');
        const last = keys.pop();
        const obj = keys.reduce((obj, k) => obj[k] = obj[k] || {}, this.config);
        obj[last] = value;
        this.save();
    }

    save() {
        try {
            fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
            logger.info('Configurações salvas');
            return true;
        } catch (error) {
            logger.error('Erro ao salvar configurações:', error);
            return false;
        }
    }
}

module.exports = {
    config: new Config()
}; 