# DevAssistant IDE

Um IDE moderno e poderoso com suporte a múltiplas linguagens e assistente IA integrado.

## Características

- 🚀 Interface moderna e intuitiva
- 🤖 Assistente IA integrado
- 🔍 Debugging avançado
- 🧩 Sistema de extensões
- 📝 Editor com syntax highlighting
- ⚡ Terminal integrado
- 🔄 Controle de versão Git
- 🎨 Temas personalizáveis
- 🔧 Altamente configurável

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/devassistant-ide.git
cd devassistant-ide
```

2. Crie um ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Inicie a interface web:
```bash
python app.py
```

2. Acesse http://localhost:5000 no navegador

3. Clique no botão "Abrir DevAssistant IDE" para iniciar o IDE

## Funcionalidades Principais

### Editor

- Syntax highlighting para múltiplas linguagens
- Auto-completar inteligente
- Formatação automática
- Múltiplos cursores
- Minimap
- Dobramento de código
- Busca e substituição avançada

### Debug

- Breakpoints condicionais
- Step-by-step debugging
- Inspeção de variáveis
- Console de debug
- Pilha de chamadas
- Expressões watch

### Terminal Integrado

- Múltiplas sessões
- Auto-completar
- Histórico de comandos
- Integração com shells do sistema

### Controle de Versão

- Integração Git
- Visualização de diferenças
- Histórico de commits
- Branches e merges
- Resolução de conflitos

### Extensões

- Marketplace de extensões
- Instalação/desinstalação fácil
- Atualizações automáticas
- Configuração por extensão

### Assistente IA

- Sugestões de código
- Explicação de código
- Refatoração automática
- Geração de testes
- Documentação automática

## Configuração

O IDE pode ser configurado através do arquivo `ide_config.py`. As principais configurações incluem:

- Tema
- Atalhos de teclado
- Extensões ativas
- Configurações do editor
- Configurações do terminal
- Configurações de debug

## Desenvolvimento de Extensões

Para criar uma extensão:

1. Use o template de extensão em `extensions/template`
2. Implemente a interface `Extension`
3. Adicione um arquivo `manifest.json`
4. Teste localmente
5. Publique no marketplace

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

- 📧 Email: suporte@devassistant.io
- 💬 Discord: https://discord.gg/devassistant
- 📖 Documentação: https://docs.devassistant.io
- 🐛 Issues: https://github.com/seu-usuario/devassistant-ide/issues

# Assistente IA Local

Um assistente de IA local com interface moderna, processamento de voz e animações suaves.

## Características

- 🤖 IA local usando Ollama com modelo Phi (leve e eficiente)
- 🎙️ Reconhecimento de voz usando Whisper
- 🔊 Síntese de voz usando Coqui TTS
- ✨ Interface moderna com animações de partículas
- 💾 Sistema de cache para melhor performance
- 🎨 Temas personalizáveis
- 🔌 Sistema de plugins

## Requisitos do Sistema

- Windows 10 ou superior
- 16GB de RAM (mínimo)
- Processador Intel/AMD x64
- 2GB de espaço em disco

## Instalação

1. Instale o Node.js (versão 16 ou superior)
2. Instale o Ollama seguindo as instruções em [ollama.ai](https://ollama.ai)
3. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/assistente-ia-local.git
   cd assistente-ia-local
   ```
4. Instale as dependências:
   ```bash
   npm install
   ```
5. Inicie o aplicativo:
   ```bash
   npm start
   ```

## Configuração

1. Na primeira execução, o sistema baixará automaticamente o modelo Phi
2. Acesse as configurações para personalizar:
   - Nome do assistente
   - Voz
   - Tema
   - Atalhos de teclado

## Uso

- Digite suas mensagens na caixa de texto
- Use o botão de microfone para entrada por voz
- Navegue entre as diferentes seções usando o menu lateral
- Personalize o assistente nas configurações

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça suas alterações e commit:
   ```bash
   git commit -m 'Adiciona nova feature'
   ```
4. Push para a branch:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request

## Estrutura do Projeto

```
assistente-ia-local/
├── src/
│   ├── ai/          # Core da IA
│   ├── voice/       # Sistema de voz
│   ├── ui/          # Interface do usuário
│   ├── core/        # Funcionalidades principais
│   ├── utils/       # Utilitários
│   └── config/      # Configurações
├── cache/           # Cache do sistema
└── plugins/         # Plugins instalados
```

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Se encontrar algum problema ou tiver sugestões, por favor abra uma issue no GitHub. 