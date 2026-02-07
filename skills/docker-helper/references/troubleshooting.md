# Docker Troubleshooting Guide

## Common Issues

### Container Won't Start

```bash
# View logs
docker logs container_name

# Run with interactive terminal
docker run -it image_name /bin/bash

# Check image exists
docker images
```

### Out of Disk Space

```bash
# See what's using space
docker system df

# Clean up
docker system prune -a  # WARNING: Removes all unused images
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 8081:8080 image_name
```

### Network Issues

```bash
# Check container network
docker inspect container_name | grep IPAddress

# Ping another container
docker exec container1 ping container2
```

## Docker Compose Tips

```yaml
# Add health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3

# Environment variables
environment:
  - DATABASE_URL=postgres://db:5432/myapp
  - NODE_ENV=production
```

## Performance

- **Limit memory**: `docker run -m 512m image_name`
- **Limit CPU**: `docker run --cpus=1 image_name`
- **Health checks**: Keep them lightweight
