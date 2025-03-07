const fs = require('fs');
const path = require('path');
const { createLogger } = require('./utils');

const logger = createLogger('[CursorConfig]');

class CursorConfig {
    constructor() {
        this.configPath = path.join(__dirname, '../../.cursor/settings.json');
        this.config = this.loadConfig();
    }

    loadConfig() {
        try {
            const configData = fs.readFileSync(this.configPath, 'utf8');
            return JSON.parse(configData);
        } catch (error) {
            logger.warn('Erro ao carregar configurações do Cursor, usando padrões:', error);
            return this.getDefaultConfig();
        }
    }

    getDefaultConfig() {
        return {
            maxLinesPerView: 1000,
            maxSearchResults: 500,
            disableLineLimits: true,
            commands: {
                read_file: {
                    maxLines: 1000,
                    requireApproval: false
                },
                list_dir: {
                    maxResults: 500,
                    requireApproval: false
                },
                grep_search: {
                    maxResults: 500,
                    requireApproval: false
                },
                file_search: {
                    maxResults: 500,
                    requireApproval: false
                },
                edit_file: {
                    maxLines: 1000,
                    requireApproval: false
                }
            }
        };
    }

    getCommandConfig(commandName) {
        return this.config.commands[commandName] || {};
    }

    shouldRequireApproval(commandName) {
        const cmdConfig = this.getCommandConfig(commandName);
        return cmdConfig.requireApproval !== false;
    }

    getMaxLines(commandName) {
        const cmdConfig = this.getCommandConfig(commandName);
        return cmdConfig.maxLines || this.config.maxLinesPerView || 1000;
    }

    getMaxResults(commandName) {
        const cmdConfig = this.getCommandConfig(commandName);
        return cmdConfig.maxResults || this.config.maxSearchResults || 500;
    }

    isLineLimitDisabled() {
        return this.config.disableLineLimits === true;
    }

    updateConfig(newConfig) {
        try {
            this.config = { ...this.config, ...newConfig };
            fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 4));
            return true;
        } catch (error) {
            logger.error('Erro ao atualizar configurações:', error);
            return false;
        }
    }
}

module.exports = new CursorConfig(); 