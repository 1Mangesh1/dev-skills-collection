#!/usr/bin/env bash
# SSH Connection Troubleshooter
# Debug SSH connection issues

debug_ssh_connection() {
    local host="$1"
    
    echo "=== SSH Debug Info ==="
    echo "Testing connectivity to: $host"
    echo ""
    
    # Check DNS resolution
    echo "1. DNS Resolution:"
    nslookup "$host" 2>&1 | head -5
    echo ""
    
    # Check port connectivity
    echo "2. Port 22 Connectivity:"
    nc -zv "$host" 22 2>&1
    echo ""
    
    # Check SSH keys
    echo "3. Available SSH Keys:"
    ls -la ~/.ssh/*.pub
    echo ""
    
    # Test SSH connection with verbose
    echo "4. SSH Connection Attempt (verbose):"
    ssh -vvv "$host" 2>&1 | head -50
}

fix_ssh_permissions() {
    echo "=== Fixing SSH Permissions ==="
    
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/id_* ~/.ssh/config 2>/dev/null || true
    chmod 644 ~/.ssh/*.pub 2>/dev/null || true
    chmod 644 ~/.ssh/known_hosts 2>/dev/null || true
    
    echo "✓ SSH permissions fixed"
}

# Usage  
debug_ssh_connection "github.com"
fix_ssh_permissions
