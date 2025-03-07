const fs = require('fs');
const path = require('path');
const { createLogger } = require('./utils');
const cursorConfig = require('./cursorConfig');

const logger = createLogger('[TaskManager]');

class TaskManager {
    constructor() {
        this.taskQueuePath = path.join(__dirname, '../../.cursor/taskQueue.json');
        this.tasksInProgress = new Set();
        this.taskQueue = this.loadTaskQueue();
    }

    loadTaskQueue() {
        try {
            if (fs.existsSync(this.taskQueuePath)) {
                return JSON.parse(fs.readFileSync(this.taskQueuePath, 'utf8'));
            }
        } catch (error) {
            logger.warn('Erro ao carregar fila de tarefas:', error);
        }
        return {
            tasks: [],
            currentTask: null,
            lastExecutionPoint: null,
            approved: false
        };
    }

    saveTaskQueue() {
        try {
            fs.writeFileSync(this.taskQueuePath, JSON.stringify(this.taskQueue, null, 4));
        } catch (error) {
            logger.error('Erro ao salvar fila de tarefas:', error);
        }
    }

    addTask(task) {
        this.taskQueue.tasks.push({
            id: Date.now(),
            ...task,
            status: 'pending',
            progress: 0,
            error: null
        });
        this.saveTaskQueue();
    }

    addBulkTasks(tasks, approvalToken) {
        this.taskQueue = {
            tasks: tasks.map((task, index) => ({
                id: Date.now() + index,
                ...task,
                status: 'pending',
                progress: 0,
                error: null
            })),
            currentTask: null,
            lastExecutionPoint: null,
            approved: true,
            approvalToken
        };
        this.saveTaskQueue();
    }

    async executeNextTask() {
        if (!this.taskQueue.approved) return;

        const pendingTask = this.taskQueue.tasks.find(t => t.status === 'pending');
        if (!pendingTask) return;

        try {
            pendingTask.status = 'in_progress';
            this.saveTaskQueue();

            // Executa a tarefa
            await this.executeTask(pendingTask);

            pendingTask.status = 'completed';
            pendingTask.progress = 100;
        } catch (error) {
            pendingTask.status = 'error';
            pendingTask.error = error.message;
            logger.error(`Erro na tarefa ${pendingTask.id}:`, error);
        }

        this.saveTaskQueue();
        this.continueTasks();
    }

    async executeTask(task) {
        switch (task.type) {
            case 'file_edit':
                await this.executeFileEdit(task);
                break;
            case 'file_create':
                await this.executeFileCreate(task);
                break;
            case 'file_delete':
                await this.executeFileDelete(task);
                break;
            case 'command':
                await this.executeCommand(task);
                break;
            default:
                throw new Error(`Tipo de tarefa desconhecido: ${task.type}`);
        }
    }

    async executeFileEdit(task) {
        const { filePath, content, mode = 'append' } = task;
        try {
            if (mode === 'append') {
                await fs.promises.appendFile(filePath, content);
            } else {
                await fs.promises.writeFile(filePath, content);
            }
        } catch (error) {
            throw new Error(`Erro ao editar arquivo ${filePath}: ${error.message}`);
        }
    }

    async executeFileCreate(task) {
        const { filePath, content } = task;
        try {
            await fs.promises.writeFile(filePath, content);
        } catch (error) {
            throw new Error(`Erro ao criar arquivo ${filePath}: ${error.message}`);
        }
    }

    async executeFileDelete(task) {
        const { filePath } = task;
        try {
            await fs.promises.unlink(filePath);
        } catch (error) {
            throw new Error(`Erro ao deletar arquivo ${filePath}: ${error.message}`);
        }
    }

    async executeCommand(task) {
        const { command } = task;
        // Implementar execução de comando aqui
        // Por segurança, isso requer implementação específica
    }

    continueTasks() {
        if (this.taskQueue.tasks.some(t => t.status === 'pending')) {
            setImmediate(() => this.executeNextTask());
        }
    }

    getProgress() {
        const total = this.taskQueue.tasks.length;
        const completed = this.taskQueue.tasks.filter(t => t.status === 'completed').length;
        return {
            total,
            completed,
            percentage: total ? (completed / total) * 100 : 0,
            currentTask: this.taskQueue.currentTask,
            tasks: this.taskQueue.tasks
        };
    }

    clearCompletedTasks() {
        this.taskQueue.tasks = this.taskQueue.tasks.filter(t => t.status !== 'completed');
        this.saveTaskQueue();
    }
}

module.exports = new TaskManager(); 