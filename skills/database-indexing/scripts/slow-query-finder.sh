#!/usr/bin/env bash
# Slow Query Finder
# Identifies and logs slow queries

find_slow_queries() {
    local log_file="$1"
    
    echo "=== Slow Queries (>1000ms) ==="
    grep "duration: [1-9][0-9][0-9][0-9]" "$log_file" | head -20
    
    echo ""
    echo "=== Top 10 Slowest Queries ==="
    grep "duration:" "$log_file" | \
        sed 's/.*duration: \([0-9]*\).*/\1/' | \
        sort -rn | head -10
}

# Usage example
find_slow_queries "/var/log/postgresql/slow-queries.log"
