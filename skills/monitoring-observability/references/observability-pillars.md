# Observability Strategy: Logs, Metrics, Traces

## The Three Pillars of Observability

### 1. Logs
Discrete events and messages from application execution.

**Best Practices:**
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR, FATAL
- Include contextual information: timestamps, request IDs, user IDs
- Use structured logging (JSON format) for easy parsing
- Never log sensitive data (passwords, PII, secrets)
- Set retention policies (usually 30-90 days for compliance)

**Log Example:**
```json
{
  "timestamp": "2024-02-07T10:30:45Z",
  "level": "ERROR",
  "service": "user-service",
  "traceId": "abc123def456",
  "message": "Failed to retrieve user profile",
  "userId": "user789",
  "error": "database connection timeout",
  "duration_ms": 5000
}
```

### 2. Metrics
Numeric measurements aggregated over time intervals.

**Types of Metrics:**
- Counter: Always increasing (requests processed, errors)
- Gauge: Current value (CPU %, active connections)
- Histogram: Distribution of values (response times)
- Summary: Similar to histogram but pre-aggregated

**Key Metrics to Track:**
```
Service Level:
  - Request rate (requests/sec)
  - Error rate (errors/sec)
  - Latency (p50, p95, p99)
  - Saturation (CPU, memory, disk)

Application Level:
  - Database query time
  - Cache hit rate
  - Queue depth
  - Active connections
```

### 3. Traces
Requests flowing through multiple services (distributed tracing).

**Trace Components:**
- Trace ID: Unique identifier for entire request flow
- Span: Single operation within a service
- Span Context: Parent-child relationships
- Baggage: Metadata passed between spans

**Trace Example:**
```
Trace: user-registration-request (trace-id: xyz789)
├── Span: api-gateway (5ms)
├── Span: user-service (50ms)
│   ├── Span: validate-email (10ms)
│   └── Span: database-insert (30ms)
└── Span: notification-service (100ms)
    ├── Span: send-email (80ms)
    └── Span: log-event (15ms)
```

## Instrumentation Strategies

### Code Instrumentation Levels

**Level 1: Basic**
- HTTP request/response logging
- Database query logging
- Exception tracking

**Level 2: Standard**
- Structured logging with context
- Performance metrics collection
- Trace span creation

**Level 3: Comprehensive**
- Custom business metrics
- Detailed span attributes
- Distributed context propagation

### Context Propagation

Track requests across service boundaries:

```
Request → Service A → Service B → Service C
Trace-ID: abc123 (passed in headers)
Parent-Span-ID: updated at each service
```

## Alerting Strategies

### Alert Thresholds

```yaml
Critical Alerts (immediate action):
  - Error rate > 5% for 1 minute
  - Latency p99 > 5 seconds
  - Service down/unreachable
  - Disk usage > 90%

Warning Alerts (investigate):
  - Error rate > 2% for 5 minutes
  - Latency p99 > 2 seconds
  - Disk usage > 80%
  - Memory > 85%

Info Alerts (informational):
  - Deployment completed
  - Database migration started
  - Configuration changed
```

### Alert Fatigue Prevention

- Avoid low-importance alerts on dashboards
- Use escalation: info → warning → critical
- Implement alert deduplication
- Set minimum alert duration (5-10 minutes baseline)
- Use composite alerts (multiple conditions)
