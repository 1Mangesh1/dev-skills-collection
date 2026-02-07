#!/usr/bin/env bash
# Dashboard Generator for Grafana
# Creates basic dashboard configuration

cat << 'EOF'
{
  "dashboard": {
    "title": "Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {"expr": "rate(http_requests_total[5m])"}
        ]
      },
      {
        "title": "Latency (p99)",
        "targets": [
          {"expr": "histogram_quantile(0.99, http_request_duration_seconds)"}
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {"expr": "rate(http_requests_total{status=~'5..'}[5m])"}
        ]
      },
      {
        "title": "CPU Usage",
        "targets": [
          {"expr": "rate(process_cpu_seconds_total[5m])"}
        ]
      },
      {
        "title": "Memory Usage",
        "targets": [
          {"expr": "process_resident_memory_bytes"}
        ]
      }
    ]
  }
}
EOF
