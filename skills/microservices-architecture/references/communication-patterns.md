# Microservices Communication Patterns

## Synchronous Communication

### REST API (Request-Response)

**When to use:** Simple request-response interactions, CRUD operations

```python
# User Service calling Order Service
import requests

def create_order(user_id, items):
    try:
        # Synchronous HTTP call
        response = requests.post(
            'http://order-service/api/orders',
            json={'user_id': user_id, 'items': items},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise TimeoutError("Order service is slow")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Order service is down")
```

**Challenges:**
- Tight coupling between services
- Cascading failures
- Slow if downstream service is slow
- Harder to scale

### gRPC (Remote Procedure Call)

**When to use:** High-performance internal communication, binary protocol needed

```protobuf
// order.proto
service OrderService {
    rpc CreateOrder(CreateOrderRequest) returns (Order) {}
    rpc GetOrder(GetOrderRequest) returns (Order) {}
}

message CreateOrderRequest {
    string user_id = 1;
    repeated Item items = 2;
}

message Order {
    string order_id = 1;
    string user_id = 2;
    repeated Item items = 3;
    string status = 4;
}
```

**Python Client:**
```python
import grpc
from order_pb2 import CreateOrderRequest

def order_service_client():
    with grpc.insecure_channel('order-service:50051') as channel:
        stub = OrderServiceStub(channel)
        request = CreateOrderRequest(
            user_id='user123',
            items=[{'id': 'item1', 'qty': 2}]
        )
        response = stub.CreateOrder(request)
        return response
```

**Advantages:**
- High performance (binary protocol)
- Efficient serialization
- Built-in multiplexing
- Supports streaming

## Asynchronous Communication

### Message Queue (RabbitMQ, Kafka)

**When to use:** Decoupled processing, event streaming, order guarantees

```python
# User Service publishes "user_created" event
import pika

def publish_user_created(user_id, user_data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq-host')
    )
    channel = connection.channel()
    
    channel.exchange_declare(
        exchange='user_events',
        exchange_type='topic'
    )
    
    channel.basic_publish(
        exchange='user_events',
        routing_key='user.created',
        body=json.dumps({
            'user_id': user_id,
            'data': user_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    )
    
    connection.close()

# Order Service subscribes to "user_created" events
def consume_user_events():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('rabbitmq-host')
    )
    channel = connection.channel()
    
    channel.exchange_declare(
        exchange='user_events',
        exchange_type='topic'
    )
    
    # Declare queue
    result = channel.queue_declare(queue='order_user_queue')
    queue_name = result.method.queue
    
    # Bind queue to topic
    channel.queue_bind(
        exchange='user_events',
        queue=queue_name,
        routing_key='user.created'
    )
    
    # Consume
    def callback(ch, method, properties, body):
        message = json.loads(body)
        print(f"New user: {message['user_id']}")
        # Process user
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback
    )
    
    channel.start_consuming()
```

### Event Sourcing

Store all changes as an immutable sequence of events:

```python
# Event store
class Event:
    def __init__(self, aggregate_id, event_type, data):
        self.aggregate_id = aggregate_id
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.utcnow()

class EventStore:
    def __init__(self, db):
        self.db = db
    
    def append_event(self, event):
        """Store event immutably"""
        self.db.insert('events', {
            'aggregate_id': event.aggregate_id,
            'event_type': event.event_type,
            'data': event.data,
            'timestamp': event.timestamp
        })
    
    def get_events(self, aggregate_id):
        """Get all events for aggregate"""
        return self.db.query('events')
            .where('aggregate_id', aggregate_id)
            .order_by('timestamp')
            .all()

# Using event sourcing
def create_order(user_id, items):
    event = Event(
        aggregate_id=f'order_{order_id}',
        event_type='OrderCreated',
        data={'user_id': user_id, 'items': items}
    )
    event_store.append_event(event)

def get_order(order_id):
    events = event_store.get_events(f'order_{order_id}')
    # Replay events to reconstruct current state
    order = {}
    for event in events:
        if event.event_type == 'OrderCreated':
            order = {**event.data, 'status': 'created'}
        elif event.event_type == 'OrderShipped':
            order['status'] = 'shipped'
    return order
```

## Service-to-Service Communication Patterns

### API Gateway Pattern

Central entry point for all client requests:

```nginx
# nginx.conf as API Gateway
upstream user_service {
    server user-service:8001;
}

upstream order_service {
    server order-service:8002;
}

upstream payment_service {
    server payment-service:8003;
}

server {
    listen 8000;
    
    # Route user requests
    location /api/users {
        proxy_pass http://user_service;
    }
    
    # Route order requests
    location /api/orders {
        proxy_pass http://order_service;
    }
    
    # Route payment requests
    location /api/payments {
        proxy_pass http://payment_service;
    }
    
    # Add authentication/authorization
    location / {
        auth_request /auth;
        proxy_pass http://requested_service;
    }
}
```

### Service Mesh (Istio)

Manage service-to-service communication:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: users
spec:
  hosts:
  - users
  http:
  - match:
    - uri:
        prefix: "/v1"
    route:
    - destination:
        host: users
        port:
          number: 8001
        subset: v1
  - match:
    - uri:
        prefix: "/v2"
    route:
    - destination:
        host: users
        port:
          number: 8001
        subset: v2
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
```

### Circuit Breaker

Prevent cascading failures:

```python
from circuit_breaker import CircuitBreaker

class CallOrderServiceCircuitBreaker:
    def __init__(self):
        self.breaker = CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            listeners=[self.on_state_change]
        )
    
    @breaker
    def call_order_service(self, user_id):
        return requests.get(
            f'http://order-service/api/user/{user_id}',
            timeout=2
        )
    
    def on_state_change(self, breaker, before, after):
        if after == 'open':
            print("Circuit breaker OPEN - service unavailable")
            # Send alert
        elif after == 'closed':
            print("Circuit breaker CLOSED - service recovered")
```

States:
- **Closed**: Normal operation, requests pass through
- **Open**: Service failing, requests rejected immediately
- **Half-Open**: Testing if service recovered, allowing limited requests

### Bulkhead Pattern

Isolate resources:

```python
from concurrent.futures import ThreadPoolExecutor

class ServiceClients:
    def __init__(self):
        # Separate thread pools for different services
        self.user_executor = ThreadPoolExecutor(max_workers=5)
        self.order_executor = ThreadPoolExecutor(max_workers=10)
        self.payment_executor = ThreadPoolExecutor(max_workers=3)
    
    def get_user(self, user_id):
        # Task runs in user_executor pool
        # Limits concurrency to 5 requests
        return self.user_executor.submit(
            self._call_user_service, user_id
        )
```

## Resilience Patterns

### Retry with Exponential Backoff

```python
import time
from functools import wraps

def retry_with_backoff(max_attempts=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Attempt {attempt+1} failed, retrying in {delay}s")
                    time.sleep(delay)
        
        return wrapper
    return decorator

@retry_with_backoff(max_attempts=3, base_delay=1)
def call_downstream_service():
    response = requests.get('http://downstream-service/api/data')
    response.raise_for_status()
    return response.json()
```

### Timeout Patterns

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_timeout():
    session = requests.Session()
    
    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Make requests with timeout
    response = session.get(
        'http://service',
        timeout=2.0  # 2 second timeout
    )
    
    return response
```
