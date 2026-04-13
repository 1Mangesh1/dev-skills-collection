---
name: deno
description: Deno runtime for TypeScript/JavaScript with built-in tooling. Use when user mentions "deno", "deno run", "deno task", "deno deploy", "deno.json", "deno compile", "deno test", "deno bench", "deno fmt", "deno lint", "fresh framework", "deno KV", "JSR", "deno permissions", or running TypeScript natively without build steps.
---

# Deno

Deno is a secure TypeScript/JavaScript runtime with built-in tooling. No `node_modules`, no bundler config, no `tsconfig.json` needed. TypeScript runs natively. All APIs use web standards (fetch, Request, Response, Web Streams).

## CLI Commands

```bash
deno run server.ts                    # Run a file
deno run --watch server.ts            # Restart on file changes
deno task dev                         # Run task from deno.json
deno test                             # Run tests
deno bench                            # Run benchmarks
deno fmt                              # Format code
deno lint                             # Lint code
deno check server.ts                  # Type-check without running
deno compile --output myapp server.ts # Compile to standalone binary
deno serve server.ts                  # Run an HTTP server (export default handler)
deno doc mod.ts                       # Generate documentation
deno info server.ts                   # Show dependency tree
deno repl                             # Interactive REPL
deno upgrade                          # Upgrade Deno itself
```

## Permissions Model

Deno is secure by default. Scripts have no file, network, or environment access unless explicitly granted.

```bash
deno run --allow-read server.ts                  # All file reads
deno run --allow-read=/tmp,./data server.ts      # Specific paths only
deno run --allow-write=./output server.ts        # Write to specific dir
deno run --allow-net server.ts                   # All network access
deno run --allow-net=api.example.com server.ts   # Specific hosts
deno run --allow-env=DATABASE_URL,PORT server.ts # Specific env vars
deno run --allow-run=git,deno server.ts          # Specific subprocesses
deno run --allow-ffi server.ts                   # Foreign function interface
deno run --allow-sys server.ts                   # System info (OS, memory)
deno run -A server.ts                            # Allow all (development only)
deno run --deny-net server.ts                    # Explicitly deny network
```

Prompt mode: without flags, Deno asks interactively at runtime. Use `--no-prompt` to deny all unpermitted access silently.

## deno.json Configuration

```jsonc
{
  "tasks": {
    "dev": "deno run --watch --allow-net --allow-read server.ts",
    "test": "deno test --allow-read",
    "build": "deno compile --output dist/app server.ts"
  },
  "imports": {
    "@std/": "jsr:@std/",
    "oak": "jsr:@oak/oak@^17",
    "zod": "npm:zod@^3.23"
  },
  "compilerOptions": {
    "strict": true,
    "jsx": "react-jsx",
    "jsxImportSource": "preact"
  },
  "fmt": {
    "useTabs": false,
    "lineWidth": 100,
    "indentWidth": 2,
    "semiColons": true,
    "singleQuote": false
  },
  "lint": {
    "rules": {
      "exclude": ["no-unused-vars"]
    }
  },
  "exclude": ["node_modules", "dist"],
  "lock": true,
  "nodeModulesDir": "auto"
}
```

The `imports` field replaces import maps. All bare specifiers resolve through it. Run `deno add @std/path` to auto-add entries.

## Standard Library (@std)

All modules live on JSR under `@std`. Add with `deno add @std/<module>`.

```typescript
// File I/O
import { exists, ensureDir, copy, walk } from "@std/fs";
import { join, resolve, basename, extname } from "@std/path";

await ensureDir("./output");
for await (const entry of walk("./src", { exts: [".ts"] })) {
  console.log(entry.path);
}

// HTTP
import { serveDir } from "@std/http/file-server";

// Testing assertions
import { assertEquals, assertThrows, assertRejects } from "@std/assert";

// Text encoding/decoding
import { encodeBase64, decodeBase64 } from "@std/encoding/base64";

// Datetime
import { format, parse } from "@std/datetime";

// Collections
import { groupBy, partition, sortBy } from "@std/collections";

// Async utilities
import { delay, deadline, retry } from "@std/async";
await retry(() => fetch("https://api.example.com"), { maxAttempts: 3 });

// Streams
import { TextLineStream } from "@std/streams";
```

## npm and Node.js Compatibility

Use `npm:` specifiers to import any npm package. No install step needed.

```typescript
import express from "npm:express@4";
import chalk from "npm:chalk@5";
import { z } from "npm:zod@3";

const app = express();
app.get("/", (_req, res) => res.json({ hello: "world" }));
app.listen(3000);
```

Node built-in modules work with `node:` prefix:

```typescript
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createServer } from "node:http";
import { EventEmitter } from "node:events";
```

Set `"nodeModulesDir": "auto"` in `deno.json` for packages that need `node_modules` on disk (native addons, frameworks expecting it).

## JSR (JavaScript Registry)

JSR is a TypeScript-first registry. Packages work in Deno, Node, and Bun.

```bash
deno add @std/path                  # Add to deno.json imports
deno add @oak/oak                   # Add third-party package
```

Publishing to JSR:

```jsonc
// deno.json
{
  "name": "@myorg/mylib",
  "version": "1.0.0",
  "exports": "./mod.ts"
}
```

```bash
deno publish              # Publish to JSR
deno publish --dry-run    # Preview what would be published
```

JSR requires explicit type exports. No `any` in public API signatures.

## HTTP Server

### Deno.serve (recommended)

```typescript
Deno.serve({ port: 8000 }, async (req: Request): Promise<Response> => {
  const url = new URL(req.url);

  if (url.pathname === "/api/health") {
    return Response.json({ status: "ok" });
  }

  if (url.pathname === "/api/users" && req.method === "POST") {
    const body = await req.json();
    return Response.json({ created: body }, { status: 201 });
  }

  if (url.pathname.startsWith("/static/")) {
    const { serveDir } = await import("@std/http/file-server");
    return serveDir(req, { fsRoot: "./public", urlRoot: "static" });
  }

  return new Response("Not Found", { status: 404 });
});
```

### deno serve (multi-worker)

Export a default object with a `fetch` handler. Run with `deno serve`:

```typescript
// server.ts
export default {
  fetch(req: Request): Response {
    return new Response("Hello from Deno!");
  },
};
```

```bash
deno serve --parallel server.ts    # Multi-core, auto-selects worker count
deno serve --port 3000 server.ts
```

### Middleware Pattern

```typescript
type Handler = (req: Request) => Response | Promise<Response>;
type Middleware = (next: Handler) => Handler;

const logger: Middleware = (next) => async (req) => {
  const start = performance.now();
  const res = await next(req);
  console.log(`${req.method} ${new URL(req.url).pathname} ${res.status} ${(performance.now() - start).toFixed(1)}ms`);
  return res;
};

const cors: Middleware = (next) => async (req) => {
  const res = await next(req);
  res.headers.set("Access-Control-Allow-Origin", "*");
  return res;
};

const compose = (...mws: Middleware[]) => (handler: Handler) =>
  mws.reduceRight((h, mw) => mw(h), handler);

const app = compose(logger, cors)((req) => Response.json({ ok: true }));
Deno.serve(app);
```

## Deno KV

Built-in key-value store. Works locally (SQLite-backed) and on Deno Deploy (globally distributed).

```typescript
const kv = await Deno.openKv();       // Local or Deploy
// const kv = await Deno.openKv("https://api.deno.com/databases/<id>/connect");  // Remote

// CRUD
await kv.set(["users", "alice"], { name: "Alice", role: "admin" });
const entry = await kv.get(["users", "alice"]);
console.log(entry.value);   // { name: "Alice", role: "admin" }
console.log(entry.versionstamp);

await kv.delete(["users", "alice"]);

// List by prefix
const iter = kv.list({ prefix: ["users"] });
for await (const entry of iter) {
  console.log(entry.key, entry.value);
}

// Atomic operations (optimistic concurrency)
const user = await kv.get(["users", "alice"]);
const result = await kv.atomic()
  .check(user)   // Fail if versionstamp changed
  .set(["users", "alice"], { ...user.value, role: "superadmin" })
  .sum(["stats", "updates"], 1n)   // Atomic counter
  .commit();
console.log(result.ok);   // true or false

// Enqueue (built-in queue)
await kv.enqueue({ type: "email", to: "alice@example.com", subject: "Welcome" });
kv.listenQueue(async (msg) => {
  console.log("Processing:", msg);
});

// Watch for changes
const stream = kv.watch([["users", "alice"]]);
for await (const [entry] of stream) {
  console.log("Changed:", entry.value);
}
```

## Deno Deploy

Serverless edge platform. Runs Deno code on 35+ regions. Supports Deno KV, BroadcastChannel, cron.

```bash
# Install deployctl
deno install -Arf jsr:@deno/deployctl

# Deploy
deployctl deploy --project=my-app server.ts
deployctl deploy --project=my-app --prod server.ts   # Production deploy

# From GitHub: connect repo in Deno Deploy dashboard for automatic deploys
```

Deno Deploy supports:

- `Deno.serve` for HTTP
- `Deno.openKv()` for globally distributed KV
- `Deno.cron()` for scheduled tasks
- `BroadcastChannel` for cross-isolate communication
- Web standard APIs (fetch, crypto, streams)
- npm packages via `npm:` specifiers

```typescript
// Scheduled tasks on Deploy
Deno.cron("cleanup", "0 * * * *", async () => {
  const kv = await Deno.openKv();
  // Cleanup logic
});
```

## Fresh Framework

Full-stack web framework for Deno. Islands architecture: zero JS shipped by default, interactive components hydrated on demand.

```bash
deno run -A -r https://fresh.deno.dev my-app   # Scaffold project
cd my-app && deno task dev                       # Start dev server
```

### Routes (file-based)

```
routes/
  index.tsx          -> GET /
  about.tsx          -> GET /about
  blog/[slug].tsx    -> GET /blog/:slug
  api/users.ts       -> API route (no UI)
  _layout.tsx        -> Layout wrapper
  _404.tsx           -> Custom 404
```

### Route with Handler

```typescript
// routes/api/users.ts
import { Handlers } from "$fresh/server.ts";

export const handler: Handlers = {
  async GET(_req, ctx) {
    const users = await getUsers();
    return Response.json(users);
  },
  async POST(req, _ctx) {
    const body = await req.json();
    const user = await createUser(body);
    return Response.json(user, { status: 201 });
  },
};
```

### Island Component

```typescript
// islands/Counter.tsx
import { useSignal } from "@preact/signals";

export default function Counter() {
  const count = useSignal(0);
  return (
    <div>
      <p>{count.value}</p>
      <button onClick={() => count.value++}>+1</button>
    </div>
  );
}

// Use in a route (only Counter hydrates on client)
// routes/index.tsx
import Counter from "../islands/Counter.tsx";
export default function Home() {
  return <div><h1>Welcome</h1><Counter /></div>;
}
```

## Testing

```typescript
import { assertEquals, assertRejects, assertThrows } from "@std/assert";
import { describe, it, beforeEach, afterEach } from "@std/testing/bdd";
import { stub, spy, assertSpyCalls } from "@std/testing/mock";
import { FakeTime } from "@std/testing/time";

// Basic
Deno.test("addition", () => {
  assertEquals(1 + 1, 2);
});

// Async
Deno.test("fetch data", async () => {
  const res = await fetch("https://api.example.com/data");
  assertEquals(res.status, 200);
});

// BDD style
describe("UserService", () => {
  let service: UserService;
  beforeEach(() => { service = new UserService(); });

  it("should create a user", async () => {
    const user = await service.create({ name: "Alice" });
    assertEquals(user.name, "Alice");
  });
});

// Mocking
Deno.test("stubbing", () => {
  const fn = spy(() => 42);
  fn();
  assertSpyCalls(fn, 1);

  using _stub = stub(Math, "random", () => 0.5);
  assertEquals(Math.random(), 0.5);
  // Stub auto-restores when _stub goes out of scope (using declaration)
});

// Fake time
Deno.test("fake time", () => {
  using time = new FakeTime();
  const start = Date.now();
  time.tick(1000);
  assertEquals(Date.now() - start, 1000);
});
```

```bash
deno test                              # Run all tests
deno test tests/auth_test.ts           # Specific file
deno test --filter "UserService"       # Filter by name
deno test --coverage=cov_profile       # Collect coverage
deno coverage cov_profile              # Display coverage report
deno coverage cov_profile --lcov > lcov.info  # LCOV output
deno test --doc                        # Test code examples in JSDoc
```

## FFI (Foreign Function Interface)

Call native C/Rust libraries from Deno.

```typescript
const lib = Deno.dlopen("./libmath.so", {
  add: { parameters: ["i32", "i32"], result: "i32" },
  multiply: { parameters: ["f64", "f64"], result: "f64" },
});

console.log(lib.symbols.add(2, 3));        // 5
console.log(lib.symbols.multiply(2.5, 4)); // 10.0
lib.close();
```

Requires `--allow-ffi` (or `-A`). Supported types: `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `f32`, `f64`, `pointer`, `buffer`, `void`.

## WebSocket and WebWorker

### WebSocket Server

```typescript
Deno.serve((req) => {
  if (req.headers.get("upgrade") === "websocket") {
    const { socket, response } = Deno.upgradeWebSocket(req);
    socket.onopen = () => console.log("connected");
    socket.onmessage = (e) => socket.send(`echo: ${e.data}`);
    socket.onclose = () => console.log("disconnected");
    return response;
  }
  return new Response("Not a WebSocket request", { status: 400 });
});
```

### Web Workers

```typescript
// worker.ts
self.onmessage = (e: MessageEvent) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};

// main.ts
const worker = new Worker(new URL("./worker.ts", import.meta.url).href, {
  type: "module",
});
worker.postMessage({ input: "data" });
worker.onmessage = (e) => console.log("Result:", e.data);
```

## Migration from Node.js

1. Rename `package.json` scripts to `deno.json` tasks
2. Replace bare imports with `npm:` specifiers or JSR packages
3. Add `node:` prefix to Node built-in imports (`fs` -> `node:fs`)
4. Add permission flags to run commands
5. Replace `__dirname` with `import.meta.dirname` (Deno 1.40+)
6. Replace `__filename` with `import.meta.filename`
7. Replace `require()` with `import` (Deno supports CJS via `npm:` but prefers ESM)
8. Set `"nodeModulesDir": "auto"` if packages expect `node_modules`

```bash
# Before (Node)
node --env-file=.env server.js

# After (Deno)
deno run --allow-net --allow-read --allow-env server.ts
```

## Deno vs Node vs Bun

| Feature | Deno | Node | Bun |
|---|---|---|---|
| TypeScript | Native, zero config | Requires transpiler | Native |
| Security | Permissions by default | No sandbox | No sandbox |
| Package manager | URL imports + `deno add` | npm/yarn/pnpm | bun install |
| Registry | JSR + npm | npm | npm |
| Formatter | `deno fmt` built-in | Prettier (external) | None built-in |
| Linter | `deno lint` built-in | ESLint (external) | None built-in |
| Test runner | `deno test` built-in | Node test / Jest | `bun test` built-in |
| Config files | `deno.json` only | package.json + many | package.json + bunfig.toml |
| Web standards | First-class | Polyfilled | Partial |
| Edge deploy | Deno Deploy | Various | None native |
| KV store | Deno KV built-in | External (Redis etc.) | External |
| Compile to binary | `deno compile` | pkg/nexe (third-party) | `bun build --compile` |
