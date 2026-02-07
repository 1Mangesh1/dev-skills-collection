#!/usr/bin/env bash
# System Diagnostics One-liners
# Analyze system performance and issues

# CPU usage
show_cpu_usage() {
    ps aux | sort -rk 3,3 | head -10
}

# Memory usage
show_memory_usage() {
    ps aux | sort -rk 4,4 | head -10
}

# Network connections
show_connections() {
    netstat -tuln | grep LISTEN
}

# Disk usage
show_disk_usage() {
    du -sh */ | sort -rh | head -10
}

# Process monitoring
watch_process() {
    watch -n 1 "ps aux | grep $1 | grep -v grep"
}

# Usage
show_cpu_usage
show_memory_usage
