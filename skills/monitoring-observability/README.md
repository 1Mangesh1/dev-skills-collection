# Monitoring & Observability Quick Start

Implement comprehensive observability across your system.

## Three Pillars

### 1. Metrics (Numbers)
- Request count, latency, error rate
- CPU, memory, disk usage
- Database query time, pool size
- Tools: Prometheus, Grafana, Datadog

### 2. Logs (Events)
- Structured JSON logs with context
- Application errors and warnings
- Request/response tracking
- Tools: ELK Stack, Splunk, CloudWatch

### 3. Traces (Flows)
- Complete request journey
- Service dependencies
- Bottleneck identification
- Tools: Jaeger, Zipkin, Datadog

## Quick Setup

### Structured Logging
```json
{
  "timestamp": "2025-02-07T10:30:00Z",
  "level": "ERROR",
  "request_id": "req_abc123",
  "service": "api-service",
  "message": "DB connection failed",
  "duration_ms": 500
}
```

### Metrics Collection
```
http_requests_total{method="GET",path="/users"} 1234
http_duration_seconds{method="GET",p99=0.850}
db_pool_size{service="user-service"} 20
```

### Distributed Tracing
- Use W3C trace context headers
- Propagate trace IDs across services
- Correlate logs and metrics

## Key Metrics to Monitor

| Metric | Target | Alert If |
|--------|--------|----------|
| Request latency (p99) | <500ms | >1000ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >90% |
| Memory usage | <80% | >95% |
| DB connections | <80% pool | > 95% pool |

## Dashboard Essentials

1. **System Health** - CPU, memory, disk, network
2. **Application** - Request rate, latency, errors
3. **Database** - Query latency, connections, slow queries
4. **Business** - User signups, revenue, conversion

## Alerting Rules

```
alert: HighErrorRate
if: rate(http_requests_500[5m]) > 0.01
duration: 5m
action: notify #alerts
```

## Tools Quick Reference

| Need | Tools |
|------|-------|
| Metrics | Prometheus, Datadog, New Relic |
| Logs | ELK Stack, Splunk, Loki |
| Traces | Jaeger, Zipkin, Datadog APM |
| All-in-one | Datadog, New Relic, Dynatrace |

## Resources

- [Prometheus Docs](https://prometheus.io/docs/)
- [ELK Stack Tutorial](https://www.elastic.co/guide/en/elastic-stack-get-started/current/index.html)
- [Jaeger Getting Started](https://www.jaegertracing.io/docs/getting-started/)
- [Google SRE Book](https://sre.google/sre-book/)

## See Also

- SKILL.md - Deep dive on observability patterns
- metadata.json - Tool integrations and references
