const { BrowserWindow, ipcMain } = require('electron');
const { createLogger } = require('./utils');
const path = require('path');
const fs = require('fs');
const testRunner = require('./testRunner');

const logger = createLogger('[PreviewManager]');

class PreviewManager {
    constructor() {
        this.previewWindow = null;
        this.currentFile = null;
        this.watchMode = false;
        this.lastUpdate = Date.now();
        this.updateDebounceTime = 500; // ms
    }

    async createPreviewWindow() {
        if (this.previewWindow) {
            return this.previewWindow;
        }

        this.previewWindow = new BrowserWindow({
            width: 800,
            height: 600,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                webSecurity: false
            },
            title: 'Preview - Cursor IDE'
        });

        // Adicionar controles de preview
        await this.previewWindow.loadFile(path.join(__dirname, '../ui/preview.html'));

        this.setupPreviewHandlers();

        return this.previewWindow;
    }

    setupPreviewHandlers() {
        this.previewWindow.webContents.on('did-finish-load', () => {
            this.refreshPreview();
        });

        // Atualização em tempo real
        if (this.watchMode && this.currentFile) {
            fs.watch(this.currentFile, (eventType) => {
                if (eventType === 'change' && Date.now() - this.lastUpdate > this.updateDebounceTime) {
                    this.refreshPreview();
                    this.lastUpdate = Date.now();
                }
            });
        }
    }

    async showPreview(filePath, options = {}) {
        this.currentFile = filePath;
        this.watchMode = options.watch || false;

        if (!this.previewWindow) {
            await this.createPreviewWindow();
        }

        await this.refreshPreview();

        if (options.runTests) {
            await this.runTests(options.testConfig);
        }
    }

    async refreshPreview() {
        if (!this.currentFile || !this.previewWindow) return;

        try {
            const content = fs.readFileSync(this.currentFile, 'utf8');
            
            // Injetar conteúdo no preview
            await this.previewWindow.webContents.executeJavaScript(`
                document.getElementById('preview-content').srcdoc = \`${content.replace(/`/g, '\\`')}\`;
            `);

        } catch (error) {
            logger.error('Erro ao atualizar preview:', error);
        }
    }

    async runTests(testConfig) {
        if (!testConfig) return;

        const results = await testRunner.runTestWithRetries(
            `file://${this.currentFile}`,
            testConfig
        );

        // Mostrar resultados no preview
        await this.showTestResults(results);

        return results;
    }

    async showTestResults(results) {
        if (!this.previewWindow) return;

        const resultsHtml = this.generateResultsHtml(results);

        await this.previewWindow.webContents.executeJavaScript(`
            document.getElementById('test-results').innerHTML = \`${resultsHtml}\`;
        `);
    }

    generateResultsHtml(results) {
        let html = '<div class="test-results">';
        
        if (results.success) {
            html += '<div class="success">✅ Todos os testes passaram!</div>';
        } else {
            html += '<div class="error">❌ Falhas encontradas:</div>';
            
            results.checks.forEach(check => {
                if (!check.success) {
                    html += `
                        <div class="failure">
                            <div class="message">${check.message}</div>
                            ${check.expected ? `<div class="expected">Esperado: ${check.expected}</div>` : ''}
                            ${check.actual ? `<div class="actual">Atual: ${check.actual}</div>` : ''}
                            ${check.autoCorrection ? `
                                <div class="correction">
                                    <button onclick="applyCorrection('${JSON.stringify(check.autoCorrection).replace(/'/g, "\\'")}')"
                                    >Aplicar Correção</button>
                                </div>
                            ` : ''}
                        </div>
                    `;
                }
            });
        }

        if (results.screenshots && results.screenshots.length > 0) {
            html += '<div class="screenshots">';
            results.screenshots.forEach(screenshot => {
                html += `<img src="${screenshot.data}" alt="Screenshot ${new Date(screenshot.timestamp).toLocaleString()}" />`;
            });
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    async applyCorrection(correction) {
        await testRunner.applyCorrection(correction);
        await this.refreshPreview();
        await this.runTests(this.lastTestConfig);
    }

    cleanup() {
        if (this.previewWindow) {
            this.previewWindow.close();
            this.previewWindow = null;
        }
    }
}

module.exports = new PreviewManager(); 