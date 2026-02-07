#!/usr/bin/env bash
# Git-Hooks Pre-Push Validator
# Comprehensive checks before pushing

pre_push_check() {
    echo "=== Pre-Push Checks ==="
    
    # No commits on main
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
        echo "❌ Cannot push directly to $current_branch"
        echo "   Create a feature branch instead"
        return 1
    fi
    
    # Check for console.log, debugger, etc
    echo "Checking for debug statements..."
    if git diff --cached | grep -E "console\.(log|debug)|debugger"; then
        echo "❌ Found debug statements. Remove before pushing."
        return 1
    fi
    
    # Run tests
    echo "Running tests..."
    npm test -- --passWithNoTests
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed"
        return 1
    fi
    
    echo "✓ All pre-push checks passed"
}

pre_push_check
