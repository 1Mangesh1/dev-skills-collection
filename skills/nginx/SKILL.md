---
name: nginx
description: Nginx web server configuration for reverse proxy, SSL/TLS, load balancing, static hosting, caching, and security hardening. Use when user asks to "configure nginx", "set up reverse proxy", "add SSL", "nginx location block", "load balancer config", "serve static files", "nginx rate limiting", "nginx caching", "nginx security headers", "nginx gzip", "nginx docker", "fix 502 bad gateway", "fix 413 entity too large", "nginx rewrite", "nginx redirect", "nginx access control", "nginx logging", "nginx performance tuning", or any web server configuration tasks.
---

# Nginx

Web server configuration, reverse proxy, SSL/TLS, load balancing, caching, and security.

## Configuration Structure

```nginx
# /etc/nginx/nginx.conf — contexts nest: main → events/http → server → location
main context          # worker_processes, error_log, pid
├── events { }        # worker_connections, multi_accept
├── http { }          # upstream, server, mime types, logging
│   ├── server { }    # listen, server_name, ssl
│   │   └── location { }  # request routing
│   └── upstream { }  # backend pools
└── stream { }        # TCP/UDP proxying (mail, databases)
```

```bash
# File layout (Debian/Ubuntu)
/etc/nginx/nginx.conf              # main config
/etc/nginx/sites-available/        # virtual host configs
/etc/nginx/sites-enabled/          # symlinks to available
/etc/nginx/conf.d/                 # additional configs (auto-included)
/etc/nginx/snippets/               # reusable config fragments
```

## Basic Server Block

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/myapp;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket upgrade
    location /ws/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
```

## Load Balancing

```nginx
upstream backend {
    server 127.0.0.1:3001;          # round-robin (default)
    server 127.0.0.1:3002;
    server 127.0.0.1:3003 backup;   # only when others are down
}

upstream backend_sticky {
    ip_hash;                         # sticky sessions
    server 127.0.0.1:3001 weight=5; # weighted: gets 5x traffic
    server 127.0.0.1:3002 weight=1;
}

upstream backend_least {
    least_conn;                      # fewest active connections
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
}

server {
    location / {
        proxy_pass http://backend;
        proxy_next_upstream error timeout http_502 http_503;
    }
}
```

## SSL/TLS (HTTPS)

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;

    location / { proxy_pass http://localhost:3000; }
}
```

```bash
# Let's Encrypt with Certbot
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot renew --dry-run
# Auto-renewal: 0 0,12 * * * certbot renew --quiet --post-hook "nginx -s reload"

# Self-signed (dev only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt -subj "/CN=localhost"
```

## Location Block Matching

```nginx
# Priority order (first match wins):
# 1. = exact match              location = /health
# 2. ^~ prefix (stops regex)    location ^~ /static/
# 3. ~ regex (case-sensitive)   location ~ \.php$
# 4. ~* regex (case-insensitive) location ~* \.(jpg|png)$
# 5. prefix (longest match)     location /api/

location = /health { return 200 "OK"; add_header Content-Type text/plain; }
location ^~ /static/ { root /var/www; }
location /api/ { proxy_pass http://localhost:3000/; }  # trailing slash strips /api/

location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Static File Serving

```nginx
# root — appends location to path
location /images/ { root /var/www; }       # serves /var/www/images/photo.jpg

# alias — replaces location with path
location /img/ { alias /var/www/images/; } # serves /var/www/images/photo.jpg

# SPA fallback — all routes resolve to index.html
server {
    root /var/www/app/dist;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
    location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; access_log off; }
    location = /index.html { add_header Cache-Control "no-cache"; }
}
```

## Security Headers

```nginx
# Add to server or http block
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'" always;
server_tokens off;
```

## Rate Limiting

```nginx
# Define zones in http block
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:3000;
    }
    location /auth/login {
        limit_req zone=login burst=5;
        limit_req_status 429;
        proxy_pass http://localhost:3000;
    }
    location /download/ {
        limit_conn addr 5;
        limit_rate 500k;   # throttle bandwidth per connection
    }
}
```

## Proxy Caching

```nginx
# Define cache zone in http block
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m
    max_size=1g inactive=60m use_temp_path=off;

server {
    location /api/ {
        proxy_pass http://backend;
        proxy_cache app_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_key $scheme$request_method$host$request_uri;
        proxy_cache_use_stale error timeout updating http_500 http_502;
        add_header X-Cache-Status $upstream_cache_status;
    }
    location /api/private/ {
        proxy_pass http://backend;
        proxy_cache_bypass $http_authorization;
        proxy_no_cache $http_authorization;
    }
}
```

## Compression

```nginx
# Gzip (in http block)
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_min_length 1000;
gzip_types text/plain text/css application/json application/javascript
    text/xml application/xml image/svg+xml application/wasm;

# Brotli (requires ngx_brotli module)
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript
    text/xml application/xml image/svg+xml;
```

## Redirect and Rewrite Rules

```nginx
# www to non-www (301)
server { server_name www.example.com; return 301 https://example.com$request_uri; }

# Temporary redirect (302)
location /old-page { return 302 /new-page; }

# Rewrite (internal URL transformation)
rewrite ^/blog/(\d+)$ /articles?id=$1 last;
rewrite ^/legacy/(.*)$ /new/$1 permanent;
```

## Access Control

```nginx
# IP whitelisting
location /admin/ {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://localhost:3000;
}

# Basic auth
location /protected/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:3000;
}
```

```bash
sudo apt install apache2-utils && sudo htpasswd -c /etc/nginx/.htpasswd admin
```

## Logging

```nginx
log_format main '$remote_addr - $remote_user [$time_local] '
    '"$request" $status $body_bytes_sent '
    '"$http_referer" "$http_user_agent" rt=$request_time';

# JSON logging (for log aggregation)
log_format json_log escape=json '{'
    '"time":"$time_iso8601",'
    '"remote_addr":"$remote_addr",'
    '"request":"$request",'
    '"status":$status,'
    '"body_bytes_sent":$body_bytes_sent,'
    '"request_time":$request_time,'
    '"upstream_response_time":"$upstream_response_time"'
    '}';

access_log /var/log/nginx/access.log main;
error_log /var/log/nginx/error.log warn;  # levels: debug info notice warn error crit
location = /health { access_log off; return 200 "OK"; }
```

## Performance Tuning

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    multi_accept on;
    use epoll;   # Linux; use kqueue on FreeBSD/macOS
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    client_max_body_size 50m;
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    open_file_cache max=10000 inactive=30s;
    open_file_cache_valid 60s;
}
```

## Docker + Nginx

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

```yaml
# docker-compose.yml — reverse proxy for multiple services
services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on: [app, api]
  app:
    build: ./app
    expose: ["3000"]
  api:
    build: ./api
    expose: ["4000"]
```

## Troubleshooting

```bash
# 413 Request Entity Too Large → client_max_body_size 50m;
# 502 Bad Gateway → check upstream is running, check error log, increase proxy timeouts
# Permission denied → sudo chown -R www-data:www-data /var/www/
# server_names_hash error → server_names_hash_bucket_size 64;
```

## Common Commands

```bash
sudo nginx -t                    # test configuration
sudo nginx -s reload             # reload (no downtime)
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl status nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload
nginx -T                         # dump full resolved config
```
