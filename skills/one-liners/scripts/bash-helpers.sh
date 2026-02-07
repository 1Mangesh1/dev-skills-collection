#!/usr/bin/env bash
# One-liners Cheat Sheet
# Useful bash one-liners for developers

# File operations
count_lines() {
    find . -name "*.js" | xargs wc -l | tail -1
}

remove_empty_lines() {
    grep -v '^$' "$1" > "$1.tmp" && mv "$1.tmp" "$1"
}

# Network tools
check_port() {
    lsof -i :$1 || echo "Port $1 is free"
}

open_ssh_tunnel() {
    ssh -L 5432:localhost:5432 user@remote.host
}

# Data manipulation
json_to_csv() {
    jq -r '.[] | [.id, .name, .email] | @csv' input.json > output.csv
}

# Docker operations
stop_all_containers() {
    docker stop $(docker ps -q)
}

remove_unused_images() {
    docker image prune -a -f
}

# Git operations
cleanup_branches() {
    git branch -d $(git branch --merged)
}

# Usage examples
count_lines
check_port 3000
