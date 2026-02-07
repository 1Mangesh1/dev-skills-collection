#!/usr/bin/env bash
# SSL/TLS Configuration Tool
# Manage SSL certificates and setup

setup_letsencrypt() {
    local domain="$1"
    
    echo "=== Setting up Let's Encrypt SSL ==="
    
    # Install certbot if needed
    if ! command -v certbot &> /dev/null; then
        sudo apt install certbot python3-certbot-nginx
    fi
    
    # Get certificate
    sudo certbot certonly --standalone -d "$domain"
    
    # Update nginx config to use certificate
    echo "Certificate stored at: /etc/letsencrypt/live/$domain/"
}

check_ssl_expiry() {
    local domain="$1"
    
    echo "=== Checking SSL Certificate Expiry ==="
    echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | \
        openssl x509 -noout -dates
}

# Usage
check_ssl_expiry "example.com"
