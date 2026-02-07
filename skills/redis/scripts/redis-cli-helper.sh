#!/usr/bin/env bash
# Redis Cache Manager
# Manage Redis connections and operations

connect_redis() {
    local host="${1:-localhost}"
    local port="${2:-6379}"
    
    echo "=== Connecting to Redis ==="
    redis-cli -h "$host" -p "$port" ping
}

test_redis_operations() {
    echo "=== Redis Operations ==="
    
    # Set and get
    redis-cli SET mykey "Hello"
    redis-cli GET mykey
    
    # Increment
    redis-cli INCR counter
    
    # List operations
    redis-cli LPUSH mylist "a"
    redis-cli LPUSH mylist "b"
    redis-cli LRANGE mylist 0 -1
    
    # Hash operations
    redis-cli HSET myhash field1 "value1"
    redis-cli HGET myhash field1
}

monitor_redis() {
    local host="${1:-localhost}"
    local port="${2:-6379}"
    
    echo "=== Monitoring Redis ==="
    redis-cli -h "$host" -p "$port" INFO
}

clear_cache() {
    echo "=== Clearing Redis Cache ==="
    read -p "Clear all keys? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        redis-cli FLUSHALL
    fi
}

# Usage
connect_redis
test_redis_operations
