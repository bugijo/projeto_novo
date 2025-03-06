# Use uma imagem base Python oficial
FROM python:3.10-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Copia os arquivos de configuração
COPY pyproject.toml poetry.lock ./

# Instala dependências do projeto
RUN poetry install --no-interaction --no-ansi --no-root

# Copia o código fonte
COPY . .

# Expõe a porta
EXPOSE 5000

# Define o comando de inicialização
CMD ["poetry", "run", "python", "run.py", "--start"] 