# Containerization Best Practices Quick Start

Build efficient and secure Docker images with production-ready practices.

## Multi-Stage Builds (Essential!)

```dockerfile
# Build stage - includes all build tools
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage - small, clean image
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

Benefits: 90%+ smaller images, fewer vulnerabilities

## Optimization Tips

### 1. Use Alpine Images
```dockerfile
# ❌ 330MB
FROM ubuntu:22.04

# ✅ 50MB
FROM node:18-alpine
```

### 2. Layer Caching
```dockerfile
# ❌ Bad - no caching
COPY . .
RUN npm install

# ✅ Good - install cached
COPY package*.json ./
RUN npm install
COPY . .
```

### 3. Minimize Layers
Combine RUN commands with `&&` to reduce layers

### 4. .dockerignore
```
node_modules
npm-debug.log
.git
README.md
.env
coverage
tests
```

## Security Checklist

- [ ] Run as non-root user
- [ ] Don't include secrets in image
- [ ] Scan image for vulnerabilities
- [ ] Keep base image updated
- [ ] Remove unnecessary tools
- [ ] Use read-only filesystems when possible

### Non-Root User
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:3000/health || exit 1
```

## Image Tagging Strategy

```bash
docker tag myapp:latest myapp:1.0.0
docker tag myapp:latest myapp:$(git rev-parse --short HEAD)
docker push myapp:1.0.0
```

## Docker Compose Example

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
```

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| Large images | Multi-stage builds, alpine |
| Layer caching broken | Order: deps first, then code |
| Secrets in image | Use build args or env vars |
| Security issues | Scan with `docker scan` |

## Debugging Commands

```bash
# Run interactive shell
docker run -it myapp:latest /bin/sh

# Inspect image
docker inspect myapp:latest

# View image history
docker history myapp:latest

# Check vulnerabilities
docker scan myapp:latest
trivy image myapp:latest
```

## Build Performance

```bash
# Enable BuildKit (better caching)
export DOCKER_BUILDKIT=1
docker build -t myapp .

# View build stats
docker buildx build --progress=plain .
```

## Tools & Commands

- `docker build` - Build images
- `docker scan` - Vulnerability scanning
- `trivy` - Container security scanner
- `docker compose` - Multi-container apps

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dockerfile_best-practices/)
- [Google Container Best Practices](https://cloud.google.com/architecture/best-practices-for-running-cost-effective-kubernetes-applications-on-gke)

## See Also

- SKILL.md - Advanced Docker patterns
- metadata.json - Container tools references
