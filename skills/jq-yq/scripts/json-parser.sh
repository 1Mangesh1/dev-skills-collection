#!/usr/bin/env bash
# jq JSON Query Tool
# Parse and transform JSON

parse_json_file() {
    local file="$1"
    
    echo "=== Parsing JSON ==="
    
    # Pretty print
    jq '.' "$file"
    
    # Extract field
    jq '.name' "$file"
    
    # Filter array
    jq '.items[] | select(.price > 100)' "$file"
}

extract_fields() {
    local file="$1"
    
    echo "=== Transforming JSON ==="
    
    # Select specific fields
    jq '{name: .name, email: .email}' "$file"
    
    # Map array
    jq '.items[] | {id, name}' "$file"
}

merge_json_files() {
    local file1="$1"
    local file2="$2"
    
    # Merge objects
    jq -s '.[0] * .[1]' "$file1" "$file2"
}

# Usage
parse_json_file "data.json"
