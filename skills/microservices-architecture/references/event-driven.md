# Event-Driven Architecture

## Publish-Subscribe Pattern

```
Service A publishes event
    ↓
Message Bus (RabbitMQ, Kafka, SQS)
    ↓ Distributes to interested subscribers
Service B (subscribes)
Service C (subscribes)
Service D (subscribes)
```

## Benefits

- Loose coupling: Services don't know about each other
- Scalability: Easy to add new subscribers
- Resilience: Services handle failures independently
- Audit trail: All events logged

## Implementation Example

### With Apache Kafka

```python
# Service A: Publish Event
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('user-events', {
    'event_type': 'user_registered',
    'user_id': 123,
    'timestamp': '2025-02-07T10:30:00Z'
})
```

### Service B: Subscribe Event
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['localhost:9092'],
    group_id='email-service'
)

for message in consumer:
    event = message.value
    if event['event_type'] == 'user_registered':
        send_welcome_email(event['user_id'])
```

## Event Schema

```json
{
  "event_id": "evt_abc123",
  "event_type": "order.created",
  "aggregate_id": "order_xyz",
  "timestamp": "2025-02-07T10:30:00Z",
  "version": 1,
  "source_service": "order-service",
  "payload": {
    "order_id": "order_xyz",
    "user_id": "user_123",
    "total": 99.99,
    "items": [...]
  }
}
```

## Tools

- **Kafka** - High-throughput, distributed
- **RabbitMQ** - Flexible routing
- **AWS SNS/SQS** - Managed service
- **Google Pub/Sub** - Fully managed
- **Azure Service Bus** - Enterprise features

## Advantages

✓ Event history (audit trail)
✓ Replay events for recovery
✓ Multiple consumers can process same event
✓ Easy to add new features without changing existing code

## Challenges

✗ Eventual consistency (not immediate)
✗ Debugging distributed flows
✗ Duplicate event handling
✗ Event versioning/evolution
