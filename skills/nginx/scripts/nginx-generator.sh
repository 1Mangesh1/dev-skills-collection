#!/usr/bin/env bash
# Nginx Configuration Manager
# Generate and validate nginx configs

generate_nginx_config() {
    local domain="$1"
    local port="${2:-8080}"
    
    cat > "nginx-$domain.conf" << EOF
upstream app_backend {
    server localhost:$port;
    keepalive 32;
}

server {
    listen 80;
    server_name $domain;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $domain;

    ssl_certificate /etc/letsencrypt/live/$domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$domain/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Cache static files
    location ~* \.(js|css|images|font|html)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
}
EOF
    
    echo "✓ Generated: nginx-$domain.conf"
}

validate_nginx_config() {
    echo "=== Validating Nginx Configuration ==="
    nginx -t
}

# Usage
generate_nginx_config "example.com" 3000
validate_nginx_config
