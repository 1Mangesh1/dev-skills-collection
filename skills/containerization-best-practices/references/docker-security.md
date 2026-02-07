# Docker Security Best Practices

## Non-Root User

```dockerfile
# Create user
RUN useradd -m -u 1000 appuser

# Use user
USER appuser

# Don't have write access to /etc, /sys, etc
```

## Secrets Management

### ❌ Bad: Secrets in Build
```dockerfile
RUN npm install --token=$NPM_TOKEN  # Token visible in image
```

### ✓ Good: BuildKit Secrets
```bash
docker build --secret npm_token=/path/to/token --file Dockerfile .
```

```dockerfile
RUN --mount=type=secret,id=npm_token \
  npm install --token=$(cat /run/secrets/npm_token)
```

## Read-Only Filesystem

```dockerfile
# For stateless apps
RUN chmod -R 755 /app
```

Run with:
```bash
docker run --read-only --tmpfs /tmp myapp
```

## Image Scanning

```bash
# Scan with trivy
trivy image myapp:latest

# Scan with dive
dive myapp:latest

# GitHub: Enable Dependabot for base images
```

## Minimal Base Images

| Image | Size |
|-------|------|
| ubuntu:22.04 | 77 MB |
| node:18 | 908 MB |
| node:18-alpine | 170 MB |
| node:18-slim | 206 MB |
| scratch | 0 MB (binary only) |

Use Alpine for most cases.
