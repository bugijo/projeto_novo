// Gerenciador de assets de games
const gameAssetsManager = {
    init() {
        this.bindEvents();
        this.initCanvas3D();
    },

    bindEvents() {
        // Forms de criação
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const type = form.getAttribute('data-type');
                this.createAsset(type, new FormData(form));
            });
        });

        // Botões de visualização 3D
        document.querySelectorAll('[data-view-3d]').forEach(button => {
            button.addEventListener('click', () => {
                this.handle3DView(button.dataset.view3d);
            });
        });

        // Botões de exportação
        document.querySelectorAll('[data-export]').forEach(button => {
            button.addEventListener('click', () => {
                this.exportAsset(button.dataset.export);
            });
        });
    },

    async createAsset(type, formData) {
        try {
            const data = this.getFormData(type, formData);
            
            // Simula criação do asset
            await this.simulateLoading();
            
            notifications.success(`${type} criado com sucesso!`);
            this.updatePreview(type, data);
        } catch (error) {
            notifications.error(`Erro ao criar ${type}: ` + error.message);
        }
    },

    getFormData(type, formData) {
        switch (type) {
            case 'character':
                return {
                    name: formData.get('name'),
                    type: formData.get('type'),
                    attributes: {
                        strength: formData.get('strength'),
                        agility: formData.get('agility'),
                        intelligence: formData.get('intelligence')
                    }
                };
            case 'scenario':
                return {
                    name: formData.get('name'),
                    type: formData.get('type'),
                    elements: {
                        trees: formData.get('trees') === 'on',
                        rocks: formData.get('rocks') === 'on',
                        water: formData.get('water') === 'on'
                    },
                    weather: formData.get('weather')
                };
            case 'item':
                return {
                    name: formData.get('name'),
                    type: formData.get('type'),
                    attributes: {
                        damage: formData.get('damage'),
                        defense: formData.get('defense'),
                        durability: formData.get('durability')
                    },
                    rarity: formData.get('rarity')
                };
            default:
                return {};
        }
    },

    initCanvas3D() {
        const canvas = document.querySelector('#preview-3d');
        if (!canvas) return;

        // Aqui seria implementada a inicialização do Three.js ou outra biblioteca 3D
        console.log('Canvas 3D inicializado');
    },

    handle3DView(action) {
        switch (action) {
            case 'rotate':
                this.rotate3DView();
                break;
            case 'zoom':
                this.zoom3DView();
                break;
        }
    },

    rotate3DView() {
        // Implementação da rotação 3D
        notifications.success('Rotação aplicada');
    },

    zoom3DView() {
        // Implementação do zoom 3D
        notifications.success('Zoom aplicado');
    },

    async exportAsset(format) {
        try {
            await this.simulateLoading();
            notifications.success(`Asset exportado em formato ${format}`);
        } catch (error) {
            notifications.error('Erro na exportação: ' + error.message);
        }
    },

    updatePreview(type, data) {
        const previewContainer = document.querySelector('#preview-container');
        if (!previewContainer) return;

        // Atualiza a visualização do asset
        previewContainer.innerHTML = `
            <div class="p-4 bg-gray-700 rounded-lg">
                <h3 class="font-medium mb-2">${data.name}</h3>
                <div class="text-sm text-gray-400">Tipo: ${data.type}</div>
                ${this.renderAttributes(data.attributes)}
            </div>
        `;
    },

    renderAttributes(attributes) {
        if (!attributes) return '';
        
        return Object.entries(attributes)
            .map(([key, value]) => `
                <div class="flex justify-between text-sm">
                    <span class="text-gray-400">${key}:</span>
                    <span>${value}</span>
                </div>
            `).join('');
    },

    simulateLoading(time = 1500) {
        return new Promise(resolve => setTimeout(resolve, time));
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    gameAssetsManager.init();
}); 