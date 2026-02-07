#!/usr/bin/env bash
# Docker Cleanup Script
# Removes unused images, containers, volumes

cleanup_docker() {
    echo "=== Docker Cleanup ==="
    
    # Remove stopped containers
    echo "Removing stopped containers..."
    docker container prune -f
    
    # Remove dangling images
    echo "Removing dangling images..."
    docker image prune -f
    
    # Remove unused volumes
    echo "Removing unused volumes..."
    docker volume prune -f
    
    # Show disk space saved
    echo ""
    echo "Showing disk usage:"
    docker system df
}

cleanup_docker
