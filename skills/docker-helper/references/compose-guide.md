# Docker Compose Best Practices

## Structure

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://db/myapp
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD=postgres
    volumes:
      - db_data:/var/lib/postgresql/data

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  db_data:

networks:
  default:
    name: app-network
```

## Common Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Execute command in service
docker-compose exec web npm test

# Scale service
docker-compose up -d --scale worker=3

# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v
```

## Networking

All services can reach each other by service name:
- `web` service reaches `db` at `postgres://db:5432`
- No need for `localhost`

## Development vs Production

Development:
```yaml
services:
  web:
    build: .          # Build from source
    volumes:          # Mount local code
      - .:/app
    environment:
      - DEBUG=true
```

Production:
```yaml
services:
  web:
    image: myapp:1.0.0   # Pre-built image
    restart: always      # Auto-restart on crash
    environment:
      - DEBUG=false
```
