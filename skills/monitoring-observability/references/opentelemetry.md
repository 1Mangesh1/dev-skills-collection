# OpenTelemetry Instrumentation

## What is OpenTelemetry?

OpenTelemetry (OTel) is a vendor-agnostic observability framework. It provides:
- Instrumentation libraries for automatic data collection
- APIs for custom instrumentation
- Exporters to send data to various backends

## Three Main Components

### 1. Traces
Track request flow through system:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order_id", 12345)
    result = process_payment()
    span.set_attribute("result", "success")
```

### 2. Metrics
Collect numerical data:

```python
from opentelemetry.metrics import get_meter

meter = get_meter(__name__)
order_counter = meter.create_counter("orders_processed")
order_counter.add(1, {"status": "completed"})
```

### 3. Logs
Structured event logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Order processed",
    extra={
        "order_id": 12345,
        "status": "completed",
        "duration_ms": 234
    }
)
```

## Setup Example

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace_provider = TracerProvider()
trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
```

## Integration with Popular Frameworks

- **FastAPI**: `opentelemetry-instrumentation-fastapi`
- **Flask**: `opentelemetry-instrumentation-flask`
- **Django**: `opentelemetry-instrumentation-django`
- **PostgreSQL**: `opentelemetry-instrumentation-psycopg2`
- **Redis**: `opentelemetry-instrumentation-redis`

## Exporting Data

OpenTelemetry supports multiple exporters:
- **Jaeger** - Distributed tracing
- **Prometheus** - Metrics
- **Loki** - Logs
- **Datadog** - All-in-one
- **New Relic** - All-in-one
- **STDOUT** - Local debugging
