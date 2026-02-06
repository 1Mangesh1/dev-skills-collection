# Microservices Architecture Quick Start

Design and implement scalable microservices architectures with proven patterns.

## Service Decomposition

### Domain-Driven Design (DDD)
```
Bounded Contexts:
├─ User Service (registration, profile)
├─ Order Service (order management)
├─ Payment Service (payment processing)
└─ Inventory Service (product stock)
```

Each service owns its database, has clear boundaries

## Communication Patterns

### Synchronous (Request-Response)
```
Service A --→ Service B
         ←-- Response
```
Fast but creates tight coupling

### Asynchronous (Event-Driven)
```
Service A → Event Bus → Service B
                    → Service C
```
Loose coupling, eventual consistency

## Essential Patterns

### Circuit Breaker
Prevent cascading failures
```javascript
const breaker = new CircuitBreaker(async () => {
  return await callService();
}, { threshold: 5, timeout: 60000 });
```

### Saga Pattern (Distributed Transactions)
```
Service A: Process → ✓
           ↓
Service B: Process → ✓
           ↓
Service C: Process → ✗ (Compensate A & B)
```

### API Gateway
```
Client → API Gateway → Service 1
                    → Service 2
                    → Service 3
```
Single entry point, routing, rate limiting

## Database Strategy

```
User Service       Order Service      Payment Service
  [User DB]         [Order DB]          [Payment DB]
     ✓ Isolation        ✓ Tech freedom      ✓ Scaling
     ✓ Scaling          ✓ Independent      ✓ Security
     ✗ Joins hard       ✗ Consistency      
```

## Configuration Example

```yaml
services:
  user-service:
    database: postgres://users
    cache: redis://cache:6379
    logging: json
    
  order-service:
    database: mysql://orders
    messageQueue: rabbitmq://queue
    
  api-gateway:
    routes:
      /users: user-service:8001
      /orders: order-service:8002
```

## Reliability Patterns

### Retry Logic
```javascript
for (let i = 0; i < 3; i++) {
  try {
    return await service.call();
  } catch(e) {
    if (i === 2) throw e;
    await sleep(1000 * Math.pow(2, i));
  }
}
```

### Timeout Management
- Set timeouts at every level
- Shortest timeout for fastest failure

## Monitoring Essentials

1. **Distributed Tracing** - Track requests across services
2. **Request Correlation IDs** - Link related requests
3. **Service Health** - Status of each service
4. **Latency** - Request times, bottlenecks

## Deployment Strategies

### Blue-Green
Two identical environments, switch traffic

### Canary
Gradually roll out to % of users

### Rolling
Gradually replace old instances

## Common Challenges

| Challenge | Solution |
|-----------|----------|
| Consistency | Saga pattern, event sourcing |
| Debugging | Distributed tracing, correlation IDs |
| Complexity | Service mesh (Istio, Linkerd) |
| Latency | Caching, async communication |

## Tools & Technologies

- **API Gateway**: Kong, AWS API Gateway, Ambassador
- **Service Mesh**: Istio, Linkerd
- **Message Queue**: Kafka, RabbitMQ, AWS SQS
- **Monitoring**: Jaeger, Prometheus, Grafana
- **Container Orchestration**: Kubernetes, Docker Swarm

## Team Structure

- Cross-functional teams per service
- Clear API contracts
- Async communication between teams
- Shared monitoring/alerting

## Resources

- [Sam Newman - Building Microservices](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/)
- [Chris Richardson - Microservices.io](https://microservices.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Microservices Architecture](https://aws.amazon.com/microservices/)

## See Also

- SKILL.md - Detailed patterns and examples
- metadata.json - Architecture references
