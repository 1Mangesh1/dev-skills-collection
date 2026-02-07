#!/usr/bin/env bash
# Docker Compose Health Check
# Monitors container health

check_service_health() {
    local service="$1"
    
    echo "=== Health Check for $service ==="
    
    # Check if container running
    if docker-compose ps "$service" | grep -q "Up"; then
        echo "✓ $service is running"
        
        # Check health status
        health=$(docker-compose ps "$service" | grep -oP "healthy|unhealthy|starting")
        echo "  Health: $health"
        
        # Show logs
        echo "  Recent logs:"
        docker-compose logs "$service" --tail=5
    else
        echo "✗ $service is not running"
    fi
}

check_service_health "${1:-web}"
