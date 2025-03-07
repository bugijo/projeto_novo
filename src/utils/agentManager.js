const { createLogger } = require('./utils');
const taskManager = require('./taskManager');

const logger = createLogger('[AgentManager]');

class AgentManager {
    constructor() {
        this.agents = new Map();
        this.maxAgents = 5;
        this.taskChunks = new Map();
    }

    createAgent(agentId, taskType) {
        const agent = {
            id: agentId,
            type: taskType,
            status: 'idle',
            currentTask: null,
            completedTasks: 0
        };
        this.agents.set(agentId, agent);
        return agent;
    }

    async planTasks(taskList, context) {
        // Divide as tarefas em chunks menores
        const chunks = this.chunkTasks(taskList);
        const planId = Date.now().toString();
        
        this.taskChunks.set(planId, {
            chunks,
            context,
            currentChunk: 0,
            status: 'planned'
        });

        return planId;
    }

    chunkTasks(taskList) {
        const chunkSize = 20; // Tamanho ideal para cada chunk
        const chunks = [];
        
        for (let i = 0; i < taskList.length; i += chunkSize) {
            chunks.push(taskList.slice(i, i + chunkSize));
        }
        
        return chunks;
    }

    async executePlan(planId) {
        const plan = this.taskChunks.get(planId);
        if (!plan) throw new Error('Plano não encontrado');

        plan.status = 'executing';
        
        while (plan.currentChunk < plan.chunks.length) {
            const chunk = plan.chunks[plan.currentChunk];
            const availableAgent = this.getAvailableAgent();

            if (availableAgent) {
                this.assignTasksToAgent(availableAgent, chunk, plan.context);
                plan.currentChunk++;
            } else {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }

    getAvailableAgent() {
        for (const [id, agent] of this.agents) {
            if (agent.status === 'idle') return agent;
        }

        if (this.agents.size < this.maxAgents) {
            return this.createAgent(`agent_${this.agents.size + 1}`, 'general');
        }

        return null;
    }

    async assignTasksToAgent(agent, tasks, context) {
        agent.status = 'busy';
        agent.currentTask = tasks[0];

        try {
            // Adiciona as tarefas ao gerenciador de tarefas
            taskManager.addBulkTasks(tasks, context.approvalToken);
            
            // Inicia a execução
            await taskManager.executeNextTask();

            agent.completedTasks += tasks.length;
        } catch (error) {
            logger.error(`Erro no agente ${agent.id}:`, error);
        } finally {
            agent.status = 'idle';
            agent.currentTask = null;
        }
    }

    getProgress(planId) {
        const plan = this.taskChunks.get(planId);
        if (!plan) return null;

        const totalChunks = plan.chunks.length;
        const completedChunks = plan.currentChunk;
        
        return {
            planId,
            status: plan.status,
            progress: (completedChunks / totalChunks) * 100,
            completedChunks,
            totalChunks,
            activeAgents: Array.from(this.agents.values())
                .filter(a => a.status === 'busy').length
        };
    }

    cancelPlan(planId) {
        const plan = this.taskChunks.get(planId);
        if (plan) {
            plan.status = 'cancelled';
            // Limpa as tarefas pendentes
            taskManager.clearCompletedTasks();
        }
    }
}

module.exports = new AgentManager(); 