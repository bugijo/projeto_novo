# Exemplo de Fluxo Completo - Assistente de Programação Autônomo

Este documento demonstra um fluxo completo de uso do sistema, desde o prompt inicial até o deploy.

## 1. Configuração Inicial

1. Instale o LM Studio e baixe o modelo DeepSeek-Coder
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o assistente:
   ```bash
   python -m ai_engine.cli
   ```

## 2. Exemplo de Criação de Projeto

### 2.1 Prompt Inicial
```
🤖> novo todoapp "Criar um aplicativo de lista de tarefas com interface web usando Flask, SQLite para persistência, e interface moderna com Tailwind CSS. Precisa ter autenticação de usuários e categorização de tarefas."
```

### 2.2 Análise de Requisitos
O sistema irá analisar o prompt e gerar uma especificação técnica:

```
Especificação do Projeto
+--------------+------------------------------------------+
| Campo        | Valor                                    |
+--------------+------------------------------------------+
| name         | todoapp                                  |
| description  | Aplicativo de lista de tarefas web       |
| platform     | web                                      |
| language     | python                                   |
| dependencies | ["flask", "sqlite3", "tailwindcss", ...] |
| features     | ["auth", "tasks", "categories", ...]     |
| architecture | {                                        |
|              |   "backend": "Flask + SQLite",           |
|              |   "frontend": "Tailwind CSS",            |
|              |   "modules": [                           |
|              |     "auth",                              |
|              |     "tasks",                             |
|              |     "categories"                         |
|              |   ]                                      |
|              | }                                        |
+--------------+------------------------------------------+
```

### 2.3 Geração de Código
O sistema irá criar a estrutura do projeto:

```
todoapp/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
├── static/
│   ├── css/
│   └── js/
├── tests/
│   └── test_app.py
├── .env
├── config.py
└── requirements.txt
```

### 2.4 Validação de Código
Para cada arquivo gerado, você pode usar o comando `validar`:

```
🤖> validar todoapp/app/models.py

Validação de models.py
+----------+----------------------------------------+
| Tipo     | Detalhes                               |
+----------+----------------------------------------+
| Score    | 9/10                                   |
| Sugestão | Adicionar índices para otimização      |
| Sugestão | Incluir tipos de retorno nas funções   |
+----------+----------------------------------------+
```

### 2.5 Geração de Testes
Use o comando `testes` para gerar testes automaticamente:

```
🤖> testes todoapp/app/models.py

Teste #1
Descrição: Testa criação de usuário
Tipo: unit
Código:
def test_user_creation():
    user = User(username="test", email="test@test.com")
    assert user.username == "test"
    assert user.email == "test@test.com"
...
```

### 2.6 Explicação de Código
Use o comando `explicar` para entender o código gerado:

```
🤖> explicar todoapp/app/models.py

# Explicação do Código

## Visão Geral
Este módulo define os modelos de dados usando SQLAlchemy...

## Componentes Principais
1. Classe User
   - Gerencia autenticação
   - Usa bcrypt para senhas
...
```

## 3. Iteração e Melhorias

Após a geração inicial, você pode solicitar melhorias específicas:

```
🤖> novo feature todoapp "Adicionar suporte para tags nas tarefas"
```

O sistema irá:
1. Analisar o código existente
2. Fazer as alterações necessárias
3. Atualizar testes
4. Validar as mudanças

## 4. Deploy

O sistema pode gerar configurações de deploy:
- Dockerfile
- docker-compose.yml
- Scripts de CI/CD
- Instruções de deploy

## 5. Manutenção

O sistema mantém um histórico de decisões e mudanças no `knowledge_base.json`:

```json
{
  "decisions": [
    {
      "type": "architecture",
      "description": "Uso de SQLite para simplicidade inicial",
      "timestamp": "2024-02-20T14:30:00"
    }
  ],
  "corrections": [
    {
      "file": "models.py",
      "change": "Adicionado índice em Task.category_id",
      "reason": "Otimização de queries"
    }
  ]
}
```

Este histórico ajuda o sistema a aprender e melhorar suas decisões futuras. 