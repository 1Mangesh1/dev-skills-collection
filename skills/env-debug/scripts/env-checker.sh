#!/usr/bin/env bash
# Environment Variable Debugger
# Diagnose issues with environment configuration

debug_environment() {
    echo "=== Environment Debug Info ==="
    echo ""
    
    echo "Shell Information:"
    echo "  Shell: $SHELL"
    echo "  Shell PID: $$"
    echo ""
    
    echo "Path Information:"
    echo "  PATH:"
    echo "$PATH" | tr ':' '\n' | head -10
    echo ""
    
    echo "Node/NPM Information:"
    which node && node --version
    which npm && npm --version
    which npx && npx --version
    echo ""
    
    echo "Python Information:"
    which python && python --version
    which python3 && python3 --version
    echo ""
    
    echo "Git Information:"
    git --version
    echo "  Git config user: $(git config user.name)"
    echo ""
    
    echo "Common Environment Variables:"
    echo "  HOME: $HOME"
    echo "  USER: $USER"
    echo "  NODE_ENV: ${NODE_ENV:-not set}"
    echo "  DEBUG: ${DEBUG:-not set}"
}

debug_environment
