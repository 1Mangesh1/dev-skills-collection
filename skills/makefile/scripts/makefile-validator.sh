#!/usr/bin/env bash
# Makefile Validator
# Test and validate Makefile syntax

validate_makefile() {
    echo "=== Validating Makefile ==="
    
    if make -n 2>&1 | head -5 | grep -q "Makefile"; then
        echo "✓ Makefile is syntactically valid"
    else
        echo "⚠ Makefile may have issues"
        make -n 2>&1 | head -20
    fi
}

list_targets() {
    echo "=== Available Targets ==="
    grep "^[^.#].*:.*##" Makefile | sed 's/:.*##//' | column -t
}

# Usage
validate_makefile
list_targets
