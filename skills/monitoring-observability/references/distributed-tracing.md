# Distributed Tracing Implementation

## OpenTelemetry Overview

Modern standard for collecting traces, metrics, and logs across distributed systems.

### Key Components

1. **Spans** - Individual operation units
2. **Trace Context** - Correlation between services
3. **Baggage** - Metadata passed through spans
4. **Exporters** - Send data to backend (Jaeger, Zipkin, Datadog)

## Implementation Guide

### Java/Spring Boot

```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.GlobalOpenTelemetry;

public class UserService {
    private static final Tracer tracer = 
        GlobalOpenTelemetry.getTracer("user-service");
    
    public User getUser(String userId) {
        Span span = tracer.spanBuilder("getUserById")
            .setAttribute("user.id", userId)
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // Business logic
            return database.findUser(userId);
        } catch (Exception e) {
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### Python

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider

# Configure exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set tracer
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)
        # Business logic
        return find_user(user_id)
```

### Node.js

```javascript
const { NodeTracerProvider } = require('@opentelemetry/node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { SimpleSpanProcessor } = require('@opentelemetry/tracing');

const provider = new NodeTracerProvider({
    plugins: {
        express: {
            enabled: true,
            path: '@opentelemetry/plugin-express',
        }
    }
});

const jaegerExporter = new JaegerExporter({
    host: 'localhost',
    port: 6831,
});

provider.addSpanProcessor(new SimpleSpanProcessor(jaegerExporter));

const tracer = provider.getTracer('user-service');

// Usage
const span = tracer.startSpan('getUser', { attributes: { 'user.id': '123' } });
span.end();
```

## Trace Sampling Strategies

### Sampling Rules

```yaml
# Sample 100% of errors
- condition: error != null
  probability: 1.0

# Sample 10% of successful requests
- condition: error == null
  probability: 0.1

# Sample 100% of slow requests
- condition: duration > 1000ms
  probability: 1.0

# Sample all requests from specific service
- condition: service_name == "payment"
  probability: 1.0
```

### Head-Based Sampling (Recommended)

Decision made at request entry point:
- Consistent traces (don't split decisions)
- Can use request attributes
- Reduces backend cost

### Tail-Based Sampling

Decision made at backend:
- Can sample on complete trace
- Remove boring traces
- Higher backend CPU usage

## Troubleshooting Traces

### Missing Spans

1. Check instrumentation is enabled
2. Verify context propagation
3. Ensure exporter is configured
4. Check network connectivity to backend

### Large Traces

1. Reduce span count (filter, merge)
2. Implement sampling
3. Limit span attributes
4. Use tail-based sampling to filter

### High Cardinality Issues

Avoid attributes with unbounded values:
- ❌ Full SQL queries
- ❌ User IDs in high-cardinality scenarios
- ❌ Request parameters that vary widely

Better approach:
- ✅ Parameterized queries
- ✅ Resource types instead of IDs
- ✅ Ranges vs specific values
