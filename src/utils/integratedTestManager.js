const { createLogger } = require('./utils');
const testRunner = require('./testRunner');
const fs = require('fs');
const path = require('path');
const autoBackup = require('./autoBackup');
const notificationManager = require('./notificationManager');
const chokidar = require('chokidar');

const logger = createLogger('[IntegratedTest]');

class IntegratedTestManager {
    constructor() {
        this.testSuites = new Map();
        this.testResults = new Map();
        this.watchedFiles = new Set();
        this.isTestRunning = false;
        this.pendingChanges = new Set();
        this.autoSaveEnabled = true;
        this.watchers = new Map();
        this.baseDir = path.join(__dirname, '../..');
    }

    registerTestSuite(name, patterns, testFn) {
        this.testSuites.set(name, {
            patterns: Array.isArray(patterns) ? patterns : [patterns],
            testFn
        });

        // Configurar observador para cada padrão
        patterns.forEach(pattern => {
            const absolutePattern = path.join(this.baseDir, pattern);
            this.watchFiles(name, absolutePattern);
        });

        this.logger.info(`Suite de testes "${name}" registrada`);
    }

    watchFiles(suiteName, pattern) {
        try {
            const watcher = chokidar.watch(pattern, {
                persistent: true,
                ignoreInitial: true
            });

            watcher
                .on('change', async (path) => {
                    this.logger.info(`Arquivo alterado: ${path}`);
                    await this.runTestSuite(suiteName);
                })
                .on('error', error => {
                    this.logger.error(`Erro ao observar arquivos: ${error}`);
                });

            this.watchers.set(suiteName, watcher);
        } catch (error) {
            this.logger.error(`Erro ao configurar observador para ${pattern}:`, error);
        }
    }

    async runTestSuite(name) {
        const suite = this.testSuites.get(name);
        if (!suite) {
            this.logger.error(`Suite de testes "${name}" não encontrada`);
            return false;
        }

        try {
            this.logger.info(`Executando suite de testes "${name}"...`);
            await suite.testFn();
            this.logger.info(`Suite de testes "${name}" concluída com sucesso`);
            return true;
        } catch (error) {
            this.logger.error(`Erro ao executar suite de testes "${name}":`, error);
            return false;
        }
    }

    async runAllTests() {
        let success = true;
        for (const [name] of this.testSuites) {
            if (!await this.runTestSuite(name)) {
                success = false;
            }
        }
        return success;
    }

    stopWatching() {
        for (const [name, watcher] of this.watchers) {
            watcher.close();
            this.logger.info(`Observador para "${name}" encerrado`);
        }
        this.watchers.clear();
    }

    async handleFileChange(filePath) {
        // Salvar alteração automaticamente
        if (this.autoSaveEnabled) {
            await this.saveFile(filePath);
        }

        // Adicionar à lista de mudanças pendentes
        this.pendingChanges.add(filePath);

        // Agendar execução dos testes
        this.scheduleTestRun();
    }

    async saveFile(filePath) {
        try {
            // Implementar lógica de salvamento aqui
            await autoBackup.saveFile(filePath);
            logger.info(`Arquivo salvo: ${filePath}`);
        } catch (error) {
            logger.error(`Erro ao salvar arquivo ${filePath}:`, error);
        }
    }

    scheduleTestRun() {
        if (this.isTestRunning) return;

        // Executar testes após um pequeno delay para agrupar múltiplas mudanças
        setTimeout(async () => {
            await this.runAffectedTests();
        }, 1000);
    }

    async runAffectedTests() {
        if (this.isTestRunning) return;
        this.isTestRunning = true;

        try {
            const affectedSuites = this.getAffectedTestSuites();
            logger.info(`Executando ${affectedSuites.length} suites de teste afetadas`);

            for (const suite of affectedSuites) {
                await this.runTestSuite(suite.name);
            }

            // Notificar resultados dos testes
            const results = this.getTestResults();
            await notificationManager.notifyTestResults(results);

            // Limpar mudanças pendentes
            this.pendingChanges.clear();
        } catch (error) {
            logger.error('Erro ao executar testes:', error);
            await notificationManager.notifyError(`Erro ao executar testes: ${error.message}`);
        } finally {
            this.isTestRunning = false;
        }
    }

    getAffectedTestSuites() {
        const affectedSuites = [];
        const changedFiles = Array.from(this.pendingChanges);

        for (const [name, suite] of this.testSuites) {
            if (this.isSuiteAffected(suite, changedFiles)) {
                affectedSuites.push({ name, ...suite });
            }
        }

        return affectedSuites;
    }

    isSuiteAffected(suite, changedFiles) {
        if (!suite.patterns) return false;

        return changedFiles.some(file => {
            return suite.patterns.some(pattern => {
                if (pattern instanceof RegExp) {
                    return pattern.test(file);
                }
                return file.includes(pattern);
            });
        });
    }

    async runUITests(suite) {
        for (const test of suite.uiTests) {
            const results = await testRunner.runTestWithRetries(
                test.url,
                test.config
            );

            if (!results.success) {
                throw new Error(`Falha nos testes de UI: ${JSON.stringify(results.checks)}`);
            }
        }
    }

    async runIntegrationTests(suite) {
        for (const test of suite.integrationTests) {
            // Implementar testes de integração aqui
            // Por exemplo, testar comunicação entre módulos
        }
    }

    async runUnitTests(suite) {
        for (const test of suite.unitTests) {
            // Implementar testes unitários aqui
            // Por exemplo, testar funções individuais
        }
    }

    async attemptAutoFix(suite, error) {
        logger.info(`Tentando correção automática para ${suite.name}`);

        try {
            // Tentar correções específicas do tipo de erro
            if (error.type === 'ui') {
                await this.fixUIError(suite, error);
            } else if (error.type === 'integration') {
                await this.fixIntegrationError(suite, error);
            }

            // Executar testes novamente após correção
            await this.runTestSuite(suite.name);
        } catch (fixError) {
            logger.error(`Não foi possível corrigir automaticamente:`, fixError);
        }
    }

    async fixUIError(suite, error) {
        // Implementar correções de UI aqui
        // Por exemplo, ajustar estilos ou elementos
    }

    async fixIntegrationError(suite, error) {
        // Implementar correções de integração aqui
        // Por exemplo, ajustar configurações ou dependências
    }

    getTestResults() {
        const results = {
            total: this.testSuites.size,
            passed: 0,
            failed: 0,
            pending: 0,
            suites: {}
        };

        for (const [name, suite] of this.testSuites) {
            results.suites[name] = {
                status: suite.status,
                lastRun: suite.lastRun,
                files: suite.patterns
            };

            switch (suite.status) {
                case 'passed':
                    results.passed++;
                    break;
                case 'failed':
                    results.failed++;
                    break;
                default:
                    results.pending++;
            }
        }

        return results;
    }

    setAutoSave(enabled) {
        this.autoSaveEnabled = enabled;
    }
}

module.exports = new IntegratedTestManager(); 