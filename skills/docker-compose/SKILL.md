---
name: docker-compose
description: Docker Compose for multi-container local development and production stacks. Use when user mentions "docker-compose", "docker compose", "multi-container", "compose file", "services", "docker networking", "compose volumes", "dev environment setup", or orchestrating multiple containers locally.
---

# Docker Compose

## Compose File Syntax

A `docker-compose.yml` (or `compose.yml` in Compose V2) defines services, networks, and volumes.

```yaml
# compose.yml
services:
  web:
    image: nginx:1.25-alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - frontend
    depends_on:
      api:
        condition: service_healthy

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    networks:
      - backend

  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    networks:
      - backend

volumes:
  pgdata:

networks:
  frontend:
  backend:
```

## Common Service Patterns

### Web + API + Database + Cache

Shown in the example above. The web server reverse-proxies to the API, which talks to both the database and cache on a shared backend network.

### Frontend + Backend + Database

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    environment:
      VITE_API_URL: http://localhost:4000

  backend:
    build: ./backend
    ports:
      - "4000:4000"
    volumes:
      - ./backend/src:/app/src
    depends_on:
      db:
        condition: service_healthy
    environment:
      DB_HOST: db

  db:
    image: mysql:8
    volumes:
      - mysql_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: app
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      retries: 5

volumes:
  mysql_data:
```

## Networking Between Services

Services on the same network can reach each other by service name. DNS resolution is automatic.

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # no external access
```

- A service on `frontend` and `backend` networks can talk to services on both.
- A service only on `backend` cannot reach the internet if `internal: true`.
- Use service names as hostnames: `postgres://db:5432`, `http://api:3000`.

To inspect networking issues at runtime:

```bash
docker network ls
docker network inspect myproject_backend
docker compose exec api ping db
```

## Volume Management

### Named Volumes

Persist data across container restarts. Docker manages the storage location.

```yaml
volumes:
  pgdata:
    driver: local
```

### Bind Mounts

Map host directories into containers. Essential for development hot-reload.

```yaml
services:
  api:
    volumes:
      - ./src:/app/src          # source code
      - /app/node_modules       # anonymous volume to prevent overwrite
```

### tmpfs

In-memory storage. Useful for secrets or scratch data that should not persist.

```yaml
services:
  api:
    tmpfs:
      - /tmp
      - /run:size=64M
```

### Read-Only Mounts

```yaml
volumes:
  - ./config:/etc/app/config:ro
```

## Environment Variables

### Inline

```yaml
services:
  api:
    environment:
      NODE_ENV: production
      LOG_LEVEL: info
```

### From .env File

```yaml
services:
  api:
    env_file:
      - .env
      - .env.local
```

### Variable Substitution

Compose reads a `.env` file in the project root automatically for variable substitution in the YAML itself.

```
# .env
POSTGRES_VERSION=16
APP_PORT=3000
```

```yaml
services:
  db:
    image: postgres:${POSTGRES_VERSION}-alpine
  api:
    ports:
      - "${APP_PORT}:3000"
```

Use defaults with `${VAR:-default}` and required variables with `${VAR:?error message}`.

## Health Checks and depends_on

`depends_on` alone only waits for the container to start, not for the service inside to be ready. Use conditions:

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
      migrations:
        condition: service_completed_successfully
```

Available conditions:
- `service_started` -- container has started (default)
- `service_healthy` -- healthcheck is passing
- `service_completed_successfully` -- container exited with code 0

A healthcheck example for Postgres:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
  interval: 5s
  timeout: 3s
  retries: 5
  start_period: 10s
```

## Development Overrides

Compose automatically merges `docker-compose.override.yml` (or `compose.override.yml`) on top of the base file. Use this for development-specific settings.

```yaml
# compose.yml (base)
services:
  api:
    build: ./api
    environment:
      NODE_ENV: production

# compose.override.yml (dev, loaded automatically)
services:
  api:
    build:
      target: development
    volumes:
      - ./api/src:/app/src
    environment:
      NODE_ENV: development
      DEBUG: "app:*"
    ports:
      - "9229:9229"  # debugger port
```

For explicit file selection:

```bash
docker compose -f compose.yml -f compose.prod.yml up -d
```

## Useful Commands

```bash
# Start all services (detached)
docker compose up -d

# Start and force rebuild
docker compose up -d --build

# Stop and remove containers, networks
docker compose down

# Stop and also remove volumes (destroys data)
docker compose down -v

# View logs (follow mode, last 100 lines)
docker compose logs -f --tail=100
docker compose logs -f api db    # specific services

# Run a one-off command
docker compose exec api sh
docker compose exec db psql -U app -d myapp

# Run a new container (not exec into existing)
docker compose run --rm api npm test

# List running services
docker compose ps

# Pull latest images
docker compose pull

# Restart a single service
docker compose restart api

# Scale a service (stateless services only)
docker compose up -d --scale worker=3

# View resource usage
docker compose top
docker stats
```

## Production Considerations

```yaml
services:
  api:
    restart: unless-stopped          # or: always, on-failure, no
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt   # available at /run/secrets/db_password
```

## Debugging

```bash
# Container won't start -- check logs and exit codes
docker compose ps -a
docker compose logs api
docker compose run --rm api sh          # interactive shell to diagnose

# Service can't reach another service
docker compose exec api getent hosts db
docker network inspect myproject_backend

# Inspect environment and mounts inside a container
docker compose exec api env | sort
docker inspect $(docker compose ps -q db) --format '{{json .Mounts}}' | jq

# Resource usage
docker stats --no-stream

# Validate compose file without starting
docker compose config --quiet
```
