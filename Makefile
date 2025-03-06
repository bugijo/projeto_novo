.PHONY: help setup install test lint format clean docker-build docker-run docker-test

# Cores para mensagens
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

## Mostra ajuda
help:
	@echo ''
	@echo 'Uso:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

## Configura o ambiente de desenvolvimento
setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	pre-commit install

## Instala as dependências
install:
	pip install -r requirements.txt

## Executa os testes
test:
	pytest tests/ -v --cov=. --cov-report=term-missing

## Executa verificação de código
lint:
	flake8 .
	mypy .
	black . --check
	isort . --check-only

## Formata o código
format:
	black .
	isort .

## Remove arquivos temporários
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

## Constrói a imagem Docker
docker-build:
	docker-compose build

## Executa o projeto no Docker
docker-run:
	docker-compose up

## Executa os testes no Docker
docker-test:
	docker-compose run tests

## Inicia o servidor de desenvolvimento
dev:
	flask run --debug

## Inicia o servidor de produção
prod:
	gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 4 --timeout 120 app:app

## Atualiza as dependências
update-deps:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

## Cria uma nova migração do banco de dados
db-migrate:
	flask db migrate -m "$(message)"

## Aplica as migrações pendentes
db-upgrade:
	flask db upgrade

## Reverte a última migração
db-downgrade:
	flask db downgrade

## Verifica a segurança das dependências
security-check:
	safety check

## Gera relatório de cobertura de testes
coverage:
	pytest --cov=. --cov-report=html
	open htmlcov/index.html

## Executa verificação de tipos
type-check:
	mypy .

## Executa verificação de estilo
style-check:
	flake8 .
	black . --check
	isort . --check-only

## Executa todos os checks (lint, type-check, security-check)
check-all: lint type-check security-check

## Prepara uma nova versão
release:
	@echo "Atual: $$(git describe --tags --abbrev=0)"
	@read -p "Nova versão: " version; \
	git tag -a $$version -m "Versão $$version"
	@echo "Tag criada. Execute 'git push origin --tags' para publicar." 