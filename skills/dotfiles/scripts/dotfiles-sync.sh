#!/usr/bin/env bash
# Dotfiles Sync with Repository
# Sync system dotfiles with git repo

sync_dotfiles_to_repo() {
    local repo_dir="${1:-.dotfiles}"
    
    echo "=== Syncing Dotfiles to Repository ==="
    
    # List of dotfiles to track
    declare -a dotfiles=(
        ".bashrc"
        ".zshrc"
        ".vimrc"
        ".gitconfig"
        ".tmux.conf"
    )
    
    for dotfile in "${dotfiles[@]}"; do
        if [ -f "$HOME/$dotfile" ]; then
            cp "$HOME/$dotfile" "$repo_dir/$dotfile"
            echo "Synced $dotfile"
        fi
    done
    
    # Commit changes
    cd "$repo_dir"
    git add .
    git commit -m "feat: update dotfiles"
}

sync_dotfiles_to_repo "${1:-.dotfiles}"
