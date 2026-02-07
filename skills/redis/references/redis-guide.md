# Redis Guide

## Installation & Setup

```bash
# macOS
brew install redis

# Ubuntu
sudo apt install redis-server

# Docker
docker run -d -p 6379:6379 redis:latest
```

## Basic Commands

```bash
# Connect
redis-cli

# Set and get
SET key value
GET key

# Delete
DEL key

# Check existence
EXISTS key

# Expire after seconds
EXPIRE key 3600
TTL key

# Increment
INCR counter
INCRBY counter 5

# Decrement
DECR counter
```

## Data Structures

### Strings
```bash
SET username "john"
APPEND username " doe"
STRLEN username
```

### Lists
```bash
LPUSH mylist "a"        # Add to left
RPUSH mylist "z"        # Add to right
LRANGE mylist 0 -1      # Get all
LPOP mylist             # Pop from left
LLEN mylist             # Length
```

### Sets
```bash
SADD myset "apple"
SADD myset "banana"
SMEMBERS myset          # Get all
SCARD myset             # Count
SINTER set1 set2        # Intersection
```

### Hashes
```bash
HSET user:1 name "John" age 30
HGET user:1 name
HGETALL user:1          # Get all fields
HINCRBY user:1 age 1    # Increment field
```

### Sorted Sets
```bash
ZADD scores 100 "Alice"
ZADD scores 85 "Bob"
ZRANGE scores 0 -1      # Get by rank
ZRANK scores "Alice"    # Get rank
ZREVRANGE scores 0 1    # Highest scores
```

## Expiry & TTL

```bash
# Set with expiry
SETEX key 3600 value    # Expire after 1 hour

# Get remaining time
TTL key                 # Seconds
PTTL key                # Milliseconds

# Remove expiry
PERSIST key

# Check if key exists
EXISTS key
```

## Keys & Scanning

```bash
# Find keys
KEYS *pattern*

# Safe scanning (for large datasets)
SCAN 0 MATCH "user:*" COUNT 10

# Get all keys (dangerous on large DB)
KEYS *

# Delete multiple keys
DEL key1 key2 key3
```

## Performance Tips

1. **Use pipelines** - Batch commands
2. **Set TTLs** - Auto-cleanup old data
3. **Use appropriate data types** - Hash > String for objects
4. **Monitor memory** - Use INFO MEMORY
5. **Eviction policy** - Set `maxmemory-policy`
