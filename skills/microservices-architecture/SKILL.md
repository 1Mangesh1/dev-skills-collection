---
name: microservices-architecture
description: Microservices architecture patterns, trade-offs, and implementation guidance. Use when user asks about service decomposition, bounded contexts, API gateways, distributed transactions, saga pattern, circuit breaker, service mesh, event-driven architecture, CQRS, event sourcing, message brokers, service discovery, distributed tracing, contract testing, strangler fig migration, polyglot persistence, eventual consistency, inter-service communication, or any microservices design, operational concerns, and architectural decisions.
---

# Microservices Architecture

Patterns, trade-offs, and practical guidance for designing, building, and operating microservices systems.

---

## When to Use Microservices (and When Not To)

### Microservices are a good fit when:
- Multiple teams need to deploy independently on different release cadences
- Different parts of the system have fundamentally different scaling requirements
- The domain is well understood and service boundaries are clear
- The organization can invest in infrastructure automation, monitoring, and CI/CD

### A monolith is better when:
- The team is small (fewer than 8-10 engineers)
- The domain is not yet well understood and boundaries are likely to shift
- Speed of initial development matters more than independent deployability
- The organization lacks mature DevOps practices
- The application has low complexity and uniform scaling needs

Start with a well-structured monolith. Extract services only when you have a clear, justified reason. Premature decomposition creates distributed monoliths.

---

## Service Boundaries

### Domain-Driven Design (DDD)

Service boundaries should align with business domains, not technical layers.

**Bounded Contexts** define the boundaries within which a particular domain model applies. Each microservice should map to one bounded context.

```
Order Context          Inventory Context        Shipping Context
+-----------------+    +-----------------+      +-----------------+
| Order           |    | Product         |      | Shipment        |
| OrderLine       |    | StockLevel      |      | Carrier         |
| Payment         |    | Warehouse       |      | TrackingEvent   |
+-----------------+    +-----------------+      +-----------------+
```

### Guidelines for drawing boundaries:
- **Business capability**: Each service represents a business function (ordering, billing, shipping)
- **Data ownership**: A service owns its data and exposes it only through its API
- **Autonomy**: A service can be developed, deployed, and scaled independently
- **Cohesion**: Related behavior lives together; unrelated behavior lives apart
- **Loose coupling**: Changes in one service should rarely require changes in another

### Context Mapping

Define explicit relationships between bounded contexts:
- **Shared Kernel**: Two contexts share a small common model (use sparingly)
- **Customer-Supplier**: Upstream context provides what downstream needs
- **Anticorruption Layer**: Translates between contexts to prevent model leakage
- **Conformist**: Downstream adopts upstream model as-is

---

## Communication Patterns

### Synchronous Communication

**REST (HTTP/JSON)**
- Widely understood, good tooling, human-readable
- Suitable for CRUD operations and simple request-response flows
- Versioning via URL path (`/v1/orders`) or headers
- Use when: clients need immediate responses, operations are simple

**gRPC (Protocol Buffers)**
- Binary protocol, significantly faster than JSON over HTTP
- Strongly typed contracts via `.proto` files
- Supports streaming (unary, server-streaming, client-streaming, bidirectional)
- Use when: low-latency internal service-to-service communication, high throughput

```protobuf
service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
  rpc StreamOrderUpdates (OrderQuery) returns (stream OrderUpdate);
}
```

### Asynchronous Communication

**Message Queues (Point-to-Point)**
- One producer sends a message; one consumer processes it
- Work distribution, task offloading, load leveling
- Examples: RabbitMQ queues, SQS

**Events (Publish-Subscribe)**
- One producer publishes an event; multiple consumers react independently
- Decouples producers from consumers
- Examples: Kafka topics, SNS, RabbitMQ exchanges

Choose async when:
- The caller does not need an immediate result
- You want to decouple services temporally
- You need to buffer load spikes
- Multiple consumers need to react to the same event

---

## API Gateway Pattern

```
Mobile App  --\
Web App     ----> API Gateway ----> Order Service
Partner API --/        |   \------> Inventory Service
                       |   \------> User Service
                       v
                Authentication
                Rate Limiting
                Request Routing
                Response Aggregation
                Protocol Translation
                Logging / Metrics
```

### Responsibilities:
- **Routing**: Direct requests to the correct backend service
- **Authentication/Authorization**: Validate tokens, enforce policies at the edge
- **Rate limiting**: Protect backend services from traffic spikes
- **Response aggregation**: Combine data from multiple services into a single response
- **Protocol translation**: Accept REST from clients, forward as gRPC internally
- **SSL termination**: Handle TLS at the gateway

### Implementations:
- Kong, NGINX, AWS API Gateway, Envoy, Traefik

### Backend-for-Frontend (BFF):
A variant where each client type (mobile, web, partner) gets its own gateway tailored to its needs, avoiding a one-size-fits-all gateway.

---

## Service Discovery

Services need to locate each other at runtime when instances scale dynamically.

### Client-Side Discovery
The client queries a service registry and selects an instance.
```
Client -> Service Registry -> [Instance A, Instance B, Instance C]
Client -> Instance B (selected via load balancing)
```

### Server-Side Discovery
The client sends requests to a load balancer, which queries the registry.
```
Client -> Load Balancer -> Service Registry -> Instance A
```

### Implementations:
- **Consul**: Service registry with health checking, key-value store, DNS interface
- **Eureka**: Netflix OSS, common in Spring Cloud ecosystems
- **Kubernetes DNS**: Built-in service discovery via DNS names (e.g., `order-service.default.svc.cluster.local`)
- **AWS Cloud Map**: Managed service discovery for AWS workloads

In Kubernetes environments, built-in DNS-based discovery often eliminates the need for a separate registry.

---

## Event-Driven Architecture

### Event Sourcing

Instead of storing current state, store the sequence of events that led to the current state.

```
Events (append-only log):
1. OrderCreated { orderId: 42, items: [...], total: 150.00 }
2. PaymentReceived { orderId: 42, amount: 150.00 }
3. OrderShipped { orderId: 42, trackingId: "XYZ123" }

Current state is derived by replaying events.
```

**Benefits**: Full audit trail, temporal queries ("what was the state at time T"), ability to rebuild read models, supports event replay for debugging.

**Costs**: Increased storage, more complex queries, eventual consistency, schema evolution for events requires care.

### CQRS (Command Query Responsibility Segregation)

Separate the write model (commands) from the read model (queries).

```
Commands (writes)            Queries (reads)
     |                            |
     v                            v
Write Model  --events-->   Read Model (projection)
(normalized)               (denormalized, optimized for queries)
```

- The write side validates and persists domain events
- The read side subscribes to events and maintains query-optimized views
- Often paired with event sourcing, but they are independent patterns
- Use when read and write workloads have very different performance or modeling needs

---

## Message Brokers

### When to use which:

| Broker | Best for | Key characteristics |
|--------|----------|-------------------|
| **RabbitMQ** | Task queues, work distribution, routing | AMQP protocol, flexible routing (direct, topic, fanout), message acknowledgment, per-message delivery guarantees, lower throughput than Kafka |
| **Apache Kafka** | Event streaming, event sourcing, high-throughput pipelines | Append-only log, consumer groups, message retention by time/size, replay capability, horizontal scaling via partitions, high throughput |
| **Amazon SQS** | Simple cloud-native queuing | Fully managed, no infrastructure to operate, standard and FIFO queues, dead-letter queues, integrates with AWS Lambda |

### Decision guidance:
- Need message replay or event sourcing? **Kafka**
- Need complex routing logic (topic exchanges, headers-based routing)? **RabbitMQ**
- Want zero infrastructure management on AWS? **SQS**
- Need strict ordering with exactly-once delivery? **SQS FIFO** or **Kafka** (with idempotent producers)
- Need pub/sub with persistent consumer groups? **Kafka**
- Need lightweight, traditional work queues? **RabbitMQ** or **SQS**

---

## Data Management

### Database per Service

Each service owns its database. No other service accesses it directly.

```
Order Service  --> Orders DB (PostgreSQL)
Product Service --> Products DB (MongoDB)
Search Service --> Search Index (Elasticsearch)
```

**Benefits**: Independent schema evolution, technology choice per service, no shared-database coupling.

**Challenge**: Cross-service queries and distributed transactions.

### Saga Pattern

Manage distributed transactions as a sequence of local transactions with compensating actions.

**Choreography (event-based):**
```
Order Service: CreateOrder --> emit OrderCreated
Payment Service: hears OrderCreated --> charge payment --> emit PaymentCompleted
Inventory Service: hears PaymentCompleted --> reserve stock --> emit StockReserved
Order Service: hears StockReserved --> confirm order

On failure at any step: each service listens for failure events and runs compensation
(e.g., PaymentFailed --> refund payment, release stock)
```

**Orchestration (coordinator-based):**
```
Saga Orchestrator:
  1. Tell Order Service: create order
  2. Tell Payment Service: charge payment
  3. Tell Inventory Service: reserve stock
  On failure: send compensating commands in reverse order
```

- Choreography: simpler for few steps, harder to trace as complexity grows
- Orchestration: explicit flow control, easier to reason about, single point to monitor

### Eventual Consistency

In a microservices system, strong consistency across services is impractical. Accept that:
- Data will be temporarily inconsistent between services
- Design UIs to handle in-progress states gracefully
- Use idempotent operations to safely retry
- Implement read-your-writes consistency where user experience demands it

---

## Circuit Breaker Pattern

Prevent cascading failures when a downstream service is unhealthy.

### States:
```
CLOSED (normal) --failures exceed threshold--> OPEN (failing fast)
OPEN --timeout expires--> HALF-OPEN (testing)
HALF-OPEN --success--> CLOSED
HALF-OPEN --failure--> OPEN
```

### Implementation concerns:

**Retry with exponential backoff:**
```python
import time

def call_with_retry(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            time.sleep(delay)
```

**Timeout**: Set timeouts on every external call. A missing timeout is a latency leak. Calculate cascading timeouts so upstream timeouts are longer than downstream.

**Fallback strategies**:
- Return cached data (stale but available)
- Return a default/degraded response
- Queue the request for later processing
- Return an error with clear guidance

**Libraries**: Resilience4j (Java), Polly (.NET), Hystrix (legacy), custom implementations.

---

## Distributed Tracing and Observability

### Three Pillars of Observability

**Logs**: Structured, machine-parsable records of discrete events.
- Use structured logging (JSON) with consistent fields
- Include a correlation/trace ID in every log entry
- Centralize with ELK (Elasticsearch, Logstash, Kibana), Loki, or Splunk

**Metrics**: Numeric measurements aggregated over time.
- RED method: Rate, Errors, Duration (for request-driven services)
- USE method: Utilization, Saturation, Errors (for resources)
- Tools: Prometheus + Grafana, Datadog, CloudWatch

**Traces**: End-to-end request paths across services.
- Propagate trace context (W3C Trace Context or B3 headers) across service boundaries
- Each service creates spans representing its work
- Tools: Jaeger, Zipkin, AWS X-Ray, OpenTelemetry (vendor-neutral standard)

### OpenTelemetry

The emerging standard for instrumentation. Provides APIs and SDKs for traces, metrics, and logs with exporters to multiple backends. Prefer OpenTelemetry over vendor-specific instrumentation.

### Health checks

Every service should expose:
- **Liveness**: "Is the process running?" (restart if not)
- **Readiness**: "Can the service handle traffic?" (remove from load balancer if not)

---

## Service Mesh

A dedicated infrastructure layer for managing service-to-service communication.

### What it solves:
- Mutual TLS between services without application code changes
- Traffic management (retries, timeouts, circuit breaking) at the infrastructure level
- Observability (metrics, traces) injected automatically via sidecar proxies
- Traffic splitting for canary deployments
- Access control policies between services

### How it works:
```
Service A -> Sidecar Proxy A ---network---> Sidecar Proxy B -> Service B
                    \                              /
                     -----> Control Plane <--------
                            (configuration, certificates, policies)
```

### Implementations:
- **Istio**: Feature-rich, Envoy-based, higher operational complexity
- **Linkerd**: Lightweight, simpler to operate, Rust-based proxy
- **AWS App Mesh**: Managed mesh for AWS workloads

### When to adopt:
- You have many services (dozens+) and need uniform observability and security
- You want to enforce mTLS without changing application code
- You need advanced traffic management (fault injection, mirroring)
- Do not adopt for fewer than 5-10 services; the overhead is not justified

---

## Deployment Patterns

### Blue-Green Deployment
- Maintain two identical production environments (blue and green)
- Deploy new version to the idle environment
- Switch traffic from blue to green (or vice versa) once verified
- Instant rollback by switching traffic back
- Cost: maintaining two full environments

### Canary Deployment
- Route a small percentage of traffic (e.g., 5%) to the new version
- Monitor error rates, latency, and business metrics
- Gradually increase traffic if metrics are healthy
- Roll back by routing all traffic to the old version
- Lower risk than blue-green, but slower rollout

### Rolling Deployment
- Replace instances of the old version one at a time (or in batches)
- At any point, both old and new versions are running simultaneously
- No additional infrastructure cost
- Requires backward-compatible changes (APIs, database schemas)
- Slower rollback compared to blue-green

### Choosing a strategy:
- Need instant rollback? Blue-green
- Want to minimize risk with gradual exposure? Canary
- Want simplicity and low infrastructure cost? Rolling

---

## Container Orchestration Basics

Microservices are typically deployed as containers managed by an orchestrator.

### Kubernetes core concepts:
- **Pod**: Smallest deployable unit; one or more containers sharing network and storage
- **Deployment**: Declares desired state (image version, replica count); handles rolling updates
- **Service**: Stable network endpoint that routes to healthy pods
- **ConfigMap / Secret**: Externalized configuration and sensitive data
- **Horizontal Pod Autoscaler (HPA)**: Scales pod count based on CPU, memory, or custom metrics
- **Namespace**: Logical isolation within a cluster

### Alternatives:
- **AWS ECS/Fargate**: Managed container orchestration without Kubernetes complexity
- **Docker Swarm**: Simpler orchestration, suitable for smaller deployments
- **Nomad**: HashiCorp orchestrator supporting containers and non-container workloads

---

## Testing Microservices

### Testing pyramid for microservices:
```
           /  E2E Tests  \        (few, slow, expensive)
          / Integration    \
         / Contract Tests    \
        / Component Tests      \
       /   Unit Tests            \   (many, fast, cheap)
```

### Contract Testing
Verify that service interfaces remain compatible without running full integration tests.

- **Consumer-driven contracts**: The consumer defines expectations; the provider verifies it meets them
- Tools: Pact, Spring Cloud Contract
- Catches breaking API changes early in CI

### Component Testing
Test a single service in isolation with its dependencies stubbed or mocked.

### Integration Testing
Test interactions between real services in a shared test environment.
- Expensive to maintain; use sparingly
- Focus on critical paths and failure modes

### End-to-End Testing
Test complete user journeys across the full system.
- Slowest and most brittle; keep the count low
- Supplement with synthetic monitoring in production

### Testing in production:
- Feature flags to control rollout
- Canary deployments with automated metric checks
- Synthetic transactions (health-check requests that exercise real paths)
- Chaos engineering (deliberately inject failures to verify resilience)

---

## Common Anti-Patterns

### Distributed Monolith
Services are deployed independently but must be changed, tested, and deployed together. Causes:
- Shared libraries with business logic
- Synchronous call chains that create tight runtime coupling
- Shared database schemas

### Shared Database
Multiple services read/write the same database tables. Eliminates independent deployability and schema evolution. Always give each service its own data store.

### Chatty Services
Excessive fine-grained calls between services. If Service A makes 20 calls to Service B to fulfill one request:
- Aggregate into coarser-grained APIs
- Consider if the boundary is drawn incorrectly
- Use batch endpoints or data replication

### Mega Service / God Service
One service grows to handle too many responsibilities, becoming a monolith in disguise. Enforce bounded contexts.

### Ignoring Network Fallibility
Treating remote calls like local function calls. Always account for latency, partial failure, and network partitions.

### Synchronous Chains
`A -> B -> C -> D` where each call is synchronous. Latency compounds, and failure in any service fails the entire chain. Prefer async communication or reduce chain depth.

---

## Migration from Monolith

### Strangler Fig Pattern

Incrementally replace monolith functionality with microservices.

```
Phase 1: All traffic --> Monolith

Phase 2: Proxy/Router --> New Service (handles /orders)
                     \--> Monolith (handles everything else)

Phase 3: Proxy/Router --> Order Service
                     \--> Payment Service
                     \--> Monolith (shrinking)

Phase N: Monolith is decommissioned
```

Steps:
1. Place a routing layer (API gateway, reverse proxy) in front of the monolith
2. Identify a bounded context to extract
3. Build the new service alongside the monolith
4. Redirect traffic for that context to the new service
5. Repeat, shrinking the monolith over time

### Branch by Abstraction

Refactor internally before extracting.

1. Create an abstraction (interface) for the functionality to extract
2. Implement the abstraction with the existing monolith code
3. Build a second implementation that calls the new microservice
4. Switch the implementation (feature flag or configuration)
5. Remove the old implementation once the new service is stable

### Migration guidance:
- Extract the most independently valuable bounded context first
- Avoid extracting shared/core logic early (it has the most coupling)
- Ensure the monolith and new services can coexist indefinitely
- Data migration is the hardest part; plan for dual-write or change-data-capture strategies
- Measure success by deployment independence, not service count

---

## References

- Sam Newman, *Building Microservices* (2nd edition)
- Chris Richardson, *Microservices Patterns*
- Martin Fowler, microservices articles at martinfowler.com
- Eric Evans, *Domain-Driven Design*
- OpenTelemetry documentation: opentelemetry.io
- Kubernetes documentation: kubernetes.io
