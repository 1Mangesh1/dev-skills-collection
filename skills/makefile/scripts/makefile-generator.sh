#!/usr/bin/env bash
# Makefile Generator
# Create simple Makefiles for common tasks

create_makefile() {
    cat > Makefile << 'EOF'
.PHONY: help install build test lint format clean deploy

help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	npm install

build: ## Build application
	npm run build

test: ## Run tests
	npm test

lint: ## Run linter
	npm run lint

format: ## Format code
	npm run format

clean: ## Clean build artifacts
	rm -rf dist/ coverage/ node_modules/

deploy: build ## Deploy application
	npm run deploy

.DEFAULT_GOAL := help
EOF
    
    echo "✓ Makefile created"
}

# Create Python Makefile
create_python_makefile() {
    cat > Makefile << 'EOF'
.PHONY: install test lint format clean

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	flake8 src/
	pylint src/

format:
	black src/
	isort src/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	rm -rf .pytest_cache/
EOF
}

# Usage
create_makefile
