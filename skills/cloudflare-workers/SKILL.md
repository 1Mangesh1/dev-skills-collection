---
name: cloudflare-workers
description: Cloudflare Workers for edge computing, serverless functions, and global deployment. Use when user mentions "cloudflare workers", "wrangler", "edge functions", "serverless edge", "cloudflare pages", "D1 database", "R2 storage", "KV store", "workers AI", "edge computing", or deploying to Cloudflare.
---

# Cloudflare Workers

## Setup

```bash
npm install -g wrangler && wrangler login
wrangler init my-worker
```

### wrangler.toml

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"
[vars]
ENVIRONMENT = "production"
[[kv_namespaces]]
binding = "MY_KV"
id = "abc123"
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "def456"
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"
```

## Worker Basics

```typescript
interface Env {
  MY_KV: KVNamespace; DB: D1Database; BUCKET: R2Bucket;
  ENVIRONMENT: string; API_KEY: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/api/health") return Response.json({ status: "ok" });
    if (request.method === "POST" && url.pathname === "/api/data") {
      const body = await request.json();
      return new Response("Created", { status: 201 });
    }
    return new Response("Not Found", { status: 404 });
  },
};
```

## Wrangler CLI

```bash
wrangler dev                    # local dev server on localhost:8787
wrangler dev --remote           # dev against real Cloudflare infrastructure
wrangler deploy                 # deploy to production
wrangler tail                   # stream live logs from deployed worker
wrangler secret put API_KEY     # set an encrypted secret
wrangler secret list            # list configured secrets
wrangler delete                 # remove the deployed worker
```

## Routing

Manual routing with a map, or use `hono`/`itty-router` for path params:

```typescript
// Manual
const routes: Record<string, () => Promise<Response>> = {
  "/api/users": () => handleUsers(request),
  "/api/posts": () => handlePosts(request),
};
const handler = routes[new URL(request.url).pathname];
if (handler) return handler();

// Hono (recommended for complex routing)
import { Hono } from "hono";
const app = new Hono<{ Bindings: Env }>();
app.get("/users/:id", (c) => c.json({ id: c.req.param("id") }));
export default app;
```

## KV Store

Global, low-latency key-value store. Eventually consistent. Best for read-heavy data.

```bash
wrangler kv namespace create MY_KV
wrangler kv namespace create MY_KV --preview
```

```typescript
await env.MY_KV.put("user:123", JSON.stringify({ name: "Alice" }), {
  expirationTtl: 3600, metadata: { created: Date.now() },
});
const value = await env.MY_KV.get("user:123", "json");
const list = await env.MY_KV.list({ prefix: "user:", limit: 100 });
await env.MY_KV.delete("user:123");
```

## D1 Database

SQLite at the edge with queries, transactions, and migrations.

```bash
wrangler d1 create my-db
wrangler d1 execute my-db --command "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
wrangler d1 migrations create my-db init
wrangler d1 migrations apply my-db
```

```typescript
const { results } = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId).all();
await env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Alice").run();
await env.DB.batch([
  env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Bob"),
  env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Carol"),
]);
const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(1).first();
```

## R2 Storage

S3-compatible object storage with no egress fees.

```bash
wrangler r2 bucket create my-bucket
```

```typescript
// Upload
await env.BUCKET.put("images/photo.jpg", imageData, {
  httpMetadata: { contentType: "image/jpeg" },
});
// Download
const object = await env.BUCKET.get("images/photo.jpg");
if (object) {
  return new Response(object.body, {
    headers: { "Content-Type": object.httpMetadata?.contentType ?? "application/octet-stream" },
  });
}
// List, delete
const listed = await env.BUCKET.list({ prefix: "images/", limit: 50 });
await env.BUCKET.delete("images/photo.jpg");
```

For large files use `createMultipartUpload()`, `uploadPart()`, `complete()`.

## Durable Objects

Strongly consistent, stateful compute. Each object has a unique ID and private storage. Use for rate limiters, WebSocket coordination, collaborative editing, session state.

```toml
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"
[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

```typescript
export class Counter implements DurableObject {
  constructor(private state: DurableObjectState, private env: Env) {}
  async fetch(request: Request): Promise<Response> {
    const current = (await this.state.storage.get<number>("count")) ?? 0;
    await this.state.storage.put("count", current + 1);
    return Response.json({ count: current + 1 });
  }
}
// Calling from a worker:
const id = env.COUNTER.idFromName("my-counter");
const response = await env.COUNTER.get(id).fetch(request);
```

## Workers AI

Run ML models at the edge. Add `[ai]` with `binding = "AI"` to wrangler.toml.

```typescript
// Text generation
const resp = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
  messages: [{ role: "user", content: "Summarize this article." }],
});
// Embeddings
const emb = await env.AI.run("@cf/baai/bge-base-en-v1.5", { text: ["document to embed"] });
// Image classification
const cls = await env.AI.run("@cf/microsoft/resnet-50", { image: await request.arrayBuffer() });
```

## Environment Variables and Secrets

Non-sensitive values go in `wrangler.toml` under `[vars]`. Set secrets with `wrangler secret put API_KEY`. Both accessed through `env.API_KEY`, `env.ENVIRONMENT`, etc.

Multiple environments:

```toml
[env.staging]
name = "my-worker-staging"
vars = { ENVIRONMENT = "staging" }
[env.production]
name = "my-worker-production"
vars = { ENVIRONMENT = "production" }
```

Deploy with `wrangler deploy --env staging` or `--env production`.

## Cron Triggers

```toml
[triggers]
crons = ["0 */6 * * *", "30 8 * * 1"]
```

```typescript
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(doCleanup(env));
  },
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return new Response("OK");
  },
};
```

Test locally: `curl "http://localhost:8787/__scheduled?cron=0+*/6+*+*+*"`

## Middleware Patterns

### CORS

```typescript
function corsHeaders(origin: string): HeadersInit {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };
}
```

### Auth

```typescript
async function requireAuth(request: Request, env: Env): Promise<Response | null> {
  const token = request.headers.get("Authorization")?.replace("Bearer ", "");
  if (!token || token !== env.API_KEY) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  return null; // proceed
}
```

### Rate Limiting

Use a Durable Object to track request timestamps per key. Store timestamps in storage, filter to the current window, reject if over limit, append and persist otherwise.

## Local Development

```bash
wrangler dev                     # local server with miniflare runtime
wrangler dev --persist-to=./data # persist KV/D1/R2 data locally
wrangler dev --port 3000         # custom port
wrangler dev --remote            # proxy to Cloudflare (real bindings)
```

Miniflare simulates KV, D1, R2, Durable Objects, and caches locally.

## Deployment

```bash
wrangler deploy                      # deploy to production
wrangler deploy --env staging        # named environment
wrangler deploy --dry-run            # validate without deploying
wrangler versions list               # list deployed versions
wrangler rollback                    # rollback to previous version
```

Custom domains:

```toml
routes = [{ pattern = "api.example.com/*", zone_name = "example.com" }]
```

## Common Patterns

### API Proxy

```typescript
async function proxyRequest(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  url.hostname = "api.upstream.com";
  return fetch(new Request(url.toString(), {
    method: request.method,
    headers: { ...Object.fromEntries(request.headers), "X-API-Key": env.UPSTREAM_KEY },
    body: request.body,
  }));
}
```

### Edge Cache

```typescript
async function cachedFetch(request: Request, ctx: ExecutionContext): Promise<Response> {
  const cache = caches.default;
  let response = await cache.match(request);
  if (response) return response;
  response = await fetch("https://api.origin.com" + new URL(request.url).pathname);
  const cached = new Response(response.body, response);
  cached.headers.set("Cache-Control", "s-maxage=300");
  ctx.waitUntil(cache.put(request, cached.clone()));
  return cached;
}
```

### Webhook Handler

```typescript
async function handleWebhook(request: Request, env: Env): Promise<Response> {
  const signature = request.headers.get("X-Signature-256") ?? "";
  const body = await request.text();
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(env.WEBHOOK_SECRET),
    { name: "HMAC", hash: "SHA-256" }, false, ["verify"]
  );
  const valid = await crypto.subtle.verify(
    "HMAC", key, hexToBytes(signature.replace("sha256=", "")),
    new TextEncoder().encode(body)
  );
  if (!valid) return new Response("Invalid signature", { status: 401 });
  return new Response("OK", { status: 200 });
}
```

### URL Shortener

```typescript
app.post("/shorten", async (c) => {
  const { url } = await c.req.json();
  const id = crypto.randomUUID().slice(0, 8);
  await c.env.MY_KV.put(`url:${id}`, url, { expirationTtl: 86400 * 30 });
  return c.json({ short: `${new URL(c.req.url).origin}/${id}` });
});
app.get("/:id", async (c) => {
  const target = await c.env.MY_KV.get(`url:${c.req.param("id")}`);
  if (!target) return c.text("Not found", 404);
  return c.redirect(target, 302);
});
```

## Limits

| Resource | Free | Paid |
|---|---|---|
| CPU time/request | 10 ms | 30 s (Unbound) / 50 ms |
| Memory | 128 MB | 128 MB |
| Worker size | 1 MB | 10 MB |
| Subrequests (fetch) | 50 | 1000 |
| KV reads/day | 100K | 10M+ |
| KV writes/day | 1K | 1M+ |
| D1 rows read/day | 5M | 50B |
| D1 rows written/day | 100K | 50M |
| R2 Class A ops/month | 1M | $4.50/M |
| R2 storage | 10 GB | $0.015/GB-mo |
| Cron triggers | 3 | 3+ |
| Request body size | 100 MB | 100 MB |

Key constraints: no raw TCP/UDP sockets (use WebSockets or Tunnels). `crypto.subtle` available. Node.js built-ins partially supported via `nodejs_compat` flag. Globals persist within an isolate but not across cold starts. `ctx.waitUntil()` extends execution after response for background work.
