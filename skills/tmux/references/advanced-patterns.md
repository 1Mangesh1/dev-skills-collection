# Advanced Tmux Patterns

## Session Templating

```bash
function dev_session {
    local project="$1"
    
    tmux new-session -d -s "$project"
    
    # Window 1: Editor
    tmux send-keys -t "$project" "vim" Enter
    
    # Window 2: Shell
    tmux new-window -t "$project" -n shell
    tmux send-keys -t "$project:shell" "cd ~/projects/$project" Enter
    
    # Window 3: Test
    tmux new-window -t "$project" -n test
    
    tmux attach -t "$project"
}

dev_session "myapp"
```

## Pane Scripting

```bash
# Create 4-pane layout
tmux new-session -d -s work

# Split to 2x2 grid
tmux split-window -h                    # Split right
tmux split-window -v                    # Split bottom of left
tmux select-pane -t 0
tmux split-window -v                    # Split bottom of left
tmux select-pane -t 0

# Send commands to panes
tmux send-keys -t work:0 "nvim" Enter
tmux send-keys -t work:1 "npm run watch" Enter
tmux send-keys -t work:2 "npm run test -- --watch" Enter
tmux send-keys -t work:3 "docker logs -f app" Enter

tmux attach -t work
```

## Monitor Specific Commands

```bash
# Watch server status in background
tmux new-window -t logs -n status
tmux send-keys -t logs "watch -n 1 'ps aux | grep app'" Enter

# Watch test results
tmux new-window -t logs -n tests
tmux send-keys -t logs "npm run test -- --watch" Enter
```

## Conditional Configuration

```bash
# ~/.tmux.conf

# Check if running on macOS
if-shell "uname | grep -q Darwin" {
    bind -n End send-key -X end-of-line
    bind -n Home send-key -X start-of-line
}

# Different colors for different hosts
if-shell "hostname | grep -q production" {
    set -g status-bg red
} {
    set -g status-bg green
}
```

## Synchronize Panes

```
# Send same command to all panes
Ctrl-a : set-window-option synchronize-panes on
Ctrl-a : set-window-option synchronize-panes off
```

## Status Line

```
#{session_name}     Current session
#{window_name}      Current window
#{window_index}     Window number
#{pane_index}       Pane number
#{pane_current_path} Current directory
#(command)          Run shell command
```

Example with uptime:
```
set -g status-right "#(uptime | cut -d, -f3-)"
```
