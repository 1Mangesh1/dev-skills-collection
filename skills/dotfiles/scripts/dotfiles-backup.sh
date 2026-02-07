#!/usr/bin/env bash
# Dotfiles Manager
# Backup and restore configuration files

backup_dotfiles() {
    local backup_dir="$HOME/.dotfiles-backup"
    mkdir -p "$backup_dir"
    
    echo "=== Backing up Dotfiles ==="
    
    # Common dotfiles
    files=(
        ~/.bashrc
        ~/.zshrc
        ~/.vimrc
        ~/.gitconfig
        ~/.ssh/config
        ~/.tmux.conf
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/$(basename "$file")"
            echo "✓ Backed up $(basename "$file")"
        fi
    done
}

restore_dotfiles() {
    local backup_dir="$HOME/.dotfiles-backup"
    
    echo "=== Restoring Dotfiles ==="
    
    for file in "$backup_dir"/*; do
        if [ -f "$file" ]; then
            cp "$file" "$HOME/$(basename "$file")"
            echo "✓ Restored $(basename "$file")"
        fi
    done
}

# Usage
backup_dotfiles
