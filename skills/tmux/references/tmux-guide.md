# Tmux Guide

## Installation

```bash
# macOS
brew install tmux

# Ubuntu
sudo apt install tmux

# Check version
tmux -V
```

## Basic Commands

```bash
# Create new session
tmux new-session -s myapp

# List sessions
tmux list-sessions

# Attach to session
tmux attach-session -s myapp

# Kill session
tmux kill-session -t myapp

# Kill all sessions
tmux kill-server
```

## Inside Tmux (Prefix: Ctrl-a)

### Sessions
```
Ctrl-a :new-session -s name     Create new session
Ctrl-a s                        List sessions
Ctrl-a d                        Detach from session
Ctrl-a (                        Previous session
Ctrl-a )                        Next session
```

### Windows
```
Ctrl-a c                        Create new window
Ctrl-a w                        List windows
Ctrl-a n                        Next window
Ctrl-a p                        Previous window
Ctrl-a &                        Kill window
Ctrl-a ,                        Rename window
```

### Panes
```
Ctrl-a %                        Split vertical
Ctrl-a "                        Split horizontal
Ctrl-a h/j/k/l                  Navigate panes
Ctrl-a x                        Kill pane
Ctrl-a o                        Next pane
Ctrl-a !                        Break pane to window
```

### Copy Mode
```
Ctrl-a [                        Enter copy mode
Space                          Start selection
Enter                          Copy selection
Ctrl-a ]                        Paste
```

## Configuration (~/.tmux.conf)

```bash
# Set prefix key
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Pane navigation with vim keys
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Windows and panes
bind | split-window -h          # Vertical split
bind - split-window -v          # Horizontal split

# Colors
set -g default-terminal "screen-256color"

# Status bar
set -g status-left "#S"
set -g status-right "%H:%M"

# Mouse support
set -g mouse on

# Auto renumber windows
set -g renumber-windows on
```

## Common Workflows

### Development Session
```bash
tmux new-session -s dev -n editor
tmux send-keys -t dev "vim" Enter
tmux new-window -t dev -n shell
tmux new-window -t dev -n build
tmux split-window -h -t dev:build
tmux attach -t dev
```

### Multiple Logs
```bash
tmux new-session -s logs
tmux send-keys -t logs "tail -f app.log" Enter
tmux new-window -t logs
tmux send-keys -t logs "tail -f error.log" Enter
```

## Tips

1. **Copy between panes** - Ctrl-a [ to mark, Ctrl-a ] to paste
2. **Reload config** - Ctrl-a : then `source-file ~/.tmux.conf`
3. **Show pane numbers** - Ctrl-a q
4. **Zoom pane** - Ctrl-a z
5. **List all keybindings** - Ctrl-a ? or `tmux list-keys`
