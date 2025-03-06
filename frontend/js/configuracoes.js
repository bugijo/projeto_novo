// Gerenciador de configurações
const configManager = {
    init() {
        this.loadConfigs();
        this.bindEvents();
    },

    bindEvents() {
        // Alteração de idioma
        const languageSelect = document.querySelector('[name="language"]');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.updateConfig('language', e.target.value);
            });
        }

        // Alteração de tema
        const themeSelect = document.querySelector('[name="theme"]');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                this.updateConfig('theme', e.target.value);
                themeManager.setTheme(e.target.value);
            });
        }

        // Toggles de notificação e som
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateConfig(checkbox.name, e.target.checked);
            });
        });

        // Campos de API
        document.querySelectorAll('input[type="password"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateConfig(input.name, e.target.value);
            });
        });

        // Seleção de diretório
        const dirButton = document.querySelector('[data-action="select-dir"]');
        if (dirButton) {
            dirButton.addEventListener('click', () => {
                this.selectDirectory();
            });
        }

        // Botões de backup
        document.querySelector('[data-action="backup"]')?.addEventListener('click', () => {
            this.createBackup();
        });

        document.querySelector('[data-action="restore"]')?.addEventListener('click', () => {
            this.restoreBackup();
        });
    },

    loadConfigs() {
        const configs = this.getStoredConfigs();

        // Preenche os campos com as configurações salvas
        Object.entries(configs).forEach(([key, value]) => {
            const element = document.querySelector(`[name="${key}"]`);
            if (!element) return;

            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value;
            }
        });

        // Aplica o tema
        themeManager.setTheme(configs.theme || 'dark');
    },

    getStoredConfigs() {
        const defaultConfigs = {
            language: 'pt-br',
            theme: 'dark',
            notifications: true,
            sounds: true,
            projectsDir: '',
            editor: 'vscode',
            terminal: 'powershell'
        };

        try {
            return {
                ...defaultConfigs,
                ...JSON.parse(localStorage.getItem('configs') || '{}')
            };
        } catch {
            return defaultConfigs;
        }
    },

    updateConfig(key, value) {
        const configs = this.getStoredConfigs();
        configs[key] = value;
        localStorage.setItem('configs', JSON.stringify(configs));

        notifications.success('Configuração atualizada');
    },

    async selectDirectory() {
        try {
            // Simulação de seleção de diretório
            await this.simulateLoading();
            const dir = '/Users/exemplo/projetos';
            
            const input = document.querySelector('[name="projectsDir"]');
            if (input) {
                input.value = dir;
                this.updateConfig('projectsDir', dir);
            }
        } catch (error) {
            notifications.error('Erro ao selecionar diretório: ' + error.message);
        }
    },

    async createBackup() {
        try {
            await this.simulateLoading();
            
            const backup = {
                configs: this.getStoredConfigs(),
                date: new Date().toISOString()
            };

            const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `backup-${new Date().toISOString()}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            notifications.success('Backup criado com sucesso');
        } catch (error) {
            notifications.error('Erro ao criar backup: ' + error.message);
        }
    },

    async restoreBackup() {
        try {
            await this.simulateLoading();
            
            // Aqui seria implementada a lógica de restauração
            notifications.success('Backup restaurado com sucesso');
            this.loadConfigs();
        } catch (error) {
            notifications.error('Erro ao restaurar backup: ' + error.message);
        }
    },

    simulateLoading(time = 1500) {
        return new Promise(resolve => setTimeout(resolve, time));
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    configManager.init();
}); 