#!/usr/bin/env python3
"""Metrics Collection Configuration Generator"""

import json

def generate_prometheus_config():
    """Generate Prometheus scrape configuration"""
    return {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s"
        },
        "scrape_configs": [
            {
                "job_name": "prometheus",
                "static_configs": [{"targets": ["localhost:9090"]}]
            },
            {
                "job_name": "application",
                "static_configs": [{"targets": ["localhost:8080"]}],
                "metrics_path": "/metrics"
            },
            {
                "job_name": "postgres",
                "static_configs": [{"targets": ["localhost:9187"]}]
            }
        ],
        "alerting": {
            "alertmanagers": [
                {"static_configs": [{"targets": ["localhost:9093"]}]}
            ]
        }
    }

def generate_structured_logging():
    """Generate structured logging example"""
    return {
        "timestamp": "2025-02-07T10:30:00.123Z",
        "level": "ERROR",
        "service": "user-service",
        "request_id": "req_abc123def456",
        "correlation_id": "corr_xyz789",
        "user_id": "user_12345",
        "action": "user_registration",
        "status": "failed",
        "error_code": "EMAIL_ALREADY_EXISTS",
        "error_message": "Email already registered",
        "duration_ms": 145,
        "tags": {"environment": "production", "region": "us-east-1"}
    }

if __name__ == "__main__":
    print("=== Prometheus Configuration ===")
    print(json.dumps(generate_prometheus_config(), indent=2))
    print("\n=== Structured Log Entry ===")
    print(json.dumps(generate_structured_logging(), indent=2))
