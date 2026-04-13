---
name: caching-strategies
description: Caching strategies and implementation patterns. Use when user asks to "add caching", "cache API responses", "set up CDN caching", "configure HTTP caching", "implement memoization", "cache database queries", "set cache headers", "invalidate cache", "design cache layer", "reduce API latency", "cache warming", "cache busting", "distributed caching", "Redis caching", "edge caching", or mentions caching strategies, cache invalidation, TTL, cache-aside, write-through, write-behind, CDN, browser caching, or memoization.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - caching
    - performance
    - cdn
    - redis
    - memoization
    - http-cache
---

# Caching Strategies

A comprehensive guide to caching at every layer of the stack -- from browser and CDN to application, database, and distributed systems. Proper caching dramatically reduces latency, lowers infrastructure costs, and improves user experience.

## Caching Fundamentals

### Core Concepts

| Term | Definition |
|------|-----------|
| Cache Hit | Requested data found in cache; served without hitting the origin |
| Cache Miss | Data not in cache; must be fetched from the origin and optionally stored |
| TTL (Time-To-Live) | Duration a cached entry remains valid before expiration |
| Eviction | Removal of entries from cache when capacity is reached or policy triggers |
| Stale Data | Cached data that is outdated relative to the source of truth |
| Cache Warming | Pre-populating a cache before traffic arrives |
| Cache Stampede | Many concurrent requests for the same uncached key overwhelming the origin |

### Eviction Policies

| Policy | Behavior | Best For |
|--------|----------|----------|
| LRU (Least Recently Used) | Evicts the entry not accessed for the longest time | General-purpose workloads |
| LFU (Least Frequently Used) | Evicts the entry accessed the fewest times | Frequency-skewed access patterns |
| FIFO (First In, First Out) | Evicts the oldest entry regardless of access | Simple, predictable rotation |
| TTL-Based | Evicts entries after a fixed duration | Time-sensitive data |
| Random | Evicts a random entry | When simplicity matters more than precision |
| ARC (Adaptive Replacement Cache) | Dynamically balances recency and frequency | Workloads with mixed access patterns |

---

## HTTP Caching

HTTP caching is the first line of defense. Proper headers prevent unnecessary network requests entirely.

### Cache-Control Header

```http
# Cache publicly for 1 hour, allow stale content for 60s while revalidating
Cache-Control: public, max-age=3600, stale-while-revalidate=60

# Private cache (browser only), revalidate every time
Cache-Control: private, no-cache

# Never cache (sensitive data)
Cache-Control: no-store

# Immutable assets (hashed filenames)
Cache-Control: public, max-age=31536000, immutable
```

### Cache-Control Directives Reference

| Directive | Meaning |
|-----------|---------|
| `public` | Any cache (CDN, proxy, browser) may store the response |
| `private` | Only the browser may cache; proxies must not |
| `no-cache` | Cache may store but must revalidate with origin before serving |
| `no-store` | Do not cache under any circumstances |
| `max-age=N` | Response is fresh for N seconds |
| `s-maxage=N` | Overrides max-age for shared caches (CDN/proxy) |
| `stale-while-revalidate=N` | Serve stale content for N seconds while fetching fresh copy |
| `stale-if-error=N` | Serve stale content for N seconds if origin returns an error |
| `immutable` | Content will never change; skip revalidation entirely |
| `must-revalidate` | Once stale, must revalidate before use -- no stale serving |

### ETag and Conditional Requests

```javascript
// Express.js -- ETag validation
const express = require('express');
const crypto = require('crypto');
const app = express();

app.get('/api/products/:id', async (req, res) => {
  const product = await db.getProduct(req.params.id);
  const etag = crypto
    .createHash('md5')
    .update(JSON.stringify(product))
    .digest('hex');

  // Check If-None-Match from client
  if (req.headers['if-none-match'] === etag) {
    return res.status(304).end(); // Not Modified
  }

  res.set({
    'ETag': etag,
    'Cache-Control': 'private, no-cache', // always revalidate
    'Last-Modified': product.updatedAt.toUTCString(),
  });

  res.json(product);
});
```

### Last-Modified and If-Modified-Since

```python
# Flask -- Last-Modified conditional response
from flask import Flask, request, make_response
from datetime import datetime

app = Flask(__name__)

@app.route('/api/report')
def get_report():
    report = fetch_report()
    last_modified = report['updated_at']

    # Check If-Modified-Since from client
    ims = request.headers.get('If-Modified-Since')
    if ims:
        ims_dt = datetime.strptime(ims, '%a, %d %b %Y %H:%M:%S GMT')
        if last_modified <= ims_dt:
            return '', 304

    resp = make_response(report['data'])
    resp.headers['Last-Modified'] = last_modified.strftime(
        '%a, %d %b %Y %H:%M:%S GMT'
    )
    resp.headers['Cache-Control'] = 'public, max-age=300'
    return resp
```

### Vary Header

The `Vary` header tells caches that the response differs based on certain request headers.

```http
# Cache separate versions by encoding and language
Vary: Accept-Encoding, Accept-Language

# Cache separate versions for authenticated vs anonymous
Vary: Authorization, Accept
```

---

## Browser Caching Strategies

### Service Worker Cache (Stale-While-Revalidate)

```javascript
// service-worker.js -- stale-while-revalidate strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open('api-cache-v1').then(async (cache) => {
      const cachedResponse = await cache.match(event.request);

      // Fetch fresh copy in the background
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse.ok) {
          cache.put(event.request, networkResponse.clone());
        }
        return networkResponse;
      });

      // Return cached immediately, update in background
      return cachedResponse || fetchPromise;
    })
  );
});
```

### Service Worker Cache (Network-First with Fallback)

```javascript
// service-worker.js -- network-first with offline fallback
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone and cache successful responses
        const clone = response.clone();
        caches.open('dynamic-cache-v1').then((cache) => {
          cache.put(event.request, clone);
        });
        return response;
      })
      .catch(() => {
        // Network failed, serve from cache
        return caches.match(event.request);
      })
  );
});
```

### Cache Versioning for Static Assets

```javascript
// webpack.config.js -- content-hash for cache busting
module.exports = {
  output: {
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
  },
};
```

```nginx
# Nginx -- long-lived cache for hashed assets, short for HTML
location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location / {
    expires 5m;
    add_header Cache-Control "public, no-cache";
}
```

---

## CDN Caching

### Cloudflare Page Rules / Cache Rules

```text
# Cache everything on the /api/public/* path for 1 hour
URL pattern: example.com/api/public/*
Cache Level: Cache Everything
Edge Cache TTL: 3600
Browser Cache TTL: 300

# Bypass cache for authenticated routes
URL pattern: example.com/api/user/*
Cache Level: Bypass
```

### CloudFront Cache Policy (AWS CDK)

```typescript
// AWS CDK -- CloudFront distribution with caching
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucket = new s3.Bucket(this, 'AssetsBucket');

const cachePolicy = new cloudfront.CachePolicy(this, 'ApiCachePolicy', {
  cachePolicyName: 'api-cache-1h',
  defaultTtl: Duration.hours(1),
  minTtl: Duration.minutes(1),
  maxTtl: Duration.days(1),
  headerBehavior: cloudfront.CacheHeaderBehavior.allowList(
    'Accept',
    'Accept-Language'
  ),
  queryStringBehavior: cloudfront.CacheQueryStringBehavior.all(),
  cookieBehavior: cloudfront.CacheCookieBehavior.none(),
  enableAcceptEncodingGzip: true,
  enableAcceptEncodingBrotli: true,
});

new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: new origins.S3Origin(bucket),
    cachePolicy,
    viewerProtocolPolicy:
      cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
  },
});
```

### Fastly VCL Snippet

```vcl
# Fastly VCL -- custom cache logic
sub vcl_recv {
  # Strip cookies for static assets to improve cache hit ratio
  if (req.url ~ "\.(css|js|png|jpg|svg|woff2)$") {
    unset req.http.Cookie;
  }

  # Pass authenticated requests directly to origin
  if (req.http.Authorization) {
    return(pass);
  }
}

sub vcl_fetch {
  # Cache API responses for 5 minutes at the edge
  if (req.url ~ "^/api/public/") {
    set beresp.ttl = 300s;
    set beresp.http.Cache-Control = "public, max-age=300";
  }
}
```

---

## Application-Level Caching Patterns

### Cache-Aside (Lazy Loading)

The application checks the cache first. On a miss, it fetches from the origin, stores in cache, and returns.

```python
# Python -- cache-aside with Redis
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_user(user_id: str) -> dict:
    cache_key = f"user:{user_id}"

    # 1. Check cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss -- fetch from DB
    user = db.query("SELECT * FROM users WHERE id = %s", (user_id,))

    # 3. Store in cache with TTL
    r.setex(cache_key, 3600, json.dumps(user))

    return user
```

### Read-Through Cache

The cache itself is responsible for loading data on a miss. The application always reads from the cache.

```java
// Java -- read-through with Caffeine
import com.github.benmanes.caffeine.cache.Caffeine;
import com.github.benmanes.caffeine.cache.LoadingCache;
import java.util.concurrent.TimeUnit;

LoadingCache<String, Product> productCache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(30, TimeUnit.MINUTES)
    .refreshAfterWrite(10, TimeUnit.MINUTES)
    .build(key -> productRepository.findById(key)); // loader function

// Usage -- cache handles miss automatically
Product product = productCache.get("prod-123");
```

### Write-Through Cache

Data is written to both the cache and the origin simultaneously. Ensures cache is always consistent.

```typescript
// TypeScript -- write-through pattern
class WriteThroughCache<T> {
  constructor(
    private cache: Map<string, { value: T; expiresAt: number }>,
    private store: DataStore<T>,
    private ttlMs: number
  ) {}

  async set(key: string, value: T): Promise<void> {
    // Write to origin first
    await this.store.save(key, value);

    // Then update cache
    this.cache.set(key, {
      value,
      expiresAt: Date.now() + this.ttlMs,
    });
  }

  async get(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    if (entry && entry.expiresAt > Date.now()) {
      return entry.value;
    }

    // Cache miss or expired -- read from origin
    const value = await this.store.load(key);
    if (value !== null) {
      this.cache.set(key, {
        value,
        expiresAt: Date.now() + this.ttlMs,
      });
    }
    return value;
  }
}
```

### Write-Behind (Write-Back) Cache

Writes go to the cache immediately and are asynchronously flushed to the origin, improving write throughput.

```python
# Python -- write-behind with background flush
import threading
import time
from collections import deque

class WriteBehindCache:
    def __init__(self, store, flush_interval=5):
        self.cache = {}
        self.store = store
        self.write_queue = deque()
        self.lock = threading.Lock()

        # Background flush thread
        self.flusher = threading.Thread(target=self._flush_loop,
                                        args=(flush_interval,),
                                        daemon=True)
        self.flusher.start()

    def set(self, key, value):
        with self.lock:
            self.cache[key] = value
            self.write_queue.append((key, value))

    def get(self, key):
        return self.cache.get(key)

    def _flush_loop(self, interval):
        while True:
            time.sleep(interval)
            self._flush()

    def _flush(self):
        with self.lock:
            batch = list(self.write_queue)
            self.write_queue.clear()

        if batch:
            self.store.bulk_save(batch)
```

---

## In-Memory Caching

### Node.js -- LRU Cache

```javascript
// Node.js -- using lru-cache package
const { LRUCache } = require('lru-cache');

const cache = new LRUCache({
  max: 500,                  // max entries
  maxSize: 50 * 1024 * 1024, // 50 MB
  sizeCalculation: (value) => JSON.stringify(value).length,
  ttl: 1000 * 60 * 10,       // 10 minutes
  allowStale: false,
  updateAgeOnGet: true,
});

// Usage
cache.set('user:42', { name: 'Alice', role: 'admin' });
const user = cache.get('user:42'); // updates last-access time
```

### Python -- functools.lru_cache and cachetools

```python
# Built-in memoization
from functools import lru_cache

@lru_cache(maxsize=256)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# TTL-aware caching with cachetools
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=1024, ttl=300)  # 5-minute TTL

@cached(cache)
def get_exchange_rate(currency_pair: str) -> float:
    return api.fetch_rate(currency_pair)
```

### Java -- Guava Cache

```java
// Guava LoadingCache with stats
import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import java.util.concurrent.TimeUnit;

LoadingCache<String, Config> configCache = CacheBuilder.newBuilder()
    .maximumSize(200)
    .expireAfterWrite(15, TimeUnit.MINUTES)
    .refreshAfterWrite(5, TimeUnit.MINUTES)
    .recordStats()  // enable hit/miss tracking
    .build(new CacheLoader<>() {
        @Override
        public Config load(String key) {
            return configService.fetchConfig(key);
        }
    });

// Print stats
System.out.println(configCache.stats());
// CacheStats{hitCount=950, missCount=50, hitRate=0.95, ...}
```

### Go -- sync.Map and groupcache

```go
// Go -- simple in-memory cache with expiration
package cache

import (
    "sync"
    "time"
)

type entry struct {
    value     interface{}
    expiresAt time.Time
}

type Cache struct {
    mu    sync.RWMutex
    items map[string]entry
}

func New() *Cache {
    c := &Cache{items: make(map[string]entry)}
    go c.cleanup(time.Minute) // periodic eviction
    return c
}

func (c *Cache) Set(key string, value interface{}, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = entry{value: value, expiresAt: time.Now().Add(ttl)}
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    e, ok := c.items[key]
    if !ok || time.Now().After(e.expiresAt) {
        return nil, false
    }
    return e.value, true
}

func (c *Cache) cleanup(interval time.Duration) {
    for range time.Tick(interval) {
        c.mu.Lock()
        for k, e := range c.items {
            if time.Now().After(e.expiresAt) {
                delete(c.items, k)
            }
        }
        c.mu.Unlock()
    }
}
```

---

## Distributed Caching

### Redis Caching Patterns

```python
# Python -- Redis with structured cache keys and pipelines
import redis
import json
from datetime import timedelta

r = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)

# Pattern: namespace:entity:id:field
CACHE_PREFIX = "myapp"

def cache_key(*parts: str) -> str:
    return f"{CACHE_PREFIX}:{':'.join(parts)}"

def get_user_profile(user_id: str) -> dict:
    key = cache_key("user", user_id, "profile")
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    profile = db.fetch_user_profile(user_id)
    r.setex(key, timedelta(hours=1), json.dumps(profile))
    return profile

def invalidate_user(user_id: str):
    """Invalidate all cache entries for a user using pattern scan."""
    pattern = cache_key("user", user_id, "*")
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match=pattern, count=100)
        if keys:
            r.delete(*keys)
        if cursor == 0:
            break

# Pipeline for batch operations
def warm_cache(user_ids: list[str]):
    profiles = db.fetch_user_profiles(user_ids)
    pipe = r.pipeline()
    for uid, profile in zip(user_ids, profiles):
        key = cache_key("user", uid, "profile")
        pipe.setex(key, timedelta(hours=1), json.dumps(profile))
    pipe.execute()
```

### Redis vs Memcached

| Feature | Redis | Memcached |
|---------|-------|-----------|
| Data structures | Strings, lists, sets, hashes, sorted sets, streams | Strings only |
| Persistence | RDB snapshots + AOF | None |
| Replication | Built-in primary/replica | None (client-side sharding) |
| Pub/Sub | Yes | No |
| Lua scripting | Yes | No |
| Max value size | 512 MB | 1 MB (default) |
| Multi-threading | Single-threaded (I/O threads in 6.0+) | Multi-threaded |
| Memory efficiency | Higher overhead per key | Lower overhead per key |

---

## Database Query Caching

### Application-Level Query Cache

```typescript
// TypeScript -- query result caching with key generation
import crypto from 'crypto';
import Redis from 'ioredis';

const redis = new Redis();

function queryHash(sql: string, params: unknown[]): string {
  return crypto
    .createHash('sha256')
    .update(JSON.stringify({ sql, params }))
    .digest('hex');
}

async function cachedQuery<T>(
  sql: string,
  params: unknown[],
  ttlSeconds: number = 300
): Promise<T[]> {
  const key = `query:${queryHash(sql, params)}`;

  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }

  const results = await db.query<T>(sql, params);
  await redis.setex(key, ttlSeconds, JSON.stringify(results));
  return results;
}

// Usage
const products = await cachedQuery<Product>(
  'SELECT * FROM products WHERE category = $1 AND active = true',
  ['electronics'],
  600 // 10 min TTL
);
```

### ORM-Level Caching (SQLAlchemy with dogpile.cache)

```python
# Python -- SQLAlchemy query caching
from dogpile.cache import make_region

region = make_region().configure(
    'dogpile.cache.redis',
    arguments={
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'redis_expiration_time': 600,
    }
)

@region.cache_on_arguments()
def get_active_products(category: str) -> list[dict]:
    return (
        db.session.query(Product)
        .filter(Product.category == category, Product.active == True)
        .all()
    )

# Invalidate when data changes
def update_product(product_id: int, data: dict):
    product = db.session.query(Product).get(product_id)
    for k, v in data.items():
        setattr(product, k, v)
    db.session.commit()
    # Invalidate the cached query for this category
    get_active_products.invalidate(product.category)
```

---

## Memoization Patterns

### JavaScript/TypeScript Memoization

```typescript
// Generic memoize with TTL
function memoize<T extends (...args: any[]) => any>(
  fn: T,
  options: { ttlMs?: number; maxSize?: number } = {}
): T {
  const { ttlMs = 0, maxSize = 1000 } = options;
  const cache = new Map<string, { value: ReturnType<T>; timestamp: number }>();

  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);
    const entry = cache.get(key);

    if (entry) {
      if (!ttlMs || Date.now() - entry.timestamp < ttlMs) {
        return entry.value;
      }
      cache.delete(key);
    }

    const result = fn(...args);
    cache.set(key, { value: result, timestamp: Date.now() });

    // Evict oldest if over capacity
    if (cache.size > maxSize) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }

    return result;
  }) as T;
}

// Usage
const expensiveCalc = memoize(
  (x: number, y: number) => {
    // simulate heavy computation
    return x ** y;
  },
  { ttlMs: 60_000, maxSize: 500 }
);
```

### React useMemo and useCallback

```tsx
// React -- memoization hooks
import { useMemo, useCallback, memo } from 'react';

function Dashboard({ data, filters }: Props) {
  // Memoize expensive derived state
  const filteredData = useMemo(
    () => data.filter((item) => matchesFilters(item, filters)),
    [data, filters]
  );

  // Memoize callback to prevent child re-renders
  const handleSort = useCallback(
    (column: string) => {
      dispatch({ type: 'SORT', column });
    },
    [dispatch]
  );

  return <DataTable data={filteredData} onSort={handleSort} />;
}

// Memoize component to skip re-renders when props unchanged
const DataTable = memo(function DataTable({ data, onSort }: TableProps) {
  return (
    <table>
      {/* render rows */}
    </table>
  );
});
```

---

## Cache Invalidation Strategies

Cache invalidation is one of the hardest problems in computer science. Choose the right strategy for your consistency requirements.

### Time-Based (TTL)

Simplest approach. Data expires after a fixed duration.

```python
# Redis TTL-based invalidation
r.setex("product:123", 3600, json.dumps(product))  # 1 hour
r.psetex("session:abc", 30000, session_data)        # 30 seconds
```

### Event-Based Invalidation

Invalidate when the underlying data changes, using events or messages.

```typescript
// Event-driven invalidation with Redis Pub/Sub
import Redis from 'ioredis';

const pub = new Redis();
const sub = new Redis();
const cache = new Redis();

// Publisher -- after a write operation
async function updateProduct(id: string, data: Product): Promise<void> {
  await db.updateProduct(id, data);
  await cache.del(`product:${id}`);
  await pub.publish('cache:invalidate', JSON.stringify({
    type: 'product',
    id,
    action: 'update',
  }));
}

// Subscriber -- other instances listen for invalidation events
sub.subscribe('cache:invalidate');
sub.on('message', (channel, message) => {
  const event = JSON.parse(message);
  if (event.type === 'product') {
    localCache.delete(`product:${event.id}`);
  }
});
```

### Version-Based Invalidation

Embed a version or generation number in the cache key. Incrementing the version effectively invalidates all old entries.

```python
# Version-based cache keys
VERSION_KEY = "cache:version:products"

def get_products_cache_key(category: str) -> str:
    version = r.get(VERSION_KEY) or "1"
    return f"products:v{version}:{category}"

def get_products(category: str) -> list:
    key = get_products_cache_key(category)
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    products = db.fetch_products(category)
    r.setex(key, 3600, json.dumps(products))
    return products

def invalidate_all_products():
    """Bump version -- all old keys become orphaned and expire via TTL."""
    r.incr(VERSION_KEY)
```

---

## Cache Stampede Prevention

### Locking (Mutex)

Only one request fetches from the origin while others wait.

```python
# Redis lock to prevent stampede
import redis
import time

r = redis.Redis()

def get_with_lock(key: str, fetch_fn, ttl=3600, lock_ttl=10):
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    lock_key = f"lock:{key}"
    # Try to acquire lock
    if r.set(lock_key, "1", nx=True, ex=lock_ttl):
        try:
            value = fetch_fn()
            r.setex(key, ttl, json.dumps(value))
            return value
        finally:
            r.delete(lock_key)
    else:
        # Another process is fetching -- wait and retry
        for _ in range(lock_ttl * 10):
            time.sleep(0.1)
            cached = r.get(key)
            if cached:
                return json.loads(cached)
        # Fallback: fetch anyway
        return fetch_fn()
```

### Probabilistic Early Expiration (XFetch)

Proactively refresh the cache before it expires. Each request has an increasing probability of triggering a refresh as the TTL approaches.

```python
import math
import random
import time

def xfetch(key: str, fetch_fn, ttl: int = 3600, beta: float = 1.0):
    """
    XFetch algorithm for probabilistic early recomputation.
    beta > 1 favors earlier recomputation.
    """
    cached = r.get(key)
    if cached:
        data = json.loads(cached)
        expiry = float(r.pttl(key)) / 1000.0  # remaining TTL in seconds
        delta = data.get('_compute_time', 0.1)

        # Probabilistic early expiration
        if expiry > 0:
            threshold = delta * beta * math.log(random.random()) * -1
            if expiry > threshold:
                return data['value']

    # Recompute
    start = time.time()
    value = fetch_fn()
    compute_time = time.time() - start

    payload = json.dumps({'value': value, '_compute_time': compute_time})
    r.setex(key, ttl, payload)
    return value
```

---

## Multi-Layer Caching Architecture

A well-designed system caches at multiple levels, each with different characteristics.

```text
Request Flow:

  Client
    |
    v
  [Browser Cache]  -- L1: instant, per-user, limited size
    |  miss
    v
  [CDN / Edge]     -- L2: ~10ms, shared, geographically distributed
    |  miss
    v
  [API Gateway]    -- L3: rate limiting, response cache
    |  miss
    v
  [App Memory]     -- L4: ~1ms, per-instance, LRU
    |  miss
    v
  [Redis/Memcached] -- L5: ~2-5ms, shared, large capacity
    |  miss
    v
  [Database]       -- Origin: ~10-100ms
```

### Implementation Example

```typescript
// Multi-layer cache with fallthrough
class MultiLayerCache {
  private layers: CacheLayer[];

  constructor(layers: CacheLayer[]) {
    this.layers = layers; // ordered from fastest to slowest
  }

  async get<T>(key: string): Promise<T | null> {
    for (let i = 0; i < this.layers.length; i++) {
      const value = await this.layers[i].get<T>(key);
      if (value !== null) {
        // Backfill faster layers
        for (let j = 0; j < i; j++) {
          await this.layers[j].set(key, value);
        }
        return value;
      }
    }
    return null;
  }

  async set<T>(key: string, value: T): Promise<void> {
    await Promise.all(
      this.layers.map((layer) => layer.set(key, value))
    );
  }

  async invalidate(key: string): Promise<void> {
    await Promise.all(
      this.layers.map((layer) => layer.delete(key))
    );
  }
}

// Usage
const cache = new MultiLayerCache([
  new InMemoryLayer({ maxSize: 1000, ttlMs: 60_000 }),
  new RedisLayer({ ttlSeconds: 3600 }),
]);
```

---

## Cache Warming Strategies

Pre-populate caches before traffic hits to avoid cold-start miss storms.

```python
# Cache warming on deployment or schedule
import asyncio

async def warm_cache():
    """Warm frequently accessed data into cache."""
    # 1. Warm top products
    top_products = await db.query(
        "SELECT id FROM products ORDER BY views DESC LIMIT 1000"
    )
    for batch in chunked(top_products, 50):
        tasks = [warm_product(p['id']) for p in batch]
        await asyncio.gather(*tasks)

    # 2. Warm configuration data
    configs = await db.query("SELECT * FROM app_config")
    pipe = r.pipeline()
    for config in configs:
        pipe.setex(
            f"config:{config['key']}",
            7200,
            json.dumps(config['value'])
        )
    pipe.execute()

async def warm_product(product_id: str):
    product = await db.fetch_product(product_id)
    await r.setex(
        f"product:{product_id}",
        3600,
        json.dumps(product)
    )

# Run at startup or via cron
# asyncio.run(warm_cache())
```

---

## Monitoring Cache Performance

### Key Metrics

| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| Hit Ratio | hits / (hits + misses) | > 90% for most workloads |
| Miss Ratio | misses / (hits + misses) | < 10% |
| Eviction Rate | evictions / time | Should be low and stable |
| Latency (p50/p99) | Time per cache operation | p50 < 1ms, p99 < 5ms |
| Memory Usage | bytes used / bytes allocated | 60-85% is ideal |
| Key Count | Total keys in cache | Monitor for unbounded growth |

### Redis Monitoring

```bash
# Redis INFO command -- key metrics
redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses|evicted_keys"

# Calculate hit ratio
redis-cli INFO stats | awk -F: '
  /keyspace_hits/  { hits=$2 }
  /keyspace_misses/ { misses=$2 }
  END { printf "Hit ratio: %.2f%%\n", hits/(hits+misses)*100 }
'

# Monitor slow operations
redis-cli SLOWLOG GET 10

# Memory analysis
redis-cli MEMORY DOCTOR
redis-cli INFO memory
```

### Prometheus Metrics for Application Cache

```python
# Python -- Prometheus metrics for cache monitoring
from prometheus_client import Counter, Histogram, Gauge

cache_hits = Counter('cache_hits_total', 'Cache hit count', ['cache_name'])
cache_misses = Counter('cache_misses_total', 'Cache miss count', ['cache_name'])
cache_latency = Histogram(
    'cache_operation_duration_seconds',
    'Cache operation latency',
    ['cache_name', 'operation'],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05]
)
cache_size = Gauge('cache_size_bytes', 'Cache memory usage', ['cache_name'])

def cached_get(key: str, fetch_fn, cache_name: str = 'default'):
    with cache_latency.labels(cache_name, 'get').time():
        result = cache.get(key)

    if result is not None:
        cache_hits.labels(cache_name).inc()
        return result

    cache_misses.labels(cache_name).inc()
    value = fetch_fn()

    with cache_latency.labels(cache_name, 'set').time():
        cache.set(key, value)

    return value
```

---

## Common Pitfalls and Solutions

### Stale Data

**Problem:** Cache serves outdated data after the source of truth changes.

**Solutions:**
- Use short TTLs for frequently changing data
- Implement event-based invalidation on writes
- Use `stale-while-revalidate` to serve stale while refreshing

### Thundering Herd

**Problem:** When a popular cache key expires, hundreds of requests simultaneously hit the origin.

**Solutions:**
- Use locking/mutex (see stampede prevention above)
- Stagger TTLs by adding jitter: `ttl = base_ttl + random(0, ttl * 0.1)`
- Use `stale-while-revalidate` to continue serving expired content

```python
import random

def ttl_with_jitter(base_ttl: int, jitter_pct: float = 0.1) -> int:
    """Add random jitter to TTL to prevent synchronized expiration."""
    jitter = int(base_ttl * jitter_pct)
    return base_ttl + random.randint(-jitter, jitter)
```

### Cache Penetration

**Problem:** Repeated requests for keys that do not exist in the origin (e.g., invalid IDs), bypassing the cache every time.

**Solutions:**
- Cache negative results (null/empty) with a short TTL
- Use a Bloom filter to reject definitely-absent keys

```python
# Cache null results to prevent penetration
def get_item(item_id: str):
    key = f"item:{item_id}"
    cached = r.get(key)

    if cached == "__NULL__":
        return None  # Known absent
    if cached:
        return json.loads(cached)

    item = db.get_item(item_id)
    if item is None:
        r.setex(key, 300, "__NULL__")  # Cache the absence for 5 min
        return None

    r.setex(key, 3600, json.dumps(item))
    return item
```

### Cache Breakdown

**Problem:** A single hot key expires and the origin cannot handle the sudden load.

**Solution:** Never let the hot key expire -- refresh it proactively.

```python
def get_hot_key(key: str, fetch_fn, ttl: int = 3600):
    """Ensure hot keys are refreshed before expiry."""
    remaining = r.ttl(key)

    if remaining > 60:
        # Plenty of time, serve from cache
        return json.loads(r.get(key))

    # TTL is low or expired -- refresh
    value = fetch_fn()
    r.setex(key, ttl, json.dumps(value))
    return value
```

---

## Quick Reference: Choosing a Caching Strategy

| Scenario | Recommended Approach |
|----------|---------------------|
| Static assets (JS, CSS, images) | Browser cache + CDN, long TTL, content-hash filenames |
| API responses (public, read-heavy) | CDN + Redis, moderate TTL, ETag validation |
| User-specific data | Browser cache (private), short TTL, event-based invalidation |
| Database query results | Application-level cache-aside with Redis |
| Expensive computations | Memoization (in-process) or Redis for shared results |
| Session data | Redis with sliding TTL |
| Configuration / feature flags | Read-through cache, event-based invalidation |
| High-write workloads | Write-behind cache with async flush |
| Search results / aggregations | Pre-computed cache warming + moderate TTL |

---

## Summary Checklist

- [ ] Identify hot paths and measure current latency
- [ ] Choose the right caching layer (browser, CDN, app, distributed)
- [ ] Set appropriate TTLs based on data freshness requirements
- [ ] Implement cache invalidation tied to data mutation events
- [ ] Add jitter to TTLs to prevent thundering herd
- [ ] Cache negative results to prevent cache penetration
- [ ] Use locking or probabilistic refresh to prevent stampedes
- [ ] Monitor hit ratio, latency, eviction rate, and memory usage
- [ ] Plan cache warming for cold starts and deployments
- [ ] Document cache keys, TTLs, and invalidation triggers for the team
