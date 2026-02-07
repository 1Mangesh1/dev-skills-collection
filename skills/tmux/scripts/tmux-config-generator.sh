#!/usr/bin/env bash
# Tmux Configuration Helper
# Generate and manage tmux config

generate_tmux_config() {
    local config_file="$HOME/.tmux.conf"
    
    cat > "$config_file" << 'EOF'
# Tmux Configuration

# Set prefix to Ctrl-a
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Pane navigation
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Splitting
bind | split-window -h
bind - split-window -v

# 256 color support
set -g default-terminal "screen-256color"

# Status bar
set -g status-bg colour234
set -g status-fg colour137

# Status options
set -g status-left '#[fg=colour233,bg=colour245] #S #[default]'
set -g status-right '#(date +"%H:%M") #h'

# Mouse support
set -g mouse on

# Aggressive resize
setw -g aggressive-resize on
EOF
    
    echo "✓ Config created: $config_file"
}

# Usage
generate_tmux_config
