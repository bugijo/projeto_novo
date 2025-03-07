const fs = require('fs');
const path = require('path');
const { createLogger } = require('../utils/utils');

class PluginManager {
    constructor() {
        this.logger = createLogger('[PluginManager]');
        this.pluginsDir = path.join(__dirname, '../../plugins');
        this.plugins = new Map();
    }

    async initialize() {
        try {
            // Criar diretório de plugins se não existir
            if (!fs.existsSync(this.pluginsDir)) {
                fs.mkdirSync(this.pluginsDir, { recursive: true });
            }

            // Carregar plugins
            await this.loadPlugins();
            
            this.logger.info('Sistema de plugins inicializado com sucesso');
            return true;
        } catch (error) {
            this.logger.error('Erro ao inicializar sistema de plugins:', error);
            throw error;
        }
    }

    async loadPlugins() {
        try {
            const files = fs.readdirSync(this.pluginsDir);
            
            for (const file of files) {
                if (file.endsWith('.js')) {
                    const pluginPath = path.join(this.pluginsDir, file);
                    const plugin = require(pluginPath);
                    
                    if (plugin.name && plugin.initialize) {
                        await plugin.initialize();
                        this.plugins.set(plugin.name, plugin);
                        this.logger.info(`Plugin carregado: ${plugin.name}`);
                    }
                }
            }
        } catch (error) {
            this.logger.error('Erro ao carregar plugins:', error);
        }
    }

    getPlugin(name) {
        return this.plugins.get(name);
    }

    async executePlugin(name, ...args) {
        const plugin = this.getPlugin(name);
        if (plugin && plugin.execute) {
            try {
                return await plugin.execute(...args);
            } catch (error) {
                this.logger.error(`Erro ao executar plugin ${name}:`, error);
                throw error;
            }
        }
        return null;
    }
}

module.exports = new PluginManager(); 