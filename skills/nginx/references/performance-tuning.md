# Nginx Performance Tuning

## Worker Optimization

```nginx
# /etc/nginx/nginx.conf

worker_processes auto;  # One per CPU core
worker_connections 1024;  # Adjust based on load
keepalive_timeout 65;

# Connection pooling
upstream backend {
    keepalive 32;
}
```

## Buffer Settings

```nginx
client_body_buffer_size 128k;
client_max_body_size 10m;

# Fastcgi buffers (if using PHP)
fastcgi_buffer_size 256k;
fastcgi_buffers 4 256k;
```

## Monitoring

```bash
# Check connections
netstat -an | grep ESTABLISHED | wc -l

# Nginx stats
curl http://localhost/nginx_status

# Monitor performance
# Configure in nginx.conf:
# location /nginx_status {
#     stub_status on;
#     access_log off;
#     allow 127.0.0.1;
#     deny all;
# }
```

## Common Optimizations

1. **Enable gzip compression** - Reduce bandwidth
2. **Browser caching** - Use far-future expires
3. **Load balancing** - Distribute traffic
4. **Connection pooling** - Reuse connections
5. **Rate limiting** - Prevent abuse
