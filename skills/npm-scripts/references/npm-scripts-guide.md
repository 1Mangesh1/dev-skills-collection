# NPM Scripts Guide

## Basic Scripts

```json
{
  "scripts": {
    "start": "node index.js",
    "build": "webpack",
    "test": "jest",
    "dev": "vite",
    "serve": "http-server dist/"
  }
}
```

Run with: `npm run <script>` or `npm start`

## Lifecycle Hooks

Run automatically:

```json
{
  "scripts": {
    "prebuild": "npm run lint",    // Runs before build
    "build": "vite build",
    "postbuild": "npm run test"    // Runs after build
  }
}
```

Install hooks:
```json
{
  "preinstall": "check-node-version",
  "postinstall": "npm run setup"
}
```

## Useful Patterns

### Chaining Commands

```json
{
  "build": "npm run clean && npm run lint && vite build",
  "clean": "rm -rf dist/"
}
```

### Conditional Scripts

```bash
# In script
npm run lint && npm run build || echo "Build failed"
```

### Concurrent Scripts

```json
{
  "build": "npm run build:client & npm run build:server",
  "build:client": "vite build",
  "build:server": "tsc --project tsconfig.server.json"
}
```

Or use concurrently:
```json
{
  "dev": "concurrently \"npm:dev:*\"",
  "dev:client": "vite",
  "dev:server": "node server.js"
}
```

## Tips

- Use `npm run` without arguments to list available scripts
- Prefix with `npm run` (not just command name)
- Pre/post hooks run automatically
- Use `exit 1` on error to fail the build
- Scripts run in order (wait for completion)

## Common Setup

```json
{
  "scripts": {
    "dev": "vite",
    "build": "npm run lint && npm run type-check && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .ts,.tsx",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "test": "vitest",
    "test:ci": "vitest run --coverage",
    "prepare": "husky install"
  }
}
```
