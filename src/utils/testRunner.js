const { BrowserWindow } = require('electron');
const { createLogger } = require('./utils');
const path = require('path');
const fs = require('fs');

const logger = createLogger('[TestRunner]');

class TestRunner {
    constructor() {
        this.testWindow = null;
        this.testResults = new Map();
        this.autoCorrections = new Map();
        this.maxRetries = 3;
    }

    async createTestWindow() {
        this.testWindow = new BrowserWindow({
            width: 1024,
            height: 768,
            show: false, // Janela invisível para testes headless
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                webSecurity: false
            }
        });

        // Interceptar console.log da janela de teste
        this.testWindow.webContents.on('console-message', (event, level, message) => {
            logger.info(`[TestWindow] ${message}`);
        });

        return this.testWindow;
    }

    async runVisualTest(url, testConfig) {
        if (!this.testWindow) {
            await this.createTestWindow();
        }

        try {
            await this.testWindow.loadURL(url);
            
            // Esperar carregamento completo
            await this.testWindow.webContents.executeJavaScript(`
                new Promise(resolve => {
                    if (document.readyState === 'complete') {
                        resolve();
                    } else {
                        window.addEventListener('load', resolve);
                    }
                });
            `);

            // Executar testes visuais
            const results = await this.executeVisualTests(testConfig);
            return results;
        } catch (error) {
            logger.error('Erro no teste visual:', error);
            return { success: false, error: error.message };
        }
    }

    async executeVisualTests(config) {
        const results = {
            success: true,
            checks: [],
            screenshots: []
        };

        // Verificar elementos
        if (config.elements) {
            for (const element of config.elements) {
                const check = await this.checkElement(element);
                results.checks.push(check);
                if (!check.success) results.success = false;
            }
        }

        // Verificar estilos
        if (config.styles) {
            for (const style of config.styles) {
                const check = await this.checkStyle(style);
                results.checks.push(check);
                if (!check.success) results.success = false;
            }
        }

        // Capturar screenshots se necessário
        if (config.captureScreenshots) {
            const screenshot = await this.testWindow.capturePage();
            results.screenshots.push({
                timestamp: Date.now(),
                data: screenshot.toDataURL()
            });
        }

        return results;
    }

    async checkElement(elementConfig) {
        const { selector, shouldExist = true, content } = elementConfig;

        const exists = await this.testWindow.webContents.executeJavaScript(`
            !!document.querySelector('${selector}')
        `);

        if (exists !== shouldExist) {
            return {
                success: false,
                message: `Elemento ${selector} ${shouldExist ? 'não encontrado' : 'não deveria existir'}`,
                autoCorrection: this.getAutoCorrection('element', elementConfig)
            };
        }

        if (content && exists) {
            const actualContent = await this.testWindow.webContents.executeJavaScript(`
                document.querySelector('${selector}').textContent
            `);

            if (actualContent !== content) {
                return {
                    success: false,
                    message: `Conteúdo incorreto para ${selector}`,
                    expected: content,
                    actual: actualContent,
                    autoCorrection: this.getAutoCorrection('content', { selector, expected: content, actual: actualContent })
                };
            }
        }

        return { success: true };
    }

    async checkStyle(styleConfig) {
        const { selector, properties } = styleConfig;

        const styles = await this.testWindow.webContents.executeJavaScript(`
            const element = document.querySelector('${selector}');
            if (!element) return null;
            const computed = window.getComputedStyle(element);
            const result = {};
            ${Object.keys(properties).map(prop => `
                result['${prop}'] = computed.getPropertyValue('${prop}');
            `).join('')}
            result;
        `);

        if (!styles) {
            return {
                success: false,
                message: `Elemento ${selector} não encontrado para verificação de estilos`,
                autoCorrection: this.getAutoCorrection('style', styleConfig)
            };
        }

        const failures = [];
        for (const [prop, expected] of Object.entries(properties)) {
            if (styles[prop] !== expected) {
                failures.push({
                    property: prop,
                    expected,
                    actual: styles[prop]
                });
            }
        }

        if (failures.length > 0) {
            return {
                success: false,
                message: 'Estilos incorretos',
                failures,
                autoCorrection: this.getAutoCorrection('style', { selector, failures })
            };
        }

        return { success: true };
    }

    getAutoCorrection(type, config) {
        switch (type) {
            case 'element':
                return {
                    type: 'element',
                    fix: `Adicionar elemento: ${config.selector}`,
                    code: this.generateElementCorrection(config)
                };
            case 'content':
                return {
                    type: 'content',
                    fix: `Corrigir conteúdo de ${config.selector}`,
                    code: this.generateContentCorrection(config)
                };
            case 'style':
                return {
                    type: 'style',
                    fix: `Corrigir estilos de ${config.selector}`,
                    code: this.generateStyleCorrection(config)
                };
            default:
                return null;
        }
    }

    generateElementCorrection(config) {
        return {
            selector: config.selector,
            html: `<div class="${config.selector.replace('.', '')}">${config.content || ''}</div>`
        };
    }

    generateContentCorrection(config) {
        return {
            selector: config.selector,
            content: config.expected
        };
    }

    generateStyleCorrection(config) {
        const corrections = {};
        config.failures.forEach(failure => {
            corrections[failure.property] = failure.expected;
        });
        return {
            selector: config.selector,
            styles: corrections
        };
    }

    async applyCorrections(corrections) {
        for (const correction of corrections) {
            try {
                await this.applyCorrection(correction);
            } catch (error) {
                logger.error(`Erro ao aplicar correção:`, error);
            }
        }
    }

    async applyCorrection(correction) {
        switch (correction.type) {
            case 'element':
                await this.testWindow.webContents.executeJavaScript(`
                    const parent = document.body;
                    parent.insertAdjacentHTML('beforeend', '${correction.code.html}');
                `);
                break;
            case 'content':
                await this.testWindow.webContents.executeJavaScript(`
                    const element = document.querySelector('${correction.code.selector}');
                    if (element) element.textContent = '${correction.code.content}';
                `);
                break;
            case 'style':
                await this.testWindow.webContents.executeJavaScript(`
                    const element = document.querySelector('${correction.code.selector}');
                    if (element) {
                        ${Object.entries(correction.code.styles)
                            .map(([prop, value]) => `element.style.${prop} = '${value}';`)
                            .join('\n')}
                    }
                `);
                break;
        }
    }

    async runTestWithRetries(url, testConfig) {
        let attempts = 0;
        let lastResult;

        while (attempts < this.maxRetries) {
            lastResult = await this.runVisualTest(url, testConfig);
            
            if (lastResult.success) {
                return lastResult;
            }

            // Tentar correções automáticas
            if (lastResult.checks.some(check => check.autoCorrection)) {
                const corrections = lastResult.checks
                    .filter(check => check.autoCorrection)
                    .map(check => check.autoCorrection);
                
                await this.applyCorrections(corrections);
                attempts++;
            } else {
                break;
            }
        }

        return lastResult;
    }

    cleanup() {
        if (this.testWindow) {
            this.testWindow.close();
            this.testWindow = null;
        }
    }
}

module.exports = new TestRunner(); 