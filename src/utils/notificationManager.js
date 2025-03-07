const { createLogger } = require('./utils');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const logger = createLogger('[NotificationManager]');

class NotificationManager {
    constructor() {
        this.configPath = path.join(__dirname, '../../config/notification.json');
        this.config = this.loadConfig();
        this.totalTasks = 0;
        this.currentTask = 0;
    }

    loadConfig() {
        try {
            if (fs.existsSync(this.configPath)) {
                const config = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
                return config;
            }
        } catch (error) {
            logger.error('Erro ao carregar configuração de notificações:', error);
        }
        return { pushbulletToken: null };
    }

    saveConfig() {
        try {
            fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
        } catch (error) {
            logger.error('Erro ao salvar configuração de notificações:', error);
        }
    }

    setApiToken(token) {
        this.config.pushbulletToken = token;
        this.saveConfig();
    }

    async sendNotification(title, message) {
        if (!this.config.pushbulletToken) {
            logger.warn('Token do Pushbullet não configurado');
            return;
        }

        try {
            await axios.post('https://api.pushbullet.com/v2/pushes', {
                type: 'note',
                title: title,
                body: message
            }, {
                headers: {
                    'Access-Token': this.config.pushbulletToken,
                    'Content-Type': 'application/json'
                }
            });

            logger.info(`Notificação enviada: ${title}`);
        } catch (error) {
            logger.error('Erro ao enviar notificação:', error);
        }
    }

    setTotalTasks(total) {
        this.totalTasks = total;
        this.currentTask = 0;
    }

    async notifyTaskProgress(taskName) {
        this.currentTask++;
        await this.sendNotification(
            'Progresso do Projeto',
            `Item ${this.currentTask}/${this.totalTasks} implementado, testado e aprovado\n\nTarefa: ${taskName}`
        );
    }

    async notifyApprovalNeeded(description) {
        await this.sendNotification(
            'Aprovação Necessária',
            `Necessária sua aprovação para continuar\n\nDetalhes: ${description}`
        );
    }

    async notifyError(error) {
        await this.sendNotification(
            'Erro Detectado',
            `Ocorreu um erro que requer sua atenção:\n\n${error}`
        );
    }

    async notifyTestResults(results) {
        const summary = `
Resultados dos Testes:
✅ Passou: ${results.passed}
❌ Falhou: ${results.failed}
⏳ Pendente: ${results.pending}
        `.trim();

        await this.sendNotification('Resultados dos Testes', summary);
    }
}

module.exports = new NotificationManager(); 