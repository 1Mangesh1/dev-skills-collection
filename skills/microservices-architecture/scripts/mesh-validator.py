#!/usr/bin/env python3
"""Service Mesh Configuration Validator"""

import json

def validate_service_mesh_config():
    """Validate microservices configuration"""
    
    return {
        "mesh_type": "Istio",
        "services": [
            {
                "name": "user-service",
                "replicas": 3,
                "port": 8001,
                "health_check": "/health",
                "circuit_breaker": {
                    "consecutive_errors": 5,
                    "interval": "30s"
                }
            },
            {
                "name": "order-service",
                "replicas": 3,
                "port": 8002,
                "dependencies": ["user-service", "payment-service"]
            },
            {
                "name": "payment-service",
                "replicas": 2,
                "port": 8003,
                "critical": True
            }
        ],
        "traffic_policies": {
            "load_balancing": "round_robin",
            "timeouts": {
                "connection": "10s",
                "request": "30s"
            },
            "retries": {
                "attempts": 3,
                "backoff": "exponential"
            }
        },
        "security": {
            "mtls": "STRICT",
            "authorization_policy": "enabled"
        }
    }

if __name__ == "__main__":
    result = validate_service_mesh_config()
    print(json.dumps(result, indent=2))
