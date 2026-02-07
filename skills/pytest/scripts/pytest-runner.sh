#!/usr/bin/env bash
# Pytest Test Runner
# Execute Python tests with pytest

run_tests() {
    local test_dir="${1:-.}"
    local markers="${2:-}"
    
    echo "=== Running Pytest ==="
    
    if [ -z "$markers" ]; then
        python -m pytest "$test_dir" -v
    else
        python -m pytest "$test_dir" -v -m "$markers"
    fi
}

run_with_coverage() {
    local test_dir="${1:-.}"
    
    echo "=== Running Tests with Coverage ==="
    python -m pytest "$test_dir" \
        --cov=src \
        --cov-report=html \
        --cov-report=term-missing
    
    echo "Coverage report: htmlcov/index.html"
}

run_specific_test() {
    local test_file="$1"
    local test_name="$2"
    
    if [ -z "$test_name" ]; then
        python -m pytest "$test_file" -v
    else
        python -m pytest "$test_file::$test_name" -v
    fi
}

# Usage
run_tests "tests/"
