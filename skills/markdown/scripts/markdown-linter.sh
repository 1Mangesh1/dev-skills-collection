#!/usr/bin/env bash
# Markdown Linter & Formatter
# Check and improve markdown files

lint_markdown() {
    local file="$1"
    
    echo "=== Linting: $file ==="
    
    # Check for common issues
    if grep -q "^#  " "$file"; then
        echo "⚠ Found extra space after heading"
    fi
    
    if grep -q "\[.*\]$" "$file"; then
        echo "⚠ Found reference without URL"
    fi
    
    echo "✓ Markdown lint complete"
}

format_markdown() {
    echo "=== Formatting Markdown ==="
    
    # Install prettier if not already
    if ! command -v prettier &> /dev/null; then
        npm install --global prettier
    fi
    
    prettier --write "**/*.md"
    echo "✓ All markdown files formatted"
}

generate_toc() {
    local file="$1"
    
    echo "=== Generating Table of Contents ==="
    
    # Extract headings
    grep "^##" "$file" | sed 's/^## /- [/' | sed 's/$/#/'
}

# Usage
lint_markdown "README.md"
format_markdown
