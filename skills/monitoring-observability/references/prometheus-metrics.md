# Prometheus and Metrics Collection

## Prometheus Architecture

### Components

1. **Prometheus Server** - Collects and stores metrics
2. **Exporter** - Exposes application metrics in Prometheus format
3. **AlertManager** - Handles alerting
4. **Grafana** - Visualization dashboard

### Metric Format

```
# HELP metric_name Description of metric
# TYPE metric_name gauge|counter|histogram|summary
metric_name{label1="value1",label2="value2"} 123.45
```

## Writing Custom Exporters

### Python Example

```python
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# Counter - always increases
http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Gauge - current value
memory_usage = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

# Histogram - distribution
request_latency = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0)
)

# Usage
http_requests.labels(method='GET', endpoint='/api/users', status='200').inc()
memory_usage.set(1024 * 1024 * 512)  # 512MB
with request_latency.time():
    # ... code execution time measured
    pass

# Export
print(generate_latest())
```

## PromQL Queries

### Common Queries

```promql
# Request rate per second
rate(http_requests_total[5m])

# Error rate percentage
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100

# 95th percentile latency
histogram_quantile(0.95, request_latency_seconds_bucket)

# Service availability
(1 - (rate(up{job="api"}[5m] == 0) / count(up{job="api"}))) * 100

# Memory usage over time
increase(memory_usage_bytes[1h])
```

## Metric Naming Conventions

```
<namespace>_<subsystem>_<name>_<unit>

Examples:
- http_request_duration_seconds
- database_query_count_total
- cache_hit_ratio
- gc_duration_milliseconds
- worker_queue_depth

Rules:
- Use snake_case
- Include unit suffix
- Use _total for counters
- Avoid redundant labels
```

## Grafana Dashboard Best Practices

### Dashboard Organization

```
Row 1: Service Health
  - Uptime
  - Error rate
  - Performance summary

Row 2: Performance
  - Request latency (p50, p95, p99)
  - Throughput
  - Request size distribution

Row 3: Resource Usage
  - CPU utilization
  - Memory usage
  - Disk I/O

Row 4: Business Metrics
  - User signups
  - Revenue
  - Conversion funnel
```

### Panel Configuration

- Use appropriate chart types (time series, gauge, heatmap)
- Set meaningful alert thresholds
- Use min/max normalization for comparisons
- Include runbook links for alerts
