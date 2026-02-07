#!/usr/bin/env bash
# SSH Configuration Manager
# Manage SSH keys and connections

generate_ssh_key() {
    local name="${1:-id_rsa}"
    local comment="${2:-user@hostname}"
    
    echo "=== Generating SSH Key ==="
    
    ssh-keygen -t ed25519 -f ~/.ssh/"$name" -C "$comment" -N ""
    
    echo "✓ Generated: ~/.ssh/$name"
    echo "✓ Public key: ~/.ssh/${name}.pub"
}

list_ssh_keys() {
    echo "=== SSH Keys ==="
    ls -la ~/.ssh/*.pub | awk '{print $9}'
}

add_to_ssh_config() {
    local host="$1"
    local hostname="$2"
    local user="$3"
    local keyfile="${4:-~/.ssh/id_rsa}"
    
    cat >> ~/.ssh/config << EOF

Host $host
    HostName $hostname
    User $user
    IdentityFile $keyfile
    AddKeysToAgent yes
    UseKeychain yes
EOF
    
    echo "✓ Added to ~/.ssh/config"
}

test_ssh_connection() {
    local host="$1"
    
    echo "=== Testing SSH Connection ==="
    ssh -T "git@$host" 2>&1 || ssh -v "$host" 2>&1 | head -30
}

# Usage
list_ssh_keys
