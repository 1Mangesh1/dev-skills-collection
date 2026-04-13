---
name: bun-runtime
description: Bun runtime for fast JavaScript/TypeScript execution, package management, bundling, and testing. Use when user mentions "bun", "bun run", "bun install", "bunx", "bun test", "bun build", "fast node alternative", "bun shell", or migrating from Node to Bun.
---

# Bun Runtime

Bun is an all-in-one JavaScript/TypeScript runtime, package manager, bundler, and test runner.

## Runtime

Bun runs `.ts`, `.tsx`, `.js`, and `.jsx` files directly. No compilation step or tsconfig required.

```bash
bun run index.ts              # Run a file
bun --watch run server.ts     # Restart on file changes
bun --hot run server.ts       # Hot reload (preserves state)
```

## Package Management

Uses a binary lockfile (`bun.lockb`). Commit it to version control.

```bash
bun install                        # Install all deps
bun add express                    # Add dependency
bun add -d typescript @types/node  # Add dev dependency
bun add -g serve                   # Global install
bun remove express                 # Remove dependency
bun update                         # Update deps
```

By default, postinstall scripts do not run. Allow specific packages in `package.json`:

```json
{ "trustedDependencies": ["sharp", "esbuild"] }
```

Or run `bun install --trust` to allow all.

## Running Scripts

```bash
bun run dev                          # Run package.json script
bun dev                              # Shorthand (same thing)
bunx cowsay hello                    # One-off binary (like npx)
bun --env-file=.env.local run app.ts # Custom env file
```

## Bun Shell

Cross-platform shell via `$` tagged template. Works on macOS, Linux, and Windows.

```typescript
import { $ } from "bun";

const result = await $`ls -la`.text();
const count = await $`cat file.txt | wc -l`.text();

const dir = "/tmp";
await $`ls ${dir}`;                              // Safe interpolation
await $`echo "hello" > output.txt`;              // Redirect
await $`noisy-command`.quiet();                   // Suppress stdout
const { exitCode } = await $`cmd`.nothrow();     // No throw on failure

for await (const line of $`tail -f log.txt`.lines()) {
  console.log(line);                             // Stream lines
}
```

## Built-in Test Runner

Jest-compatible syntax with `bun:test`.

```bash
bun test                       # Run all tests
bun test auth.test.ts          # Specific file
bun test --grep "login"        # Filter by pattern
bun test --watch               # Watch mode
bun test --coverage            # Coverage report
bun test --update-snapshots    # Update snapshots
```

### Writing Tests

```typescript
import { test, expect, describe, mock, spyOn } from "bun:test";

describe("math", () => {
  test("addition", () => {
    expect(1 + 1).toBe(2);
  });
  test("async", async () => {
    const result = await fetchData();
    expect(result).toEqual({ id: 1 });
  });
});

// Mocking
const fn = mock(() => 42);
fn();
expect(fn).toHaveBeenCalled();

mock.module("./db", () => ({
  query: mock(() => [{ id: 1 }]),
}));

// Snapshots
test("snapshot", () => {
  expect({ users: [{ name: "Alice" }] }).toMatchSnapshot();
});
```

## Built-in Bundler

```bash
bun build ./src/index.ts --outdir ./dist --target browser
bun build ./src/index.ts --outdir ./dist --target node
bun build ./src/index.ts --outdir ./dist --target bun
bun build ./src/cli.ts --compile --outfile mycli    # Standalone binary
bun build ./src/index.ts --outdir ./dist --minify
```

Programmatic API:

```typescript
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./dist",
  target: "browser",
  minify: true,
  splitting: true,
  sourcemap: "external",
});
if (!result.success) {
  for (const log of result.logs) console.error(log);
}
```

## HTTP Server

```typescript
Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/health") return Response.json({ status: "ok" });
    if (req.method === "POST" && url.pathname === "/api/data") {
      return Response.json({ received: await req.json() });
    }
    return new Response("Not Found", { status: 404 });
  },
  error(error) {
    return new Response(`Error: ${error.message}`, { status: 500 });
  },
});
```

### WebSocket Support

```typescript
Bun.serve({
  fetch(req, server) {
    if (server.upgrade(req)) return;
    return new Response("Not a WebSocket request", { status: 400 });
  },
  websocket: {
    open(ws) { console.log("connected"); },
    message(ws, message) { ws.send(`echo: ${message}`); },
    close(ws) { console.log("disconnected"); },
  },
});
```

## File I/O

`Bun.file` and `Bun.write` are optimized alternatives to `node:fs`.

```typescript
const file = Bun.file("data.json");
const text = await file.text();
const json = await file.json();
const exists = await file.exists();
console.log(file.size, file.type);

await Bun.write("output.txt", "hello world");
await Bun.write("data.json", JSON.stringify({ key: "value" }));
await Bun.write("copy.txt", Bun.file("original.txt"));

// Write a fetch response directly to disk
await Bun.write("image.png", await fetch("https://example.com/image.png"));
```

## SQLite (Built-in)

```typescript
import { Database } from "bun:sqlite";

const db = new Database("app.db");
db.run(`CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, email TEXT UNIQUE
)`);

const insert = db.prepare("INSERT INTO users (name, email) VALUES (?, ?)");
insert.run("Alice", "alice@example.com");

const users = db.prepare("SELECT * FROM users WHERE name = ?").all("Alice");

const insertMany = db.transaction((entries) => {
  for (const u of entries) insert.run(u.name, u.email);
});
insertMany([
  { name: "Bob", email: "bob@example.com" },
  { name: "Carol", email: "carol@example.com" },
]);
db.close();
```

## Environment Variables

Bun auto-loads `.env` files. No `dotenv` package needed.

```typescript
const port = Bun.env.PORT ?? "3000";
const secret = process.env.SECRET_KEY;  // process.env also works
```

Load order (later overrides earlier):
`.env` < `.env.local` < `.env.${NODE_ENV}` < `.env.${NODE_ENV}.local` < actual environment.

Custom env file: `bun --env-file=.env.staging run server.ts`

## Node.js Compatibility

Works: `node:fs`, `node:path`, `node:os`, `node:crypto`, `node:buffer`, `node:http`, `node:https`,
`node:stream`, `node:events`, `node:util`, `node:child_process`, `node:worker_threads`.
CJS/ESM interop works. `__dirname` and `__filename` available in ESM. NAPI native addons supported.

Known gaps: `node:vm` (limited), `node:dgram` (partial), `node:inspector` (no), `node:http2` (partial),
`node:cluster` (no). Some native addons may not work. See https://bun.sh/docs/runtime/nodejs-apis.

## Migration from npm/yarn/pnpm

1. Remove old lockfile: `rm package-lock.json yarn.lock pnpm-lock.yaml`
2. Run `bun install` to generate `bun.lockb`
3. Replace `npx` with `bunx`, `node` with `bun` in scripts
4. Update CI/CD:

```yaml
# GitHub Actions
- uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest
- run: bun install
- run: bun test
- run: bun run build
```

5. Run `bun test` and fix any failures from unsupported Node.js APIs. You can still use `node` for specific scripts.

## Workspaces

```json
{ "workspaces": ["packages/*", "apps/*"] }
```

```bash
bun install                                # Install all workspace deps
bun run --filter '@myorg/api' dev          # Run script in workspace
bun add zod --filter '@myorg/api'          # Add dep to workspace
```

## Common Patterns

### API Server

```typescript
Bun.serve({
  port: Bun.env.PORT ?? 3000,
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/users" && req.method === "GET") {
      const db = new (await import("bun:sqlite")).Database("app.db");
      return Response.json(db.prepare("SELECT * FROM users").all());
    }
    return new Response("Not Found", { status: 404 });
  },
});
```

### CLI Tool

```typescript
#!/usr/bin/env bun
const command = Bun.argv[2];
switch (command) {
  case "init":
    await Bun.write("config.json", JSON.stringify({ version: 1 }, null, 2));
    break;
  case "build":
    const result = await Bun.build({ entrypoints: ["./src/index.ts"], outdir: "./dist" });
    console.log(result.success ? "Build succeeded" : "Build failed");
    break;
  default:
    console.log("Usage: mycli <init|build>");
}
```

Compile to standalone: `bun build ./cli.ts --compile --outfile mycli`

### Script Runner

```typescript
import { $ } from "bun";
await $`bun test`;
await $`bun run build`;
await $`docker build -t myapp .`;
await $`docker push myapp:latest`;
```

Run with `bun run scripts/deploy.ts`.
