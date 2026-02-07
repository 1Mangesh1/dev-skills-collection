#!/usr/bin/env bash
# Regex Pattern Tester
# Test and validate regular expressions

test_regex_pattern() {
    local text="$1"
    local pattern="$2"
    
    echo "=== Testing Regex Pattern ==="
    echo "Text: $text"
    echo "Pattern: $pattern"
    echo ""
    
    if [[ $text =~ $pattern ]]; then
        echo "✓ Match found"
        echo "  Full match: ${BASH_REMATCH[0]}"
        if [ ${#BASH_REMATCH[@]} -gt 1 ]; then
            echo "  Groups:"
            for i in "${!BASH_REMATCH[@]}"; do
                if [ $i -gt 0 ]; then
                    echo "    Group $i: ${BASH_REMATCH[$i]}"
                fi
            done
        fi
    else
        echo "✗ No match"
    fi
}

extract_with_regex() {
    local file="$1"
    local pattern="$2"
    
    echo "=== Extracting with Regex ==="
    grep -oE "$pattern" "$file" | head -20
}

# Usage
test_regex_pattern "user@example.com" "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
