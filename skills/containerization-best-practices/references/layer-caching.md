# Docker Layer Caching Optimization

## Understanding Layers

Each Dockerfile command creates a layer:

```dockerfile
FROM node:18-alpine         # Layer 1
WORKDIR /app                # Layer 2
COPY package.json ./        # Layer 3
RUN npm install             # Layer 4
COPY . .                    # Layer 5
RUN npm run build           # Layer 6
CMD ["npm", "start"]        # Layer 7
```

**Image Size** = Sum of all layers

## Cache Strategy: Order Matters

### ❌ Bad Order (Cache Busts Often)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .              # All code copied
RUN npm install       # Re-runs on any file change
RUN npm run build
```

### ✓ Good Order (Efficient Caching)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./ # Copy dependencies first
RUN npm install       # Cache hit if package.json unchanged
COPY . .              # Copy code
RUN npm run build
```

## Layer Caching in Action

```
Build 1: package.json changes
  Layer 3 (COPY package.json) - MISS (rebuild)
  Layer 4 (RUN npm install)   - MISS (rebuild)
  Layer 5 (COPY . .)          - MISS (rebuild)
  Rebuilds 3+ minutes

Build 2: Only app code changes
  Layer 3 (COPY package.json) - HIT (reuse from cache)
  Layer 4 (RUN npm install)   - HIT (reuse from cache)
  Layer 5 (COPY . .)          - MISS (code changed)
  Rebuilds in seconds
```

## Combine Commands

Reduce layer count:

```dockerfile
# Bad: 3 layers
RUN apt-get update
RUN apt-get install -y curl wget
RUN apt-get clean

# Good: 1 layer
RUN apt-get update && apt-get install -y curl wget && apt-get clean
```

## Remove Build Dependencies

Use multi-stage builds:

```dockerfile
# Build stage
FROM node:18 AS builder
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Runtime stage
FROM node:18-alpine
COPY --from=builder /app/dist ./dist
CMD ["npm", "start"]
```

Only final image includes runtime dependencies, not build tools.
