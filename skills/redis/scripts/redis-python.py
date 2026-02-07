#!/usr/bin/env python3
"""Redis Python Client Helper"""

import redis
import json

def connect_redis(host='localhost', port=6379, db=0):
    """Connect to Redis"""
    try:
        r = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        r.ping()
        print(f"✓ Connected to Redis at {host}:{port}")
        return r
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def cache_data(r, key, value, expiry=3600):
    """Cache data with optional expiry"""
    r.setex(key, expiry, json.dumps(value))
    print(f"Cached: {key}")

def get_cached_data(r, key):
    """Retrieve cached data"""
    data = r.get(key)
    if data:
        return json.loads(data)
    return None

def clear_cache(r, pattern='*'):
    """Clear cache by pattern"""
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
        print(f"Deleted {len(keys)} keys")

if __name__ == "__main__":
    r = connect_redis()
    if r:
        cache_data(r, "user:123", {"name": "John", "role": "admin"})
        data = get_cached_data(r, "user:123")
        print(f"Retrieved: {data}")
