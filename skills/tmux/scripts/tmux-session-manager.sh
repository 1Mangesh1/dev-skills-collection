#!/usr/bin/env bash
# Tmux Session Manager
# Create and manage tmux sessions

create_session() {
    local session_name="$1"
    
    echo "=== Creating Tmux Session ==="
    tmux new-session -d -s "$session_name"
    echo "✓ Session created: $session_name"
}

list_sessions() {
    echo "=== Tmux Sessions ==="
    tmux list-sessions
}

create_dev_layout() {
    local session_name="${1:-dev}"
    
    echo "=== Creating Dev Layout ==="
    
    tmux new-session -d -s "$session_name" -x 200 -y 50
    
    # Window 0: Editor
    tmux send-keys -t "$session_name" "vim" Enter
    
    # Window 1: Terminal
    tmux new-window -t "$session_name" -n "shell"
    
    # Window 2: Build/Test
    tmux new-window -t "$session_name" -n "build"
    
    # Split window
    tmux split-window -h -t "$session_name:build"
    
    echo "✓ Layout created with 3 windows"
}

attach_session() {
    local session_name="$1"
    
    tmux attach-session -t "$session_name"
}

# Usage
# create_session "myapp"
# create_dev_layout "dev"
