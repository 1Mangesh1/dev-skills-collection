---
name: monitoring-observability
description: Production monitoring, observability, and incident response practices. Use when the user asks about structured logging, distributed tracing, metrics collection, Prometheus, Grafana dashboards, log aggregation, ELK or Loki, alerting strategy, SLIs and SLOs, error budgets, health checks, RED or USE method, uptime monitoring, synthetic checks, incident response, postmortems, runbooks, or designing an observability stack.
---

# Monitoring and Observability

Concepts, tooling, and operational practices for monitoring production systems
and responding to incidents effectively.

---

## 1. The Three Pillars of Observability

### Logs
- Discrete events emitted by applications (errors, state changes, audit trails).
- High cardinality: every event can carry unique context.
- Best for debugging specific incidents after the fact.

### Metrics
- Numeric measurements aggregated over time (counters, gauges, histograms).
- Low cardinality by design: labels should have bounded value sets.
- Best for detecting trends, setting thresholds, and alerting.

### Traces
- Records of a single request as it traverses multiple services.
- Each trace contains spans representing individual operations.
- Best for identifying latency bottlenecks and dependency failures.

### How They Connect
A metric alert fires (error rate spike). You query logs filtered by service and
time window. You pull a trace ID from the logs to see the full request path.
Together they move you from "something is wrong" to "here is why."

---

## 2. Structured Logging

Unstructured text logs are difficult to search and aggregate. Structured logs
(typically JSON) make every field machine-parseable.

```json
{
  "timestamp": "2025-09-14T08:22:11.403Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc123def456",
  "correlation_id": "order-98765",
  "message": "Charge failed: card declined",
  "duration_ms": 342
}
```

**Log levels**: DEBUG (dev only), INFO (normal operations), WARN (recoverable
issues), ERROR (request-level failures), FATAL (process must exit).

**Correlation IDs**: Generate a unique ID at the edge (API gateway). Propagate
it via `X-Request-ID` header to every downstream call. Include it in every log
line to reconstruct the full request path.

---

## 3. Metrics Types

- **Counter**: Monotonically increasing. Use `rate()` to query. Examples: total
  requests, total errors.
- **Gauge**: Goes up and down. Examples: memory usage, active connections, queue
  depth.
- **Histogram**: Counts observations in configurable buckets. Produces `_bucket`,
  `_sum`, `_count` series. Use for latency distributions via
  `histogram_quantile()`.
- **Summary**: Calculates quantiles client-side. Not aggregatable across
  instances. Prefer histograms in most cases.

---

## 4. Prometheus Basics

Prometheus is a pull-based metrics system that scrapes HTTP endpoints exposing
metrics in its text format.

### Scrape Configuration

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "api-server"
    static_configs:
      - targets: ["api-server:8080"]
    metrics_path: /metrics
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Key PromQL Queries

```promql
rate(http_requests_total[5m])                                    # request rate
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # p99
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))                           # error ratio
```

### Alerting Rules

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5% for 5 minutes"
          runbook_url: "https://wiki.internal/runbooks/high-error-rate"
```

---

## 5. Grafana Dashboards

**Data sources**: Prometheus, Loki, Elasticsearch, InfluxDB, CloudWatch, others.

**Panel types**: Time series (metrics over time), Stat (single value), Table
(top-N lists), Heatmap (latency distribution), Logs (inline log viewer).

**Template variables**: Define `$namespace`, `$service`, `$instance` at the
dashboard level. Use in queries to make one dashboard serve many teams.

**Alerts**: Grafana 9+ has a unified alerting engine. Define rules on panels,
route notifications to Slack, PagerDuty, or OpsGenie via notification policies
matched by label.

---

## 6. Log Aggregation

### ELK Stack (Elasticsearch, Logstash, Kibana)
- Elasticsearch stores and full-text indexes logs.
- Logstash ingests, transforms, and ships logs.
- Kibana provides query, visualization, and dashboards.
- Resource-heavy. Suited for large organizations with platform teams.

### Loki (Lightweight Alternative)
- Indexes logs only by labels, not full text. Much cheaper to operate.
- LogQL query language is similar to PromQL.
- Pairs naturally with Grafana. Use Promtail or Grafana Agent to ship logs.

**When to choose**: Need full-text search across all fields? ELK. Need
cost-effective storage with label-based queries? Loki. Already running
Prometheus and Grafana? Loki reduces operational overhead.

---

## 7. Alerting Strategy

### Alert Fatigue
Every alert must be actionable. If no one needs to act, remove it. Prefer
alerting on symptoms (users affected) over causes (CPU is high).

### Severity Levels

| Severity | Meaning | Response |
|----------|---------|----------|
| P1 / Critical | Service down or data loss | Page immediately |
| P2 / High | Degraded, partial outage | Page during business hours |
| P3 / Medium | Non-urgent, workaround exists | Ticket, fix within days |
| P4 / Low | Cosmetic or minor | Backlog |

### Runbooks
Every alert should link to a runbook containing: what the alert means, how to
verify, steps to mitigate, escalation contacts, and relevant dashboard links.
Keep runbooks in version control alongside alerting rules.

### Notification Routing (PagerDuty, OpsGenie)
Route P1/P2 to on-call paging tools. Route P3/P4 to Slack or ticketing systems.
Configure escalation policies so the secondary is paged if the primary does not
acknowledge within N minutes.

---

## 8. SLIs, SLOs, and Error Budgets

**SLI (Service Level Indicator)**: A quantitative measure of a service aspect.
Examples: availability (% successful requests), latency (% requests < threshold).

**SLO (Service Level Objective)**: A target for an SLI over a time window.
Example: 99.9% of requests succeed over a 30-day rolling window.

**Error budget**: The allowed unreliability: `1 - SLO`. A 99.9% SLO gives 0.1%
budget (roughly 43 minutes of downtime per 30 days). When the budget is nearly
exhausted, freeze releases and focus on reliability.

**Tips**: Start with one or two SLOs per service. Measure from the client
perspective (load balancer logs, synthetic probes). Review in weekly reliability
meetings.

---

## 9. Health Checks and Readiness Probes

- **Liveness**: "Is the process alive?" Kubernetes restarts the pod on failure.
  Keep it simple: return 200 if the event loop is running.
- **Readiness**: "Can it accept traffic?" Kubernetes removes the pod from the
  load balancer on failure. Check dependencies (DB pool, cache).
- **Startup**: Prevents liveness checks from killing slow-starting containers.

```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  periodSeconds: 5
```

---

## 10. The RED Method (Application Metrics)

For request-driven services, dashboard these three signals:

| Signal | Measure | Example Metric |
|--------|---------|----------------|
| Rate | Requests per second | `rate(http_requests_total[5m])` |
| Errors | Failed requests per second | `rate(http_requests_total{status=~"5.."}[5m])` |
| Duration | Latency (p50, p95, p99) | `histogram_quantile(0.95, ...)` |

Alert when error rate or latency exceeds SLO thresholds.

---

## 11. The USE Method (Infrastructure Metrics)

For resources (CPU, memory, disk, network):

| Signal | Definition | Example |
|--------|-----------|---------|
| Utilization | % of resource busy | CPU at 85% |
| Saturation | Queued work beyond capacity | Run queue > core count |
| Errors | Error events | Disk I/O errors, packet drops |

High utilization alone is not a problem. High saturation means the resource is
a bottleneck. Infrastructure bottlenecks often manifest as increased request
latency (linking USE back to RED).

---

## 12. Uptime Monitoring

**Synthetic checks**: Automated scripts simulating user actions from multiple
regions. Tools: Grafana Synthetic Monitoring, Checkly, Pingdom.

**Real User Monitoring (RUM)**: Collects performance data from actual browsers.
Measures page load, time to interactive, core web vitals. Captures real network
conditions and device diversity that synthetics cannot.

**Status pages**: Publish service status externally (Statuspage, Instatus).
Automate updates from alert state changes when possible.

---

## 13. Incident Response Workflow

1. **Detect** -- Alerts fire, users report issues, synthetic checks fail.
2. **Triage** -- Assess scope and affected users. Assign severity. Open an
   incident channel.
3. **Mitigate** -- Restore service first; root cause comes later. Rollback,
   scale up, toggle feature flags, failover. Communicate at regular intervals.
4. **Resolve** -- Confirm metrics returned to normal. Close incident channel and
   update status page.
5. **Postmortem** -- Write a blameless postmortem within 48 hours. Include
   timeline, root cause, impact, what went well, and action items. Track items
   to completion.

---

## 14. Dashboards to Build First

1. **Service overview**: RED metrics per service (rate, errors, duration).
2. **Infrastructure**: CPU, memory, disk, network per node/pod (USE).
3. **SLO tracker**: Current SLI values, error budget remaining, burn rate.
4. **Deployment overlay**: Deploy events on error rate and latency graphs.
5. **Database**: Query rate, slow queries, connection pool, replication lag.
6. **Queue/worker**: Enqueue rate, dequeue rate, queue depth, processing time.

---

## 15. Anti-Patterns

- **Alert on everything**: Creates noise and on-call burnout. Alert on
  user-facing symptoms, not every internal metric.
- **No runbooks**: Engineers paged at 3 AM with no response guidance. Link every
  alert to a runbook and update it after incidents.
- **Metrics without context**: Dashboards full of unexplained numbers. Add panel
  descriptions, deployment annotations, and threshold lines.
- **Logging sensitive data**: PII or secrets in logs create compliance risk.
  Sanitize fields before logging.
- **Ignoring cardinality**: Unbounded label values (user IDs, request IDs) in
  metrics explode storage and slow queries. Use high-cardinality data in logs
  and traces instead.
- **No cross-pillar correlation**: Metrics, logs, and traces in separate silos.
  Include trace IDs in logs, add exemplars to metrics, use tooling that
  supports cross-referencing (Grafana with Prometheus, Loki, and Tempo).

---

## References

- Google SRE Book (monitoring and alerting chapters)
- Observability Engineering by Majors, Fong-Jones, Miranda (O'Reilly)
- Prometheus docs: https://prometheus.io/docs/
- Grafana docs: https://grafana.com/docs/
- OpenTelemetry: https://opentelemetry.io/
- The RED Method (Tom Wilkie)
- The USE Method (Brendan Gregg)
