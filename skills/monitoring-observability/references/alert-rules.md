# Alert Rules and Thresholds

## Alert Composition

Every alert should have:
1. **Condition** - What triggers it
2. **Threshold** - When to fire
3. **Duration** - How long before alerting
4. **Severity** - Critical, warning, info
5. **Action** - Who gets notified

## Common Alert Patterns

### High Error Rate

```yaml
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
labels:
  severity: critical
annotations:
  description: "Error rate is {{ $value | humanizePercentage }}"
```

**Meaning:** Alert if 5% of requests error for 5+ minutes

### High Latency

```yaml
alert: HighLatency
expr: histogram_quantile(0.99, http_request_duration_seconds) > 1
for: 10m
labels:
  severity: warning
annotations:
  description: "P99 latency is {{ $value }}s"
```

**Meaning:** Alert if 99th percentile latency exceeds 1 second for 10+ minutes

### Database Connection Pool Exhaustion

```yaml
alert: DBPoolExhaustion
expr: mysql_global_status_threads_connected / mysql_global_variables_max_connections > 0.8
for: 5m
labels:
  severity: critical
annotations:
  description: "DB connections at {{ $value | humanizePercentage }}"
```

### Memory Usage

```yaml
alert: HighMemoryUsage
expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
for: 10m
labels:
  severity: warning
```

## Setting Good Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | 1% | 5% |
| Latency (p99) | 500ms | 2000ms |
| CPU | 70% | 90% |
| Memory | 80% | 95% |
| DB Connection Pool | 60% | 80% |
| Disk Space | 70% | 90% |

## Alert Fatigue Prevention

1. **Avoid noise** - Only alert on actionable issues
2. **Smart thresholds** - Not too tight, not too loose
3. **Grouping** - Group related alerts
4. **Escalation** - Start with warning, then critical
5. **Resolution** - Alert clears automatically when resolved
