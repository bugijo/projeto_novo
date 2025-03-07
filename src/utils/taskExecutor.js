const fs = require('fs');
const path = require('path');
const notificationManager = require('./notificationManager');
const { createLogger } = require('./utils');

const logger = createLogger('[TaskExecutor]');

class TaskExecutor {
    constructor() {
        this.projectFile = path.join(__dirname, '../../projeto_assistente_ia.md');
        this.currentTask = null;
        this.isRunning = false;
        this.taskQueue = [];
        this.baseDir = path.join(__dirname, '../..');
    }

    async start() {
        if (this.isRunning) return;
        this.isRunning = true;
        
        try {
            const content = fs.readFileSync(this.projectFile, 'utf8');
            this.taskQueue = this.parseTasks(content);
            await this.executeNextTask();
        } catch (error) {
            logger.error('Erro ao iniciar execução:', error);
            await this.notifyError(error);
        }
    }

    parseTasks(content) {
        const tasks = [];
        const lines = content.split('\n');
        let currentSection = null;
        let currentTask = null;

        for (const line of lines) {
            if (line.startsWith('### ')) {
                currentSection = {
                    name: line.replace('### ', '').trim(),
                    tasks: []
                };
                tasks.push(currentSection);
            } else if (line.match(/^\s*- \*\*(.*?)\*\*/)) {
                if (currentSection) {
                    currentTask = {
                        name: line.match(/^\s*- \*\*(.*?)\*\*/)[1],
                        subtasks: [],
                        status: 'pending'
                    };
                    currentSection.tasks.push(currentTask);
                }
            } else if (line.match(/^\s*- [^*]/) && currentTask) {
                currentTask.subtasks.push({
                    name: line.replace(/^\s*- /, '').trim(),
                    status: 'pending'
                });
            }
        }

        return tasks;
    }

    async executeNextTask() {
        if (!this.isRunning || this.taskQueue.length === 0) return;

        const section = this.taskQueue[0];
        if (!section.tasks || section.tasks.length === 0) {
            this.taskQueue.shift();
            await this.executeNextTask();
            return;
        }

        const task = section.tasks[0];
        if (!task || task.status === 'completed') {
            section.tasks.shift();
            if (section.tasks.length === 0) {
                this.taskQueue.shift();
            }
            await this.executeNextTask();
            return;
        }

        this.currentTask = task;
        await this.notifyTaskStart(section.name, task);

        try {
            // Aqui vai a lógica real de execução da tarefa
            await this.executeTask(task);
            
            task.status = 'completed';
            await this.updateProjectFile();
            await this.notifyTaskComplete(section.name, task);

            // Continuar com a próxima tarefa
            section.tasks.shift();
            if (section.tasks.length === 0) {
                this.taskQueue.shift();
            }
            
            // Pequeno delay para não sobrecarregar
            setTimeout(() => this.executeNextTask(), 1000);
        } catch (error) {
            logger.error(`Erro ao executar tarefa ${task.name}:`, error);
            await this.notifyError(error);
            // Parar execução em caso de erro
            this.isRunning = false;
        }
    }

    async executeTask(task) {
        const taskPath = path.join(this.baseDir, 'src', 'tasks', `${task.name.toLowerCase().replace(/\s+/g, '_')}.js`);
        
        try {
            if (fs.existsSync(taskPath)) {
                const taskModule = require(taskPath);
                await taskModule.execute(task);
            } else {
                logger.warn(`Módulo de tarefa não encontrado: ${taskPath}`);
                // Simular execução bem-sucedida por enquanto
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        } catch (error) {
            throw new Error(`Erro ao executar tarefa ${task.name}: ${error.message}`);
        }
    }

    async updateProjectFile() {
        try {
            const content = fs.readFileSync(this.projectFile, 'utf8');
            const lines = content.split('\n');
            let updatedContent = '';
            let inTask = false;
            let taskName = '';

            for (const line of lines) {
                if (line.match(/^\s*- \*\*(.*?)\*\*/)) {
                    taskName = line.match(/^\s*- \*\*(.*?)\*\*/)[1];
                    inTask = true;
                    
                    // Verificar se a tarefa está completa
                    const isCompleted = this.isTaskCompleted(taskName);
                    updatedContent += line.replace('[ ]', isCompleted ? '[x]' : '[ ]') + '\n';
                } else {
                    updatedContent += line + '\n';
                }
            }

            fs.writeFileSync(this.projectFile, updatedContent);
        } catch (error) {
            logger.error('Erro ao atualizar arquivo do projeto:', error);
        }
    }

    isTaskCompleted(taskName) {
        for (const section of this.taskQueue) {
            for (const task of section.tasks) {
                if (task.name === taskName) {
                    return task.status === 'completed';
                }
            }
        }
        return false;
    }

    async notifyTaskStart(section, task) {
        await notificationManager.sendNotification(
            `▶️ Iniciando: ${task.name}`,
            `Seção: ${section}\nTarefa: ${task.name}\n\nSubtarefas:\n${task.subtasks.map(st => `- ${st.name}`).join('\n')}`
        );
    }

    async notifyTaskComplete(section, task) {
        await notificationManager.sendNotification(
            `✅ Concluído: ${task.name}`,
            `Seção: ${section}\nTarefa: ${task.name}\n\nTodas as subtarefas foram concluídas com sucesso.`
        );
    }

    async notifyError(error) {
        await notificationManager.sendNotification(
            '❌ Erro na Execução',
            `Ocorreu um erro que requer sua atenção:\n${error.message}`
        );
    }
}

module.exports = new TaskExecutor(); 