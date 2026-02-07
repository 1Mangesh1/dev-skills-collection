#!/usr/bin/env bash
# Image Security Scanner
# Scans Docker images for vulnerabilities

scan_image() {
    local image="$1"
    
    echo "=== Scanning $image ==="
    
    # Check base image
    echo ""
    echo "Base Image Analysis:"
    docker image inspect "$image" | grep -A5 '"RootFS"'
    
    # Scan with trivy if available
    if command -v trivy &> /dev/null; then
        echo ""
        echo "Vulnerability Scan:"
        trivy image --table --severity HIGH,CRITICAL "$image"
    else
        echo "Install trivy for vulnerability scanning"
    fi
    
    # Size analysis
    echo ""
    echo "Size Analysis:"
    docker images "$image" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
}

# Usage: scan_image myapp:latest
scan_image "${1:-myapp:latest}"
