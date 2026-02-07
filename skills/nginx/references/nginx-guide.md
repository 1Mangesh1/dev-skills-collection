# Nginx Configuration Guide

## Basic Server Block

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Reverse Proxy

```nginx
upstream backend {
    server backend1.example.com:8080;
    server backend2.example.com:8080;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Load Balancing

```nginx
upstream backend {
    least_conn;  # or: ip_hash, random, etc
    
    server backend1:8080 weight=5;
    server backend2:8080 weight=3;
    server backend3:8080 backup;
}
```

## SSL/TLS Setup

```nginx
server {
    listen 443 ssl http2;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

## Caching

```nginx
location ~* \.(js|css|png|jpg|gif|ico)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Skip cache for dynamic content
location ~ \.php$ {
    add_header Cache-Control "no-store";
}
```

## Security Headers

```nginx
add_header Strict-Transport-Security "max-age=31536000" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Compression

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

## Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=50;
}
```
