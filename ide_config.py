import os
from pathlib import Path

# Configurações básicas
IDE_CONFIG = {
    "name": "DevAssistant IDE",
    "version": "1.0.0",
    "theme": "dark",
    "language": "pt-BR",
    "workspace_dir": str(Path.home() / "workspace"),
    "temp_dir": str(Path.home() / ".devassistant" / "temp"),
    "cache_dir": str(Path.home() / ".devassistant" / "cache"),
    "log_dir": str(Path.home() / ".devassistant" / "logs"),
    "extensions_dir": str(Path.home() / ".devassistant" / "extensions"),
    "marketplace_url": "https://marketplace.devassistant.io",
    "port": int(os.environ.get('IDE_PORT', 5001)),  # Porta padrão 5001
}

# Configurações do editor
EDITOR_CONFIG = {
    "font_family": "Fira Code",
    "font_size": 14,
    "tab_size": 4,
    "use_spaces": True,
    "word_wrap": True,
    "show_line_numbers": True,
    "show_minimap": True,
    "auto_save": True,
    "format_on_save": True,
    "auto_complete": True,
    "snippets": True,
    "bracket_matching": True,
    "multi_cursor": True,
    "code_folding": True,
    "line_highlight": True,
    "indent_guides": True,
    "parameter_hints": True,
    "code_lens": True,
}

# Configurações do terminal
TERMINAL_CONFIG = {
    "shell": "powershell" if os.name == "nt" else "bash",
    "font_family": "Consolas",
    "font_size": 12,
    "history_size": 10000,
    "scroll_back": 1000,
    "integrated_git": True,
    "command_suggestions": True,
    "auto_complete": True,
}

# Configurações do assistente IA
AI_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "context_window": 8000,
    "save_history": True,
    "auto_complete": True,
    "code_suggestions": True,
    "natural_language_commands": True,
    "code_explanation": True,
    "error_analysis": True,
    "refactoring_suggestions": True,
    "test_generation": True,
    "documentation_generation": True,
    "code_review": True,
    "security_analysis": True,
    "performance_tips": True,
}

# Extensões padrão
DEFAULT_EXTENSIONS = {
    "python": {
        "enabled": True,
        "features": ["linting", "debugging", "formatting", "testing"]
    },
    "javascript": {
        "enabled": True,
        "features": ["linting", "debugging", "formatting", "testing"]
    },
    "typescript": {
        "enabled": True,
        "features": ["linting", "debugging", "formatting", "testing"]
    },
    "html": {
        "enabled": True,
        "features": ["preview", "formatting", "emmet"]
    },
    "css": {
        "enabled": True,
        "features": ["preview", "formatting", "emmet"]
    },
    "markdown": {
        "enabled": True,
        "features": ["preview", "formatting", "spellcheck"]
    },
    "git": {
        "enabled": True,
        "features": ["source_control", "blame", "history"]
    },
    "docker": {
        "enabled": True,
        "features": ["compose", "build", "run"]
    },
    "database": {
        "enabled": True,
        "features": ["query", "schema", "visualization"]
    },
}

# Comandos em linguagem natural
NATURAL_COMMANDS = {
    "criar_projeto": {
        "descrição": "Cria um novo projeto com estrutura básica",
        "exemplos": [
            "criar novo projeto python",
            "iniciar projeto web",
            "começar projeto react"
        ]
    },
    "executar": {
        "descrição": "Executa o código atual",
        "exemplos": [
            "rodar o programa",
            "executar arquivo atual",
            "testar código"
        ]
    },
    "debugar": {
        "descrição": "Inicia o modo de debug",
        "exemplos": [
            "debugar código",
            "encontrar erro",
            "testar passo a passo"
        ]
    },
    "explicar": {
        "descrição": "Explica o código selecionado",
        "exemplos": [
            "o que faz esse código",
            "explicar função",
            "como isso funciona"
        ]
    },
    "refatorar": {
        "descrição": "Sugere melhorias no código",
        "exemplos": [
            "melhorar código",
            "otimizar função",
            "limpar código"
        ]
    },
}

# Atalhos personalizados
SHORTCUTS = {
    "new_file": "Ctrl+N",
    "open_file": "Ctrl+O",
    "save_file": "Ctrl+S",
    "save_all": "Ctrl+Shift+S",
    "find": "Ctrl+F",
    "replace": "Ctrl+H",
    "terminal": "Ctrl+`",
    "run_code": "F5",
    "debug": "F9",
    "toggle_sidebar": "Ctrl+B",
    "toggle_terminal": "Ctrl+J",
    "ai_assistant": "Ctrl+Space",
    "quick_fix": "Ctrl+.",
    "format_code": "Shift+Alt+F",
    "refactor": "Ctrl+Shift+R",
    "go_to_definition": "F12",
    "find_references": "Shift+F12",
    "rename_symbol": "F2",
    "toggle_comment": "Ctrl+/",
    "zoom_in": "Ctrl++",
    "zoom_out": "Ctrl+-",
}

# Configurações de extensões
EXTENSIONS = {
    "python": True,
    "javascript": True,
    "typescript": True,
    "html": True,
    "css": True,
    "markdown": True,
    "json": True,
    "yaml": True,
    "docker": True,
}

# Configurações de debug
DEBUG_CONFIG = {
    "show_variables": True,
    "show_call_stack": True,
    "break_on_error": True,
    "log_debug_info": True,
}

# Configurações de preview
PREVIEW_CONFIG = {
    "auto_refresh": True,
    "port_range": (3000, 3999),
    "default_browser": "chrome",
    "live_reload": True,
}

# Configurações de git
GIT_CONFIG = {
    "show_git_status": True,
    "auto_fetch": True,
    "fetch_interval": 300,
    "show_git_blame": True,
} 