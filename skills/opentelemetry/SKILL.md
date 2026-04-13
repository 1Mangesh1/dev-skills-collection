---
name: opentelemetry
description: OpenTelemetry for distributed tracing, metrics, and logging in production systems. Use when user mentions "opentelemetry", "otel", "distributed tracing", "traces", "spans", "metrics collection", "observability", "jaeger", "prometheus", "grafana", "OTLP", "instrumentation", or setting up application monitoring.
---

# OpenTelemetry

OpenTelemetry (OTel) is a vendor-neutral observability framework for generating, collecting, and exporting telemetry data. It defines three signals:

- **Traces** -- Follow a request across services. Made up of spans (units of work with timing, status, and relationships).
- **Metrics** -- Numeric measurements aggregated over time: counters, histograms, gauges.
- **Logs** -- Structured event records, correlated with traces via trace/span IDs.

All three signals share a common context propagation mechanism so they can be correlated.

## Node.js Setup

### Auto-Instrumentation

```bash
npm install @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-grpc @opentelemetry/exporter-metrics-otlp-grpc
```

Create `tracing.ts` (must load before application code):

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-grpc';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter(), exportIntervalMillis: 15000,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
process.on('SIGTERM', () => sdk.shutdown());
```

Run with: `node --require ./tracing.js app.js`

### Manual Spans (Node.js)

```typescript
import { trace, SpanStatusCode } from '@opentelemetry/api';
const tracer = trace.getTracer('my-service', '1.0.0');

async function processOrder(orderId: string) {
  return tracer.startActiveSpan('processOrder', async (span) => {
    try {
      span.setAttribute('order.id', orderId);
      span.addEvent('validation_started');
      span.addEvent('order_processed', { 'order.total': 42.50 });
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (err) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(err) });
      span.recordException(err as Error);
      throw err;
    } finally {
      span.end();
    }
  });
}
```

## Python Setup

### Auto-Instrumentation

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
opentelemetry-instrument --service_name my-service \
  --exporter_otlp_endpoint http://localhost:4317 python app.py
```

### Programmatic Setup (Python)

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "my-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
```

### Manual Spans (Python)

```python
from opentelemetry import trace
tracer = trace.get_tracer("my-service", "1.0.0")

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.add_event("validation_started")
        span.add_event("order_processed", {"order.total": 42.50})
```

## Traces: Spans, Context, Attributes, Events

A **span** represents a unit of work. Key fields: `name` (operation), `kind` (CLIENT/SERVER/PRODUCER/CONSUMER/INTERNAL), `start_time`/`end_time`, `status` (OK/ERROR/UNSET), `attributes` (key-value pairs), `events` (timestamped entries), `links` (related spans).

**Context propagation** passes trace context across process boundaries via the W3C `traceparent` header: `00-<trace-id>-<span-id>-<trace-flags>`. Auto-instrumentation handles this for HTTP. For manual propagation:

```typescript
import { propagation, context } from '@opentelemetry/api';
// Inject into outgoing headers
const headers: Record<string, string> = {};
propagation.inject(context.active(), headers);
// Extract from incoming headers
const ctx = propagation.extract(context.active(), incomingHeaders);
```

## Metrics

| Instrument | Use Case | Example |
|---|---|---|
| **Counter** | Monotonically increasing count | `requests_total` |
| **UpDownCounter** | Value that increases or decreases | `active_connections` |
| **Histogram** | Distribution of values | `request_duration_ms` |
| **Gauge** | Point-in-time value via callback | `cpu_usage_percent` |

```typescript
import { metrics } from '@opentelemetry/api';
const meter = metrics.getMeter('my-service');

const requestCounter = meter.createCounter('http.requests', { description: 'Total HTTP requests' });
const requestDuration = meter.createHistogram('http.request.duration', { description: 'ms', unit: 'ms' });
const activeConns = meter.createUpDownCounter('http.active_connections');
meter.createObservableGauge('system.cpu.usage').addCallback((r) => {
  r.observe(getCpuUsage(), { 'cpu.core': '0' });
});

requestCounter.add(1, { 'http.method': 'GET', 'http.route': '/users' });
requestDuration.record(145, { 'http.method': 'GET' });
activeConns.add(1);   // on connect
activeConns.add(-1);  // on disconnect
```

## OTLP Exporter Configuration

**gRPC** (port 4317) / **HTTP/protobuf** (port 4318):

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_EXPORTER_OTLP_PROTOCOL=grpc          # or http/protobuf
# Signal-specific overrides:
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://localhost:4318/v1/metrics
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=http://localhost:4318/v1/logs
# Auth headers:
OTEL_EXPORTER_OTLP_HEADERS="x-api-key=abc123,x-team=backend"
```

## Collector Setup

The Collector receives, processes, and exports telemetry in a pipeline:

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }
processors:
  batch: { timeout: 5s, send_batch_size: 1024 }
  memory_limiter: { check_interval: 1s, limit_mib: 512 }
  resource:
    attributes:
      - { key: environment, value: production, action: upsert }
exporters:
  otlp/jaeger: { endpoint: jaeger:4317, tls: { insecure: true } }
  prometheus: { endpoint: 0.0.0.0:8889 }
  debug: { verbosity: detailed }
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

## Common Backends

| Backend | Signal | Notes |
|---|---|---|
| Jaeger | Traces | Open source, native OTLP support |
| Prometheus + Grafana | Metrics | Prometheus scrapes collector; Grafana visualizes |
| Datadog | All | Use Datadog exporter or OTLP endpoint |
| Honeycomb | Traces, Logs | Native OTLP; API key via `OTEL_EXPORTER_OTLP_HEADERS` |
| Grafana Tempo | Traces | Pairs with Grafana for visualization |

## Docker Compose: Collector + Jaeger (Local Dev)

```yaml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus metrics
    depends_on: [jaeger]
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment: [COLLECTOR_OTLP_ENABLED=true]
    ports:
      - "16686:16686" # Jaeger UI
      - "14268:14268" # Jaeger collector HTTP
```

Point your app at `http://localhost:4317` (gRPC) or `http://localhost:4318` (HTTP). Jaeger UI: `http://localhost:16686`.

## Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `OTEL_SERVICE_NAME` | Identifies the service | `order-service` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector address | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Transport protocol | `grpc` or `http/protobuf` |
| `OTEL_EXPORTER_OTLP_HEADERS` | Auth headers | `x-api-key=abc123` |
| `OTEL_TRACES_SAMPLER` | Sampling strategy | `parentbased_traceidratio` |
| `OTEL_TRACES_SAMPLER_ARG` | Sampler argument | `0.1` (10%) |
| `OTEL_RESOURCE_ATTRIBUTES` | Additional resource attrs | `deployment.environment=prod` |
| `OTEL_LOG_LEVEL` | SDK log level | `debug` |
| `OTEL_PROPAGATORS` | Context propagation format | `tracecontext,baggage` |

## Sampling Strategies

| Sampler | Behavior |
|---|---|
| `always_on` | Record every span. Dev only. |
| `always_off` | Record nothing. Disables tracing. |
| `traceidratio` | Sample a percentage based on trace ID. Arg: `0.0`-`1.0`. |
| `parentbased_always_on` | Respect parent decision; sample root spans. |
| `parentbased_traceidratio` | Respect parent; sample unparented at given ratio. |

For production, `parentbased_traceidratio` with `0.01`-`0.1` is a common starting point.

```bash
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.05
```

Programmatic equivalent:

```typescript
import { TraceIdRatioBasedSampler, ParentBasedSampler } from '@opentelemetry/sdk-trace-base';
const sampler = new ParentBasedSampler({ root: new TraceIdRatioBasedSampler(0.05) });
```

## Custom Span Attributes and Events for Debugging

```typescript
span.setAttribute('user.id', userId);
span.setAttribute('order.item_count', items.length);
span.setAttribute('feature_flag.dark_mode', true);
span.addEvent('cache_miss', { 'cache.key': cacheKey });
span.addEvent('retry_attempt', { 'attempt.number': 3, 'error.type': 'timeout' });
span.recordException(error);  // creates event with stack trace
span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
```

Follow semantic conventions for attribute names: `http.request.method`, `db.system`, `rpc.service`.

## Common Instrumentation Patterns

### Trace HTTP Requests

Auto-instrumentation covers most HTTP libraries. Add business context via middleware:

```typescript
app.use((req, res, next) => {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttribute('http.request.header.x_request_id', req.headers['x-request-id']);
    span.setAttribute('user.id', req.user?.id);
  }
  next();
});
```

### Trace Database Queries

Auto-instrumentation handles pg, mysql2, mongoose, etc. Add business context manually:

```typescript
async function getUser(userId: string) {
  return tracer.startActiveSpan('db.getUser', async (span) => {
    span.setAttribute('db.system', 'postgresql');
    span.setAttribute('db.operation', 'SELECT');
    span.setAttribute('user.id', userId);
    const result = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
    span.setAttribute('db.result_count', result.rows.length);
    span.end();
    return result.rows[0];
  });
}
```

### Trace External API Calls

```python
with tracer.start_as_current_span("call_payment_api") as span:
    span.set_attribute("peer.service", "payment-gateway")
    span.set_attribute("payment.amount", amount)
    span.set_attribute("payment.currency", "USD")
    try:
        response = requests.post(payment_url, json=payload)
        span.set_attribute("http.response.status_code", response.status_code)
    except requests.exceptions.Timeout:
        span.set_status(StatusCode.ERROR, "Payment API timeout")
        raise
```

## Baggage for Cross-Service Context

Baggage propagates key-value pairs across service boundaries without adding them to spans. Useful for tenant IDs, feature flags, or routing hints.

```typescript
import { propagation, context } from '@opentelemetry/api';
// Set baggage in service A
const bag = propagation.createBaggage({
  'tenant.id': { value: 'acme-corp' },
  'feature.flag': { value: 'new-checkout' },
});
const ctx = propagation.setBaggage(context.active(), bag);
// Baggage propagates automatically via headers

// Read baggage in service B
const currentBaggage = propagation.getBaggage(context.active());
const tenantId = currentBaggage?.getEntry('tenant.id')?.value;
```

Baggage travels as HTTP headers. Do not put sensitive data in it. Keep entries small -- every downstream service receives all baggage.
