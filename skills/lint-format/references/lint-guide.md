# Code Linting & Formatting

## ESLint (JavaScript)

```bash
# Install
npm install --save-dev eslint

# Initialize
npx eslint --init

# Lint files
npx eslint src/

# Fix issues
npx eslint src/ --fix
```

Configuration:
```json
{
  "extends": ["eslint:recommended"],
  "rules": {
    "no-console": "warn",
    "semi": ["error", "always"]
  }
}
```

## Prettier (Code Formatter)

```bash
npm install --save-dev prettier

# Format all files
npx prettier --write .

# Check formatting
npx prettier --check .
```

Config:
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

## Python Tools

```bash
# Flake8 (Linting)
flake8 src/

# Black (Formatter)
black src/

# isort (Sort imports)
isort src/

# Pylint (Comprehensive)
pylint src/
```

## Go Tools

```bash
# gofmt (Formatter)
gofmt -w .

# go vet (Lint)
go vet ./...

# golangci-lint (Multiple linters)
golangci-lint run
```

## Pre-commit Framework

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3
```

Install and run:
```bash
pre-commit install
pre-commit run --all-files
```
