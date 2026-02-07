#!/usr/bin/env bash
# Kubernetes Deployment Helper
# Common kubectl operations

get_pod_info() {
    local namespace="${1:-default}"
    
    echo "=== Pods in $namespace ==="
    kubectl get pods -n "$namespace" \
        --no-headers | awk '{print $1, $2, $3, $6}' | column -t
}

check_pod_logs() {
    local pod_name="$1"
    local namespace="${2:-default}"
    
    echo "=== Logs for $pod_name ==="
    kubectl logs "$pod_name" -n "$namespace" --tail=50 -f
}

deploy_application() {
    local manifest_file="$1"
    
    echo "=== Applying Manifest ==="
    kubectl apply -f "$manifest_file"
    
    # Wait for rollout
    kubectl rollout status deployment/app -n default
}

scale_deployment() {
    local deployment="$1"
    local replicas="$2"
    
    echo "Scaling $deployment to $replicas replicas"
    kubectl scale deployment "$deployment" --replicas="$replicas"
}

# Usage
get_pod_info "default"
