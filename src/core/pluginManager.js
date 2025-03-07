const fs = require('fs');
const path = require('path');
const { config } = require('../config/config');
const { createLogger } = require('../utils/utils');

class PluginManager {
    constructor() {
        this.plugins = new Map();
        this.logger = createLogger('[PluginManager]');
        this.pluginsDir = config.get('plugins.directory');
    }

    async initialize() {
        try {
            // Verificar se o diretório de plugins existe
            if (!fs.existsSync(this.pluginsDir)) {
                fs.mkdirSync(this.pluginsDir, { recursive: true });
            }

            // Carregar plugins
            await this.loadPlugins();

            this.logger.info(`${this.plugins.size} plugins carregados`);
            return true;
        } catch (error) {
            this.logger.error('Erro ao inicializar PluginManager:', error);
            return false;
        }
    }

    async loadPlugins() {
        try {
            // Carregar plugins do diretório padrão
            const defaultPluginsDir = path.join(this.pluginsDir, 'default');
            if (fs.existsSync(defaultPluginsDir)) {
                const files = fs.readdirSync(defaultPluginsDir);
                
                for (const file of files) {
                    if (file.endsWith('.js')) {
                        await this.loadPlugin(path.join(defaultPluginsDir, file));
                    }
                }
            }

            // Carregar plugins de terceiros
            const dirs = fs.readdirSync(this.pluginsDir);
            for (const dir of dirs) {
                if (dir === 'default') continue;

                const pluginDir = path.join(this.pluginsDir, dir);
                if (fs.statSync(pluginDir).isDirectory()) {
                    const mainFile = path.join(pluginDir, 'index.js');
                    if (fs.existsSync(mainFile)) {
                        await this.loadPlugin(mainFile);
                    }
                }
            }
        } catch (error) {
            this.logger.error('Erro ao carregar plugins:', error);
        }
    }

    async loadPlugin(pluginPath) {
        try {
            const plugin = require(pluginPath);

            // Verificar se o plugin tem a interface necessária
            if (!plugin.name || !plugin.initialize || !plugin.processCommand) {
                throw new Error('Plugin inválido: interface incompleta');
            }

            // Inicializar plugin
            await plugin.initialize();

            // Registrar plugin
            this.plugins.set(plugin.name, plugin);
            this.logger.info(`Plugin "${plugin.name}" carregado com sucesso`);
        } catch (error) {
            this.logger.error(`Erro ao carregar plugin ${pluginPath}:`, error);
        }
    }

    async processCommand(command, args) {
        for (const [name, plugin] of this.plugins) {
            try {
                const result = await plugin.processCommand(command, args);
                if (result) {
                    return {
                        success: true,
                        plugin: name,
                        result
                    };
                }
            } catch (error) {
                this.logger.error(`Erro ao processar comando no plugin ${name}:`, error);
            }
        }

        return {
            success: false,
            error: 'Nenhum plugin pode processar o comando'
        };
    }

    getPluginInfo() {
        return Array.from(this.plugins.values()).map(plugin => ({
            name: plugin.name,
            description: plugin.description,
            version: plugin.version
        }));
    }

    async unloadPlugin(name) {
        if (this.plugins.has(name)) {
            const plugin = this.plugins.get(name);
            if (plugin.cleanup) {
                await plugin.cleanup();
            }
            this.plugins.delete(name);
            this.logger.info(`Plugin "${name}" descarregado`);
            return true;
        }
        return false;
    }

    async reloadPlugin(name) {
        if (await this.unloadPlugin(name)) {
            // Limpar cache do require para o plugin
            const pluginPath = require.resolve(path.join(this.pluginsDir, name));
            delete require.cache[pluginPath];
            
            // Recarregar plugin
            await this.loadPlugin(pluginPath);
            return true;
        }
        return false;
    }
}

const pluginManager = new PluginManager();

module.exports = {
    pluginManager
}; 