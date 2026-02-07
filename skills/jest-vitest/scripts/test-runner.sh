#!/usr/bin/env bash
# Jest & Vitest Runner
# Run tests with filtering and reporting

run_tests() {
    local pattern="${1:-./__tests__}"
    
    echo "=== Running Tests ==="
    
    if [ -f "package.json" ] && grep -q '"vitest"' package.json; then
        # Vitest
        npx vitest run "$pattern" --reporter=verbose
    else
        # Jest
        npx jest "$pattern" --verbose
    fi
}

run_coverage() {
    echo "=== Test Coverage Report ==="
    
    if [ -f "package.json" ] && grep -q '"vitest"' package.json; then
        npx vitest run --coverage
    else
        npx jest --coverage
    fi
}

watch_tests() {
    echo "=== Watch Mode ==="
    npx jest --watch
}

# Usage
run_tests
