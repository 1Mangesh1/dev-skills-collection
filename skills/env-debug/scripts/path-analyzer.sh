#!/usr/bin/env bash
# Dependency Path Analyzer
# Find where commands are coming from

analyze_path() {
    echo "=== PATH Analysis ==="
    
    # Split PATH and show each directory
    echo "PATH entries:"
    IFS=':' read -ra PATHS <<< "$PATH"
    for i in "${!PATHS[@]}"; do
        if [ -d "${PATHS[$i]}" ]; then
            count=$(ls -1 "${PATHS[$i]}" 2>/dev/null | wc -l)
            echo "  [$((i+1))] ${PATHS[$i]} ($count commands)"
        else
            echo "  [$((i+1))] ${PATHS[$i]} (not found)"
        fi
    done
    echo ""
}

find_command() {
    local cmd="$1"
    echo "=== Looking for: $cmd ==="
    
    # Use which
    which "$cmd"
    
    # Use type for more info
    type "$cmd"
    
    # Find in PATH manually
    echo ""
    echo "Checking each PATH entry:"
    IFS=':' read -ra PATHS <<< "$PATH"
    for path in "${PATHS[@]}"; do
        if [ -x "$path/$cmd" ]; then
            file "$path/$cmd"
        fi
    done
}

# Usage
analyze_path
find_command "node"
