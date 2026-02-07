
# Multi-Stage Build Patterns

## Benefits of Multi-Stage Builds

1. **Smaller Images**: 90%+ size reduction
2. **Better Security**: Exclude build tools and source code
3. **Faster Deployment**: Less to download and transfer
4. **Cleaner Separation**: Build stage vs runtime stage

## Pattern 1: Compiled Languages (Golang)

```dockerfile
FROM golang:1.21-alpine as builder

WORKDIR /app
COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM scratch
COPY --from=builder /app/app /
EXPOSE 8080
CMD ["/app"]
```

**Result**: 
- Full builder: 800MB
- Final image: 10MB

## Pattern 2: Node.js with Build Step

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

USER node

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Pattern 3: Python with Virtual Environment

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app.py .

USER nobody
EXPOSE 8000
CMD ["python", "app.py"]
```

## Pattern 4: Java with Multiple Stages

```dockerfile
FROM maven:3.9-eclipse-temurin-21 as builder

WORKDIR /build
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

COPY --from=builder /build/target/*.jar app.jar

RUN useradd -r -u 1001 appuser
USER appuser

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Pattern 5: Frontend Build and Serve

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```
