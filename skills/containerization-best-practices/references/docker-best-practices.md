# Container Security and Best Practices

## Dockerfile Best Practices

### 1. Use Specific Base Image Tags

```dockerfile
# ❌ WRONG: Unpredictable, breaks reproducibility
FROM python:latest
FROM ubuntu

# ✅ CORRECT: Specific, reproducible
FROM python:3.11-slim-bookworm
FROM ubuntu:22.04
```

Available tags:
- `python:3.11-slim` - Minimal Python image (~150MB)
- `python:3.11-alpine` - Smallest (~50MB)
- `node:18-alpine` - Minimal Node.js
- `rust:1.74-slim` - Minimal Rust

### 2. Multi-Stage Builds

Reduce final image size dramatically:

```dockerfile
# Stage 1: Builder
FROM golang:1.21 as builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o myapp

# Stage 2: Runtime (much smaller)
FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/myapp .
ENTRYPOINT ["./myapp"]
```

Size comparison:
- Without multi-stage: 800MB
- With multi-stage: 50MB (94% reduction!)

### 3. Layer Optimization

Minimize layers and size:

```dockerfile
# ❌ WRONG: Creates 3 layers
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get clean

# ✅ CORRECT: Creates 1 layer
RUN apt-get update && apt-get install -y python3 && apt-get clean && rm -rf /var/lib/apt/lists/*
```

Benefits:
- Smaller image
- Faster layer download from registry
- Better build caching

### 4. Don't Run as Root

```dockerfile
# ❌ WRONG: Runs as root
FROM python:3.11
COPY app.py .
CMD ["python", "app.py"]

# ✅ CORRECT: Runs as non-root user
FROM python:3.11
RUN useradd -r -u 1001 appuser
COPY --chown=appuser:appuser app.py .
USER appuser
CMD ["python", "app.py"]
```

### 5. Use .dockerignore

```
# .dockerignore
.git
.gitignore
*.md
.env
__pycache__
node_modules
.pytest_cache
.vscode
.DS_Store
*.log
```

### 6. Health Checks

```dockerfile
# Python
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Node.js
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Generic (shell)
HEALTHCHECK --interval=30s CMD /app/healthcheck.sh || exit 1
```

Usage:
```bash
docker run -d --health-cmd="curl -f http://localhost:8000/health" \
    --health-interval=30s \
    --health-retries=3 \
    myapp:latest
```

## Security Best Practices

### 1. Scanning for Vulnerabilities

```bash
# Scan with Trivy
trivy image myimage:latest

# Scan with Docker Scout
docker scout cves myimage:latest

# Scan with Grype
grype myimage:latest
```

### 2. Image Signing and Verification

```bash
# Sign image with Cosign
cosign sign --key cosign.key myimage:latest

# Verify signature
cosign verify --key cosign.pub myimage:latest

# Enforce in Kubernetes
# Use Kyverno or similar policy engines
```

### 3. Secrets Management

```dockerfile
# ❌ WRONG: Hardcoded secrets
ENV DB_PASSWORD=mysecret123

# ✅ CORRECT: Use build secrets
RUN --mount=type=secret,id=db_password \
    DATABASE=$(cat /run/secrets/db_password) && \
    ./configure --db-password=$DATABASE

# Build command
docker build --secret db_password=<(echo mysecret) -t myapp .
```

### 4. Read-Only Filesystem

```dockerfile
FROM python:3.11-slim

# Pre-create necessary writable directories
RUN mkdir -p /tmp /var/run/myapp && \
    chmod 777 /tmp /var/run/myapp

USER appuser

CMD ["python", "app.py"]
```

Run with:
```bash
docker run --read-only --tmpfs /tmp --tmpfs /var/run/myapp myapp
```

## Image Optimization

### Size Comparison

| Base Image | Size | Notes |
|-----------|------|-------|
| ubuntu:22.04 | 77MB | Full OS |
| debian:bookworm-slim | 74MB | Minimal OS |
| python:3.11 | 1.0GB | With build tools |
| python:3.11-slim | 150MB | Smaller |
| python:3.11-alpine | 50MB | Minimal |
| distroless/python3 | 80MB | No OS |
| scratch | 0MB | Empty image |

### Optimization Tips

1. **Use Alpine Linux**: ~5MB base image
2. **Remove documentation**: `--no-install-recommends`
3. **Clean package managers**: `apt-get clean`, `pip cache purge`
4. **Use distroless images**: No OS files, just app
5. **Strip binaries**: Reduce compiled binary size
6. **Compress artifacts**: Use gzip for configs

## Kubernetes Best Practices

### Pod Security Standards

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL
  
  containers:
  - name: app
    image: myapp:1.0.0  # Use specific tag
    imagePullPolicy: Always
    
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsUser: 1001
    
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache
  
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

### Image Pull Policies

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0.0
    imagePullPolicy: Always        # Always pull latest
    # Other options:
    # imagePullPolicy: Never       # Use local only
    # imagePullPolicy: IfNotPresent # Use local if present
```

### Container Registries

**Private Registry Setup:**
```bash
# Docker registry authentication
docker login registry.example.com

# Create Kubernetes secret
kubectl create secret docker-registry regcred \
    --docker-server=registry.example.com \
    --docker-username=user \
    --docker-password=pass

# Use in pod
spec:
  imagePullSecrets:
  - name: regcred
```
