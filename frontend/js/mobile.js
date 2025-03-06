// Gerenciador de projetos mobile
const mobileProjectManager = {
    init() {
        this.bindEvents();
        this.loadRecentProjects();
    },

    bindEvents() {
        // Form de criação de projeto
        const createForm = document.querySelector('form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createProject(new FormData(createForm));
            });
        }

        // Botões de emulador
        document.querySelectorAll('[data-emulator]').forEach(button => {
            button.addEventListener('click', () => {
                this.startEmulator(button.dataset.emulator);
            });
        });

        // Botões de build
        document.querySelectorAll('[data-build]').forEach(button => {
            button.addEventListener('click', () => {
                this.buildProject(button.dataset.build);
            });
        });
    },

    async createProject(formData) {
        try {
            const data = {
                name: formData.get('name'),
                framework: formData.get('framework'),
                template: formData.get('template'),
                platforms: {
                    android: formData.get('android') === 'on',
                    ios: formData.get('ios') === 'on'
                }
            };

            // Simula criação do projeto
            await this.simulateLoading();
            
            notifications.success('Projeto criado com sucesso!');
            this.loadRecentProjects();
        } catch (error) {
            notifications.error('Erro ao criar projeto: ' + error.message);
        }
    },

    async startEmulator(type) {
        try {
            await this.simulateLoading();
            notifications.success(`Emulador ${type} iniciado`);
        } catch (error) {
            notifications.error('Erro ao iniciar emulador: ' + error.message);
        }
    },

    async buildProject(platform) {
        try {
            await this.simulateLoading();
            notifications.success(`Build para ${platform} concluído`);
        } catch (error) {
            notifications.error('Erro no build: ' + error.message);
        }
    },

    loadRecentProjects() {
        // Simulação de projetos recentes
        const projects = [
            { name: 'App Delivery', framework: 'Flutter', lastModified: new Date() },
            { name: 'Social Media', framework: 'React Native', lastModified: new Date() }
        ];

        const container = document.querySelector('#recent-projects');
        if (container) {
            container.innerHTML = projects.map(project => `
                <div class="p-4 bg-gray-700 rounded-lg">
                    <div class="font-medium">${project.name}</div>
                    <div class="text-sm text-gray-400">${project.framework}</div>
                    <div class="text-xs text-gray-500">${utils.formatDate(project.lastModified)}</div>
                </div>
            `).join('');
        }
    },

    simulateLoading(time = 1500) {
        return new Promise(resolve => setTimeout(resolve, time));
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    mobileProjectManager.init();
}); 