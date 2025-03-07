const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');

const MODELS_DIR = path.join(__dirname, '../models');
const CACHE_DIR = path.join(__dirname, '../cache');
const LOGS_DIR = path.join(__dirname, '../logs');

// URLs dos modelos (versões quantizadas para serem mais leves)
const MODEL_URLS = {
    'llama-3': 'https://huggingface.co/TheBloke/Llama-3-7B-GGUF/resolve/main/llama-3-7b.Q4_K_M.gguf',
    'mistral': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf'
};

// Criar diretórios necessários
function createDirectories() {
    [MODELS_DIR, CACHE_DIR, LOGS_DIR].forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
            console.log(`Diretório criado: ${dir}`);
        }
    });
}

// Baixar modelo
function downloadModel(modelName, url) {
    const modelPath = path.join(MODELS_DIR, `${modelName}.gguf`);
    
    if (fs.existsSync(modelPath)) {
        console.log(`Modelo ${modelName} já existe.`);
        return Promise.resolve();
    }

    console.log(`Baixando modelo ${modelName}...`);
    
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(modelPath);
        https.get(url, response => {
            response.pipe(file);
            file.on('finish', () => {
                file.close();
                console.log(`Modelo ${modelName} baixado com sucesso.`);
                resolve();
            });
        }).on('error', err => {
            fs.unlink(modelPath);
            reject(err);
        });
    });
}

// Instalar dependências
function installDependencies() {
    return new Promise((resolve, reject) => {
        console.log('Instalando dependências...');
        exec('npm install --save @llama-node/core @llama-node/llama-cpp --legacy-peer-deps', (error, stdout, stderr) => {
            if (error) {
                console.error('Erro ao instalar dependências:', error);
                reject(error);
                return;
            }
            console.log('Dependências instaladas com sucesso.');
            resolve();
        });
    });
}

// Função principal
async function setup() {
    try {
        // Criar diretórios
        createDirectories();

        // Instalar dependências
        await installDependencies();

        // Baixar modelos
        for (const [modelName, url] of Object.entries(MODEL_URLS)) {
            await downloadModel(modelName, url);
        }

        console.log('Setup concluído com sucesso!');
    } catch (error) {
        console.error('Erro durante o setup:', error);
        process.exit(1);
    }
}

// Executar setup
setup(); 