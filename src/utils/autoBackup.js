const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { workspace } = require('electron');

class AutoBackup {
    constructor() {
        this.lastBackup = Date.now();
        this.backupInterval = 5 * 60 * 1000; // 5 minutos
        this.autoSaveInterval = 30 * 1000; // 30 segundos
        this.watchedFiles = new Set();
    }

    async performBackup() {
        // Primeiro salva todos os arquivos
        await this.saveAllFiles();

        const commands = [
            'git add .',
            'git commit -m "Backup automático: ' + new Date().toLocaleString() + '"',
            'git push origin main'
        ];

        for (const cmd of commands) {
            try {
                await this.executeCommand(cmd);
            } catch (error) {
                console.error(`Erro ao executar ${cmd}:`, error);
                return false;
            }
        }

        this.lastBackup = Date.now();
        return true;
    }

    executeCommand(command) {
        return new Promise((resolve, reject) => {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve(stdout);
            });
        });
    }

    watchFile(filePath) {
        if (this.watchedFiles.has(filePath)) return;
        
        this.watchedFiles.add(filePath);
        fs.watch(filePath, async (eventType, filename) => {
            if (eventType === 'change') {
                await this.saveFile(filePath);
            }
        });
    }

    async saveFile(filePath) {
        try {
            // Aqui implementaríamos a lógica de salvamento específica
            // Por enquanto, vamos apenas registrar
            console.log(`Arquivo salvo automaticamente: ${filePath}`);
        } catch (error) {
            console.error(`Erro ao salvar arquivo ${filePath}:`, error);
        }
    }

    async saveAllFiles() {
        for (const filePath of this.watchedFiles) {
            await this.saveFile(filePath);
        }
    }

    startWatching() {
        // Auto-save a cada 30 segundos
        setInterval(async () => {
            await this.saveAllFiles();
        }, this.autoSaveInterval);

        // Backup a cada 5 minutos
        setInterval(async () => {
            const now = Date.now();
            if (now - this.lastBackup >= this.backupInterval) {
                await this.performBackup();
            }
        }, 60000);
    }
}

module.exports = new AutoBackup(); 