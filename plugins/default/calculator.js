class CalculatorPlugin {
    constructor() {
        this.name = 'calculator';
        this.description = 'Plugin de calculadora básica';
        this.version = '1.0.0';
    }

    initialize() {
        console.log('Plugin de calculadora inicializado');
        return true;
    }

    calculate(expression) {
        try {
            // Remover caracteres inválidos
            expression = expression.replace(/[^0-9+\-*/().]/g, '');
            
            // Avaliar expressão
            return eval(expression);
        } catch (error) {
            console.error('Erro ao calcular expressão:', error);
            return null;
        }
    }

    // Comandos suportados
    commands = {
        'calcular': (args) => {
            const expression = args.join(' ');
            const result = this.calculate(expression);
            return result !== null ? `O resultado é: ${result}` : 'Expressão inválida';
        },
        
        'ajuda': () => {
            return `
                Comandos disponíveis:
                - calcular [expressão]: Calcula uma expressão matemática
                - ajuda: Mostra esta mensagem de ajuda
            `;
        }
    };

    // Processar comando
    async processCommand(command, args) {
        if (this.commands[command]) {
            return this.commands[command](args);
        }
        return 'Comando não reconhecido. Use "ajuda" para ver os comandos disponíveis.';
    }
}

module.exports = new CalculatorPlugin(); 