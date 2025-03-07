const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Funções de manipulação de arquivos
function ensureDirectoryExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function readJsonFile(filePath, defaultValue = null) {
    try {
        if (fs.existsSync(filePath)) {
            const data = fs.readFileSync(filePath, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error(`Erro ao ler arquivo ${filePath}:`, error);
    }
    return defaultValue;
}

function writeJsonFile(filePath, data) {
    try {
        const dirPath = path.dirname(filePath);
        ensureDirectoryExists(dirPath);
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        return true;
    } catch (error) {
        console.error(`Erro ao escrever arquivo ${filePath}:`, error);
        return false;
    }
}

// Funções de cache
function generateCacheKey(data) {
    return crypto
        .createHash('md5')
        .update(JSON.stringify(data))
        .digest('hex');
}

// Funções de formatação
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

function formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
        return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    }
    if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
}

// Funções de validação
function isValidJson(str) {
    try {
        JSON.parse(str);
        return true;
    } catch (error) {
        return false;
    }
}

// Funções de debounce e throttle
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Funções de log
function createLogger(prefix) {
    return {
        info: (message, ...args) => console.log(`${prefix}:`, message, ...args),
        error: (message, ...args) => console.error(`${prefix}:`, message, ...args),
        warn: (message, ...args) => console.warn(`${prefix}:`, message, ...args),
        debug: (message, ...args) => console.debug(`${prefix}:`, message, ...args)
    };
}

module.exports = {
    // File utils
    ensureDirectoryExists,
    readJsonFile,
    writeJsonFile,
    
    // Cache utils
    generateCacheKey,
    
    // Format utils
    formatBytes,
    formatDuration,
    
    // Validation utils
    isValidJson,
    
    // Function utils
    debounce,
    throttle,
    
    // Logging utils
    createLogger
}; 