#!/usr/bin/env bash
# MCP Configuration Validator
# Check MCP server configuration

validate_mcp_config() {
    local config_file="${1:-mcp.config.json}"
    
    echo "=== Validating MCP Configuration ==="
    
    if [ ! -f "$config_file" ]; then
        echo "❌ Config file not found: $config_file"
        return 1
    fi
    
    # Check for required fields
    if ! jq '.server.name' "$config_file" > /dev/null 2>&1; then
        echo "❌ Missing required field: server.name"
        return 1
    fi
    
    if ! jq '.tools' "$config_file" > /dev/null 2>&1; then
        echo "❌ Missing required field: tools"
        return 1
    fi
    
    echo "✓ Configuration is valid"
    echo ""
    echo "Server: $(jq -r '.server.name' "$config_file")"
    echo "Tools: $(jq '.tools | length' "$config_file")"
}

# Usage
validate_mcp_config "mcp.config.json"
