const notificationManager = require('./src/utils/notificationManager');

async function testNotification() {
    try {
        await notificationManager.sendNotification(
            '🎯 Iniciando Primeira Tarefa',
            `Começando: Configuração do Sistema Base

Tarefa atual: Ollama Setup
- Instalação do Ollama
- Configuração do ambiente
- Testes de conexão
- Integração com o sistema

Progress: 1/11 seções principais
Status: Em andamento

Você será notificado quando esta etapa for concluída ou se precisar de sua aprovação.`
        );
        console.log('Notificação enviada com sucesso!');
    } catch (error) {
        console.error('Erro ao enviar notificação:', error);
    }
}

testNotification(); 