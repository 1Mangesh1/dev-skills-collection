---
name: containerization-best-practices
description: Container and Docker best practices for production workloads. Use when user asks to "optimize Docker", "Docker best practices", "container security", "image optimization", "layer caching", "multi-stage builds", "container networking", "volume management", "Docker performance", "reduce image size", "container hardening", "Dockerfile lint", "health checks", "graceful shutdown", "container debugging", "resource limits", "distroless", "tini init", "container logging", or mentions containerization strategies and Docker optimization.
---

# Containerization & Docker Best Practices

Production-grade Docker and containerization strategies for building efficient, secure, and maintainable containers.

## Dockerfile Best Practices

### Layer Ordering

Order instructions from least to most frequently changing. System deps first, then app deps, then source code. Each instruction creates a layer. Docker caches layers top-down and invalidates everything below a changed layer.

```dockerfile
FROM node:20-alpine
RUN apk add --no-cache tini curl
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

### Multi-Stage Builds

Separate build-time dependencies from runtime. Only copy artifacts you need.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
USER app
CMD ["node", "dist/index.js"]
```

For statically linked binaries (Go, Rust), use `scratch` or `gcr.io/distroless/static-debian12` as the final stage for minimal images (~2MB).

### .dockerignore

Reduces build context size and prevents secrets from leaking into images.

```
.git
node_modules
.env
.env.*
*.md
coverage
tests
__pycache__
.venv
docker-compose*.yml
Dockerfile*
```

## Base Image Selection

| Image            | Size    | Shell | Use Case              |
|------------------|---------|-------|-----------------------|
| `node:20`        | ~350MB  | Yes   | Avoid in prod         |
| `node:20-slim`   | ~200MB  | Yes   | Good default          |
| `node:20-alpine` | ~50MB   | Yes   | Best for most apps    |
| `distroless`     | ~2-20MB | No    | Maximum security      |

### Pin Versions

Never use `latest` in production. Pin to patch version, or digest for full reproducibility.

```dockerfile
FROM node:20.11.1-alpine3.19
FROM node:20.11.1-alpine3.19@sha256:abcdef1234...
```

## Security Hardening

### Non-Root User

```dockerfile
# Alpine
RUN addgroup -S app && adduser -S -G app -s /sbin/nologin app
# Debian
RUN groupadd -r app && useradd -r -g app -s /usr/sbin/nologin -M app

COPY --chown=app:app . .
USER app
```

### Read-Only Filesystem

```bash
docker run --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  -v appdata:/app/data \
  myapp:latest
```

### No Secrets in Images

Secrets in Dockerfile instructions persist in layer history.

```dockerfile
# WRONG
ENV API_KEY=sk-secret-key
COPY .env /app/.env

# RIGHT - BuildKit secrets
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci

# RIGHT - runtime injection
# docker run -e DB_PASS="$(vault read -field=password secret/db)" myapp
```

### Image Scanning

```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest
grype myapp:latest --fail-on high
docker scout cves myapp:latest
```

### Drop Capabilities

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp:latest
```

## Layer Caching Optimization

### Dependency Install Before Code Copy

Copy manifests first, install, then copy source. This is the single most impactful caching rule.

```dockerfile
# Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Go
COPY go.mod go.sum ./
RUN go mod download
COPY . .
```

### BuildKit Cache Mounts

Persist package manager caches across builds.

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends curl

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev
```

Enable BuildKit: `export DOCKER_BUILDKIT=1`

## Health Checks

```dockerfile
# HTTP check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# TCP check (no curl/wget needed)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD nc -z localhost 3000 || exit 1
```

### Compose Health Checks with Dependencies

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
```

## Container Networking

```bash
# Bridge - isolated network, containers resolve by name
docker network create app-net
docker run --network app-net --name api myapp
docker run --network app-net --name worker myworker
# worker reaches api at http://api:3000

# Host - shares host network stack, no port mapping needed
docker run --network host myapp

# Overlay - multi-host (Swarm)
docker network create --driver overlay --attachable cluster-net
```

Containers on user-defined bridge networks get DNS resolution by container name. The default bridge network does not provide this.

## Volume Management

```bash
# Named volumes - Docker-managed, persistent data
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Bind mounts - host directory, good for dev
docker run -v "$(pwd)/src":/app/src:ro myapp

# tmpfs - in-memory, good for secrets/scratch
docker run --tmpfs /tmp:rw,noexec,nosuid,size=128m myapp

# Backup a volume
docker run --rm -v pgdata:/data -v "$(pwd)":/backup \
  alpine tar czf /backup/pgdata-backup.tar.gz -C /data .
```

## Logging Best Practices

Applications should write to stdout/stderr, never to files inside the container.

```dockerfile
RUN ln -sf /dev/stdout /var/log/app.log \
 && ln -sf /dev/stderr /var/log/app-error.log
```

```bash
# JSON file driver with rotation (default)
docker run --log-driver json-file \
  --log-opt max-size=10m --log-opt max-file=3 myapp

# Syslog driver
docker run --log-driver syslog \
  --log-opt syslog-address=udp://loghost:514 myapp
```

Set defaults in daemon.json: `{ "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "5" } }`

## Resource Limits

```bash
docker run -m 512m --cpus=1.0 --pids-limit=256 myapp

# Memory with swap
docker run -m 512m --memory-swap 1g myapp

# CPU shares (relative weight, default 1024)
docker run --cpu-shares=512 myapp
```

### Compose Resource Limits

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

## Debugging Containers

```bash
docker exec -it <container> sh              # shell into running container
docker logs -f --timestamps --tail 100 <ctr> # follow logs
docker inspect <container>                    # full config/state/network
docker inspect --format='{{.State.Health.Status}}' <ctr>
docker stats <container>                      # live resource usage
docker history --no-trunc myapp:latest        # image layer sizes
docker cp <ctr>:/app/error.log ./error.log    # copy files out
docker run -it --entrypoint sh myapp:latest   # debug crashed container
docker run --rm --network container:<ctr> nicolaka/netshoot  # network debug
```

## Production Patterns

### Graceful Shutdown and Signal Handling

Containers receive SIGTERM on stop. The app must handle it or Docker sends SIGKILL after the grace period (default 10s). Always use exec form so the app is PID 1.

```dockerfile
CMD ["node", "server.js"]
# NOT: CMD node server.js  (wraps in /bin/sh, swallows signals)
```

```javascript
process.on('SIGTERM', () => {
  server.close(() => {
    db.disconnect().then(() => process.exit(0));
  });
  setTimeout(() => process.exit(1), 10000);
});
```

### Init System with Tini

Use tini as PID 1 to reap zombie processes and forward signals.

```dockerfile
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

Or: `docker run --init myapp:latest`

### Stop Grace Period

```yaml
services:
  app:
    stop_grace_period: 30s
```

## Image Size Reduction

1. Multi-stage builds to exclude compilers and build tools
2. Alpine or distroless base images
3. Combine RUN commands to reduce layers
4. Remove caches in the same layer they are created
5. Use `--no-install-recommends` (apt) or `--no-cache` (apk)

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
```

```bash
docker history myapp:latest                    # layer sizes
dive myapp:latest                              # interactive analysis
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

## Container Orchestration Considerations

### Labels and Metadata

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/org/repo"
LABEL org.opencontainers.image.version="1.2.3"
```

### Docker Compose Production Stack

```yaml
services:
  app:
    build:
      context: .
      target: runtime
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data
    networks:
      - backend

volumes:
  redisdata:

networks:
  backend:
```

### Image Registry

```bash
docker tag myapp:latest registry.example.com/myapp:1.2.3
docker tag myapp:latest registry.example.com/myapp:${GIT_SHA:0:8}
cosign sign --key cosign.key registry.example.com/myapp:1.2.3
docker image prune -a --filter "until=168h"
```

## References

- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Distroless Images: https://github.com/GoogleContainerTools/distroless
- Trivy Scanner: https://github.com/aquasecurity/trivy
- Tini Init: https://github.com/krallin/tini
