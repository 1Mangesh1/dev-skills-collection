# Redis Advanced Patterns

## Caching Strategy

```
User Request
    ↓
Check Cache (Redis)
    ↓
    Hit? → Return cached data
    Miss? → Query database → Update cache → Return
```

Implementation:
```python
def get_user_data(user_id):
    cache_key = f"user:{user_id}"
    
    # Try cache
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss
    user = database.query_user(user_id)
    redis.setex(cache_key, 3600, json.dumps(user))
    return user
```

## Rate Limiting

```bash
# Counter per minute
INCR rate:user:123:minute
EXPIRE rate:user:123:minute 60

# Check
GET rate:user:123:minute
```

## Session Storage

```bash
# Store session
HSET session:abc123 userid 1 username john created 1234567890

# Update field
HSET session:abc123 last_activity 1234567891

# Set expiry
EXPIRE session:abc123 3600

# Delete
DEL session:abc123
```

## Pub/Sub Messaging

```bash
# Publisher
PUBLISH channel:notifications "New message"

# Subscriber
SUBSCRIBE channel:notifications

# Subscriber receives: 
# 1) "message"
# 2) "channel:notifications"
# 3) "New message"
```

## Connection Pooling (Python)

```python
from redis import ConnectionPool, Redis

pool = ConnectionPool.from_url('redis://localhost:6379')
r = Redis(connection_pool=pool)

# Connection automatically returned to pool
value = r.get('key')
```
