---
name: turborepo
description: Turborepo for monorepo management — task orchestration, caching, and workspace configuration. Use when user mentions "turborepo", "turbo", "monorepo", "workspace", "turbo.json", "pnpm workspaces", "npm workspaces", "shared packages", "monorepo build", or managing multiple packages in one repository.
---

# Turborepo

Build system for JavaScript/TypeScript monorepos. Handles task orchestration, caching, and dependency-aware execution across workspaces.

## Setup

```bash
# New monorepo
npx create-turbo@latest my-monorepo

# Add to existing repo
pnpm add turbo --save-dev --workspace-root
# or: npm install turbo --save-dev
```

Add `.turbo` to `.gitignore`. Add root scripts:

```json
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint"
  }
}
```

## turbo.json Configuration

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "build/**"],
      "env": ["NODE_ENV"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": [],
      "env": ["CI"]
    },
    "lint": { "outputs": [] },
    "dev": { "cache": false, "persistent": true },
    "typecheck": { "dependsOn": ["^build"], "outputs": [] }
  }
}
```

- `dependsOn` -- tasks that must complete first. `^` prefix = topological (upstream workspaces).
- `outputs` -- files produced by the task, used for caching.
- `cache` -- set `false` to disable caching.
- `persistent` -- marks long-running tasks (dev servers).
- `env` -- environment variables that affect the task hash.

Turborepo v2 uses `"tasks"` instead of the v1 `"pipeline"` key.

## Workspace Structure

```
my-monorepo/
  turbo.json
  package.json
  pnpm-workspace.yaml
  apps/
    web/package.json
    api/package.json
  packages/
    ui/package.json
    shared-types/package.json
    eslint-config/package.json
    tsconfig/package.json
```

## Task Orchestration

```bash
turbo run build                    # all workspaces
turbo run lint build test          # multiple tasks
turbo run build --concurrency=4    # limit parallelism
turbo run build --concurrency=50%  # percentage of CPU cores
```

Turbo analyzes the dependency graph and parallelizes where possible.

## Task Dependencies

`"^build"` means run `build` in all upstream workspace dependencies first. If `apps/web` depends on `packages/ui`, then `packages/ui#build` runs before `apps/web#build`.

`"lint"` (no caret) means run `lint` in the same workspace first:

```json
{ "test": { "dependsOn": ["lint", "build"] } }
```

Per-workspace overrides -- add a `turbo.json` in the workspace directory:

```json
{
  "extends": ["//"],
  "tasks": { "build": { "outputs": [".next/**"] } }
}
```

## Caching

Turbo hashes inputs (source files, deps, env vars, config) and caches task outputs. On a cache hit, outputs are restored and logs replayed without re-execution.

```bash
turbo run build --no-cache   # skip reading cache
turbo run build --force      # ignore cache, re-execute all
```

### Remote caching

```bash
npx turbo login
npx turbo link
```

Connects to Vercel for shared remote caching across team members and CI.

Self-hosted endpoint:

```bash
turbo run build --api="https://cache.example.com" --token="<token>"
```

## Environment Variables

```json
{
  "tasks": {
    "build": {
      "env": ["API_URL", "DATABASE_URL"],
      "passThroughEnv": ["AWS_SECRET_ACCESS_KEY"]
    }
  },
  "globalEnv": ["CI", "VERCEL"]
}
```

- `env` -- affects this task's cache hash.
- `globalEnv` -- affects all tasks' cache hashes.
- `passThroughEnv` -- passed to task but excluded from hash (for secrets).

## Filtering

```bash
turbo run build --filter=web                    # by workspace name
turbo run build --filter=@myorg/ui              # by package name
turbo run test --filter=./apps/*                # by path glob
turbo run build --filter=...@myorg/ui           # package and its dependents
turbo run build --filter=@myorg/ui...           # package and its dependencies
turbo run build --filter=...[HEAD~1]            # changed since last commit
turbo run test --filter=...[main...HEAD]        # changed vs main branch
turbo run build --filter=./apps/* --filter=!./apps/admin  # exclude
```

## Shared Packages

### Internal UI library

`packages/ui/package.json`:

```json
{
  "name": "@myorg/ui",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "lint": "eslint src/"
  }
}
```

Consume with `"@myorg/ui": "workspace:*"` in the app's dependencies. For internal packages transpiled by the consuming bundler, point `main` at TypeScript source and skip the build step.

### Shared TypeScript config

`packages/tsconfig/base.json`:

```json
{
  "compilerOptions": {
    "strict": true, "target": "ES2020", "module": "ESNext",
    "moduleResolution": "bundler", "declaration": true,
    "esModuleInterop": true, "skipLibCheck": true
  }
}
```

Reference: `{ "extends": "@myorg/tsconfig/base.json", "include": ["src"] }`

### Shared types

`packages/shared-types/package.json` -- set `"main"` and `"types"` to `"./src/index.ts"`. No build step needed if consumers transpile directly.

## pnpm Workspaces Integration

`pnpm-workspace.yaml`:

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

Use `workspace:*` protocol for internal deps. For npm workspaces, use the `"workspaces"` field in root `package.json` instead.

## Watch Mode

```bash
turbo watch dev
turbo watch build
```

Watches for file changes, re-runs affected tasks respecting the dependency graph. Shared package changes trigger downstream rebuilds.

## Pruning for Docker

```bash
turbo prune web --docker
```

Produces `out/json/` (pruned package.json files for install layer) and `out/full/` (pruned source).

```dockerfile
FROM node:20-alpine AS builder
RUN corepack enable
WORKDIR /app
COPY . .
RUN turbo prune web --docker

FROM node:20-alpine AS installer
RUN corepack enable
WORKDIR /app
COPY --from=builder /app/out/json/ .
RUN pnpm install --frozen-lockfile
COPY --from=builder /app/out/full/ .
RUN turbo run build --filter=web

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=installer /app/apps/web/.next/standalone ./
CMD ["node", "apps/web/server.js"]
```

## CI/CD Patterns

### GitHub Actions with remote cache

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: turbo run build test lint
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

Run only affected tasks: `turbo run build test --filter=...[origin/main...HEAD]`

Use `turbo run build --dry-run=json` to get the task graph for dispatching parallel CI jobs per workspace.

## Migration from Lerna or Nx

### From Lerna

1. Remove `lerna.json` and `lerna` dependency.
2. Keep workspace config (`package.json` workspaces or `pnpm-workspace.yaml`).
3. Create `turbo.json` with task definitions matching Lerna scripts.
4. Replace `lerna run build` with `turbo run build`.
5. Replace `lerna run test --scope=pkg` with `turbo run test --filter=pkg`.

### From Nx

1. Remove `nx.json`, `project.json` files, and `nx` dependencies.
2. Move task config from `project.json` targets into `turbo.json` tasks.
3. Replace `nx run-many -t build` with `turbo run build`.
4. Replace `nx affected -t test` with `turbo run test --filter=...[origin/main...HEAD]`.

Differences: Nx uses per-project `project.json` and its own dependency analysis; Turbo uses a single root `turbo.json` and relies on the package manager's workspace graph. Nx has generators/executors; Turbo delegates to workspace `package.json` scripts.

## Troubleshooting

```bash
turbo run build --dry-run       # show what would run
turbo run build --graph         # output task graph (DOT format)
turbo run build --summarize     # generate run summary JSON
turbo ls                        # list workspaces
turbo ls --filter=./packages/*  # list filtered workspaces
TURBO_LOG_VERBOSITY=debug turbo run build  # debug cache misses
```
