#!/usr/bin/env bash
# YAML Query Tool (yq)
# Parse and transform YAML files

parse_yaml() {
    local file="$1"
    
    echo "=== Parsing YAML ==="
    
    # Pretty print
    yq '.' "$file"
    
    # Extract field
    yq '.metadata.name' "$file"
    
    # Filter array
    yq '.spec.containers[] | select(.name == "app")' "$file"
}

validate_yaml() {
    local file="$1"
    
    echo "=== Validating YAML ==="
    
    if yq 'keys' "$file" > /dev/null 2>&1; then
        echo "✓ Valid YAML"
    else
        echo "❌ Invalid YAML"
    fi
}

convert_yaml_to_json() {
    local yaml_file="$1"
    local json_file="${2:-output.json}"
    
    yq '.' "$yaml_file" --output-format json > "$json_file"
    echo "Converted to $json_file"
}

# Usage
parse_yaml "config.yaml"
