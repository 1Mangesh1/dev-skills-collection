---
name: redis
description: Redis mastery for caching, data structures, pub/sub, streams, Lua scripting, clustering, and CLI operations. Use when user asks to "set up Redis", "cache data", "redis commands", "pub/sub", "redis data types", "session store", "rate limiting with Redis", "distributed lock", "redis streams", "redis cluster", "redis sentinel", "Lua scripting in Redis", "redis transactions", "redis persistence", "redis monitoring", or any Redis tasks.
---

# Redis

Caching, data structures, and real-time patterns.

## Key Naming Conventions

```
object-type:id:field        # Colon-separated hierarchy
user:1001:profile           # User profile
cache:api:/v2/products      # API response cache
session:abc123              # Session data
ratelimit:ip:10.0.0.1       # Rate limit counter
lock:order:7890             # Distributed lock
```

Keep keys short but readable. Colons are convention, not syntax. Avoid KEYS in production — use SCAN.

## CLI Basics

```bash
redis-cli
redis-cli -h hostname -p 6379 -a password
redis-cli --tls -h hostname -p 6380           # TLS connection
redis-cli -u redis://user:pass@host:6379/0    # URI format
redis-cli ping                                 # PONG
redis-cli info memory
redis-cli --stat                # Live stats (hits, misses, keys)
redis-cli --bigkeys             # Find largest keys per type
redis-cli --memkeys             # Sample memory usage per key
redis-cli --latency             # Continuous latency measurement
redis-cli --scan --pattern "user:*" | head -20   # Safe key listing
redis-cli DBSIZE                # Total key count
```

## Strings

```bash
SET key "value"
GET key
SET session:abc "user123" EX 3600      # 1 hour TTL
SET key "val" PX 5000                  # 5s in ms
SET key "val" EXAT 1700000000          # Unix timestamp expiry
SET lock:res "owner" NX EX 30         # Set if not exists (lock acquire)
SET key "val" XX                       # Update only if exists
INCR counter
INCRBY counter 5
DECR counter
INCRBYFLOAT price 2.50
MSET key1 "val1" key2 "val2"
MGET key1 key2
APPEND key " suffix"
STRLEN key
GETRANGE key 0 4                       # Substring
```

## Hashes

```bash
HSET user:1 name "Alice" email "alice@test.com" age 30
HGET user:1 name
HGETALL user:1
HMGET user:1 name email
HINCRBY user:1 age 1
HINCRBYFLOAT user:1 balance 9.99
HEXISTS user:1 email
HDEL user:1 age
HLEN user:1
HKEYS user:1
HSCAN user:1 0 MATCH "n*" COUNT 10    # Safe field iteration
```

## Lists

```bash
LPUSH queue "task1"       # Left (head)
RPUSH queue "task2"       # Right (tail)
LPOP queue
RPOP queue
BLPOP queue 30            # Blocking pop (timeout 30s)
LRANGE queue 0 -1         # All elements
LLEN queue
LTRIM queue 0 99          # Keep first 100
LPOS queue "task1"        # Find position
LMOVE src dst LEFT RIGHT  # Atomic move between lists
```

## Sets and Sorted Sets

```bash
# Sets
SADD tags "python" "redis" "docker"
SREM tags "docker"
SISMEMBER tags "python"
SMEMBERS tags
SCARD tags
SUNION tags1 tags2
SINTER tags1 tags2
SDIFF tags1 tags2
SRANDMEMBER tags 2
SPOP tags                              # Remove random member
SSCAN tags 0 MATCH "p*" COUNT 100

# Sorted sets
ZADD leaderboard 100 "alice" 95 "bob" 87 "charlie"
ZRANGE leaderboard 0 -1 WITHSCORES
ZREVRANGE leaderboard 0 2 WITHSCORES   # Top 3
ZRANGEBYSCORE leaderboard 90 100
ZRANGEBYSCORE leaderboard -inf +inf LIMIT 0 10   # Paginate
ZRANK leaderboard "alice"
ZREVRANK leaderboard "alice"
ZINCRBY leaderboard 5 "bob"
ZCOUNT leaderboard 80 100
ZSCORE leaderboard "alice"
ZPOPMIN leaderboard                    # Pop lowest score
ZPOPMAX leaderboard                    # Pop highest score
ZUNIONSTORE dest 2 board1 board2 WEIGHTS 1 2
```

## Streams, HyperLogLog, and Bitmaps

```bash
# Streams — append-only log for event sourcing / message queues
XADD events * action "click" page "/home"      # Auto-generate ID
XLEN events
XRANGE events - + COUNT 10
XREAD COUNT 5 BLOCK 2000 STREAMS events $       # Blocking read

# Consumer groups (durable message queue)
XGROUP CREATE events mygroup $ MKSTREAM
XREADGROUP GROUP mygroup consumer1 COUNT 1 BLOCK 2000 STREAMS events >
XACK events mygroup <message-id>
XPENDING events mygroup                         # Check unacked messages
XCLAIM events mygroup consumer2 3600000 <id>    # Claim stuck message

# HyperLogLog — cardinality estimation (~0.81% error, 12KB per key)
PFADD unique_visitors "user1" "user2" "user3"
PFCOUNT unique_visitors
PFMERGE total daily:mon daily:tue

# Bitmaps — bit-level operations on strings
SETBIT logins:2024-01-15 1001 1                 # User 1001 logged in
GETBIT logins:2024-01-15 1001
BITCOUNT logins:2024-01-15                      # Total logins that day
BITOP AND active_both logins:day1 logins:day2   # Users active both days
```

## Key Management and TTL

```bash
SCAN 0 MATCH user:* COUNT 100   # Safe iteration (never KEYS in prod)
EXPIRE key 3600           # Set TTL (seconds)
PEXPIRE key 3600000       # Milliseconds
EXPIREAT key 1700000000   # Unix timestamp
TTL key                   # -1 = no expiry, -2 = missing
PERSIST key               # Remove expiration
DEL key                   # Synchronous delete
UNLINK key                # Async delete (non-blocking for large keys)
TYPE key
OBJECT ENCODING key       # Internal encoding (ziplist, hashtable, etc.)
MEMORY USAGE key          # Bytes consumed by key
EXISTS key key2           # Returns count of existing keys
RENAME key newkey
DUMP key                  # Serialize key
RESTORE newkey 0 <bytes>  # Restore serialized key
```

Always set TTLs on cache keys. Jitter TTLs (add random seconds) to prevent thundering herd on mass expiry. Use `EXPIREAT` for calendar-aligned expirations.

## Pub/Sub

```bash
SUBSCRIBE channel1 channel2
PSUBSCRIBE news.*
PUBLISH channel1 "Hello subscribers!"
PUBSUB CHANNELS             # List active channels
PUBSUB NUMSUB channel1      # Subscriber count
```

Limitations: fire-and-forget (no persistence, no replay). Subscribers miss messages during disconnection. No acknowledgment. For durable messaging, use Streams with consumer groups.

## Caching Patterns

```bash
# Cache-aside (lazy loading) — most common
GET cache:user:1
# Miss? Query DB, then: SET cache:user:1 '{"name":"Alice"}' EX 300

# Write-through — app writes cache + DB together on every write
SET cache:user:1 '{"name":"Alice"}' EX 300

# Write-behind — write cache immediately, async flush to DB
# Requires application-level queue to batch DB writes

# Cache stampede prevention — probabilistic early expiration
# Refresh when TTL < random threshold, or use background refresh with SET ... NX
```

## Session Storage

```bash
HSET session:sid123 userId 1 role "admin" cart '["item1"]' lastAccess 1700000000
EXPIRE session:sid123 86400              # 24h TTL
HGET session:sid123 role
HSET session:sid123 lastAccess 1700000001
EXPIRE session:sid123 86400              # Refresh TTL on activity (sliding expiry)
```

## Rate Limiting

```bash
# Fixed window (simple, but allows burst at window edges)
INCR ratelimit:user:1:1700000000
EXPIRE ratelimit:user:1:1700000000 60
# Reject if count > limit

# Sliding window log (accurate, higher memory)
ZADD ratelimit:user:1 <now_ms> <request_id>
ZREMRANGEBYSCORE ratelimit:user:1 0 <now_ms - window_ms>
ZCARD ratelimit:user:1
EXPIRE ratelimit:user:1 <window_seconds>
# Reject if count > limit

# Token bucket via Lua — see Lua scripting section
```

## Distributed Lock (Redlock)

```bash
# Acquire
SET lock:resource <unique-id> NX EX 30

# Release atomically (Lua — only owner can release)
EVAL "if redis.call('GET',KEYS[1]) == ARGV[1] then return redis.call('DEL',KEYS[1]) else return 0 end" 1 lock:resource <unique-id>

# Multi-node Redlock: acquire on N/2+1 independent Redis nodes
# Use client libraries (redlock-py, redlock-node) for production
```

## Transactions

```bash
# MULTI/EXEC — atomic batch execution
MULTI
SET user:1:balance 100
INCR stats:transactions
EXEC

# WATCH — optimistic locking (CAS)
WATCH user:1:balance
balance = GET user:1:balance
MULTI
SET user:1:balance <new-value>
EXEC                         # Returns nil if balance changed since WATCH

DISCARD                      # Abort queued transaction
```

Redis transactions are not rollback-capable. If a command fails inside EXEC, other commands still execute. Use Lua scripts for true atomic logic.

## Lua Scripting

```bash
# Atomic operations on the server
EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 mykey "myval"

# Conditional update (compare-and-swap)
EVAL "
local cur = redis.call('GET', KEYS[1])
if cur == ARGV[1] then
  redis.call('SET', KEYS[1], ARGV[2])
  return 1
end
return 0
" 1 mykey "old" "new"

# Cache scripts (avoid resending text each call)
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
# Returns SHA: "a42059b356c875f0717db19a51f6aaa9161571a2"
EVALSHA a42059b356c875f0717db19a51f6aaa9161571a2 1 mykey
SCRIPT EXISTS <sha>

# Token bucket rate limiter in Lua
EVAL "
local tokens = tonumber(redis.call('GET', KEYS[1]) or ARGV[1])
if tokens > 0 then
  redis.call('SET', KEYS[1], tokens - 1, 'EX', ARGV[2])
  return 1
end
return 0
" 1 bucket:user:1 "10" "60"
```

## Persistence

```bash
# RDB snapshots (point-in-time, compact, fast restart)
CONFIG SET save "900 1 300 10 60 10000"
BGSAVE

# AOF (append-only file — durable, replayable log)
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec            # Options: always, everysec, no
BGREWRITEAOF                               # Compact AOF file

# Hybrid (Redis 7+) — RDB base + AOF for recent changes
CONFIG SET aof-use-rdb-preamble yes
```

RDB: faster restarts, smaller files, possible data loss between snapshots. AOF: more durable, larger files. Hybrid: recommended for production.

## Redis Sentinel (High Availability)

```bash
redis-cli -p 26379 SENTINEL masters
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
redis-cli -p 26379 SENTINEL replicas mymaster

# sentinel.conf essentials:
# sentinel monitor mymaster 127.0.0.1 6379 2       # quorum = 2
# sentinel down-after-milliseconds mymaster 5000
# sentinel failover-timeout mymaster 60000
# sentinel auth-pass mymaster <password>
```

Sentinel monitors master and auto-promotes a replica on failure. Clients connect via Sentinel to discover the current master.

## Redis Cluster (Sharding)

```bash
# 16384 hash slots distributed across nodes
redis-cli --cluster create host1:6379 host2:6379 host3:6379 \
  --cluster-replicas 1                    # 3 masters + 3 replicas
redis-cli --cluster info host1:6379
redis-cli --cluster check host1:6379
redis-cli --cluster reshard host1:6379    # Move hash slots
redis-cli -c -h host1 -p 6379            # -c follows MOVED redirects

# Hash tags — force keys to same slot
SET {user:1}:profile '...'
SET {user:1}:settings '...'               # Same slot due to {user:1}
```

Multi-key commands (MGET, transactions) only work on keys in the same hash slot. Use hash tags `{...}` to colocate related keys.

## Memory Optimization

```bash
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru

# Eviction policies:
# noeviction      — errors on write when full
# allkeys-lru     — evict least recently used (general cache)
# allkeys-lfu     — evict least frequently used
# volatile-lru    — LRU among keys with TTL only
# volatile-ttl    — evict keys with shortest TTL
# allkeys-random  — random eviction

# Memory analysis
INFO memory                               # Used memory, fragmentation ratio
MEMORY DOCTOR                             # Automated memory advice
MEMORY USAGE key SAMPLES 5
redis-cli --bigkeys
```

Use hashes for small objects (ziplist encoding). Avoid large blobs — offload to object storage, cache references.

## Connection Pooling

```python
# Python (redis-py) — always use connection pools
import redis
pool = redis.ConnectionPool(host='localhost', port=6379, db=0,
                            max_connections=20, decode_responses=True)
r = redis.Redis(connection_pool=pool)
# Node.js (ioredis): pooling is built-in
```

Never create a new connection per request. Set `max_connections` based on concurrency. Use `timeout` and `retry_on_timeout`.

## Monitoring

```bash
INFO all                                  # Full server report
INFO stats                                # Hits, misses, ops/sec
INFO clients                              # Connected clients
INFO replication                          # Master/replica status
SLOWLOG GET 10                            # Last 10 slow commands
CONFIG SET slowlog-log-slower-than 10000  # Log commands > 10ms
MONITOR                                   # Stream all commands (debug only — perf hit)
CONFIG SET latency-monitor-threshold 100  # Track commands > 100ms
LATENCY LATEST
CLIENT LIST                               # All connected clients
CLIENT SETNAME "myapp-worker-1"
```

## Common Patterns

```bash
# Leaderboard
ZADD leaderboard 100 "player:1"
ZINCRBY leaderboard 5 "player:1"
ZREVRANGE leaderboard 0 9 WITHSCORES     # Top 10

# Geospatial
GEOADD locations -122.4194 37.7749 "san_francisco"
GEODIST locations "san_francisco" "new_york" km
GEOSEARCH locations FROMLONLAT -122.0 37.0 BYRADIUS 100 km ASC

# Recent activity feed (capped list)
LPUSH feed:user:1 '{"action":"post","id":42}'
LTRIM feed:user:1 0 99                   # Keep last 100

# Idempotency check
SET idempotent:req:abc123 1 NX EX 86400  # nil if already processed
```

## Reference

For caching patterns, pub/sub, and Lua scripts: `references/patterns.md`
