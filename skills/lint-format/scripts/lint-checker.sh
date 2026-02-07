#!/usr/bin/env bash
# Lint & Format Checker
# Check code style and formatting

check_lint() {
    local file_extension="$1"
    
    case "$file_extension" in
        js|jsx|ts|tsx)
            npx eslint . --max-warnings 0
            ;;
        py)
            python -m pylint src/
            python -m flake8 src/
            ;;
        go)
            go vet ./...
            gofmt -l .
            ;;
        *)
            echo "Unsupported file type: $file_extension"
            ;;
    esac
}

format_code() {
    echo "=== Formatting Code ==="
    npx prettier --write .
}

install_pre_commit() {
    echo "=== Installing Pre-commit Hook ==="
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
npx lint-staged
EOF
    
    chmod +x .git/hooks/pre-commit
}

# Usage
check_lint "js"
format_code
