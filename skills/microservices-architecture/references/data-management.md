# Data Management in Microservices

## Database per Service Pattern

Each service owns its database:

```
┌─────────────────────────────────────┐
│ User Service                        │
│ ┌──────────────────────────────┐   │
│ │   PostgreSQL (users table)   │   │
│ └──────────────────────────────┘   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Order Service                       │
│ ┌──────────────────────────────┐   │
│ │   MongoDB (orders)           │   │
│ └──────────────────────────────┘   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Payment Service                     │
│ ┌──────────────────────────────┐   │
│ │  PostgreSQL (transactions)   │   │
│ └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Advantages:**
- Technology independence (SQL, NoSQL, etc)
- Independent scaling
- Data isolation

**Challenges:**
- Distributed transactions
- Data consistency (eventual consistency)
- Cross-service queries require API calls

## Distributed Transactions

### Saga Pattern (Choreography)

Services publish events, others react:

```
User Service                Order Service              Payment Service
     │                           │                            │
     │──create order event──────>│                            │
     │                           │──reserve payment event───>│
     │                           │<─payment reserved event───│
     │<─order confirmed event────│                            │
     │                           │                            │
```

Implementation:

```python
# User Service - publishes order event
def create_order(user_id, items):
    order_id = generate_id()
    event_bus.publish('OrderCreated', {
        'order_id': order_id,
        'user_id': user_id,
        'items': items,
        'total': calculate_total(items)
    })
    return order_id

# Order Service - listens to PaymentReserved, publishes OrderConfirmed
@event_bus.subscribe('PaymentReserved')
def on_payment_reserved(event):
    order_service.confirm_order(event['order_id'])
    event_bus.publish('OrderConfirmed', {
        'order_id': event['order_id'],
        'user_id': event['user_id']
    })

# Payment Service - listens to OrderCreated, reserves payment
@event_bus.subscribe('OrderCreated')
def on_order_created(event):
    payment = payment_service.reserve(
        user_id=event['user_id'],
        amount=event['total']
    )
    event_bus.publish('PaymentReserved', {
        'order_id': event['order_id'],
        'payment_id': payment.id
    })
```

### Saga Pattern (Orchestration)

Central coordinator manages saga:

```python
class OrderSaga:
    def __init__(self, order_service, payment_service):
        self.order_service = order_service
        self.payment_service = payment_service
        self.state = 'PENDING'
    
    def execute(self, order_data):
        try:
            # Step 1: Create order
            order = self.order_service.create_draft_order(order_data)
            
            # Step 2: Reserve payment
            payment = self.payment_service.reserve(
                order.user_id,
                order.total
            )
            
            # Step 3: Confirm order
            self.order_service.confirm_order(order.id)
            
            self.state = 'COMPLETED'
            return order
        
        except Exception as e:
            # Compensating transactions
            self.compensate(order, payment)
            self.state = 'FAILED'
            raise
    
    def compensate(self, order, payment):
        """Undo transactions on failure"""
        if payment:
            self.payment_service.release_reservation(payment.id)
        if order:
            self.order_service.delete_draft_order(order.id)
```

## Handling Consistency

### Eventual Consistency

Accept temporary inconsistency:

```python
# User Service - publishes UserCreated event
def create_user(email, name):
    user = db.insert('users', {'email': email, 'name': name})
    event_bus.publish('UserCreated', {
        'user_id': user.id,
        'email': email,
        'name': name
    })
    return user

# Order Service - maintains denormalized user data
@event_bus.subscribe('UserCreated')
def on_user_created(event):
    # Denormalize to local cache
    cache.set(f'user:{event["user_id"]}', {
        'name': event['name'],
        'email': event['email']
    })

# When querying orders
def get_user_orders(user_id):
    orders = db.query('orders').where('user_id', user_id)
    
    # Get user info (might be slightly stale)
    user = cache.get(f'user:{user_id}')
    
    return {'user': user, 'orders': orders}
```

### Strong Consistency with Two-Phase Commit

Use for critical transactions (risky at scale):

```python
def transfer_money(from_user, to_user, amount):
    # Phase 1: Prepare
    from_account = account_service.prepare_withdrawal(from_user, amount)
    to_account = account_service.prepare_deposit(to_user, amount)
    
    try:
        # Phase 2: Commit
        account_service.commit_withdrawal(from_user, from_account)
        account_service.commit_deposit(to_user, to_account)
    except Exception:
        # Rollback
        account_service.abort_withdrawal(from_user, from_account)
        account_service.abort_deposit(to_user, to_account)
        raise
```

## Cross-Service Data Queries

### API Aggregation

Client calls multiple services:

```python
def get_user_with_orders(user_id):
    # Call multiple services
    user = user_service.get_user(user_id)
    orders = order_service.get_user_orders(user_id)
    payments = payment_service.get_user_payments(user_id)
    
    return {
        'user': user,
        'orders': orders,
        'payments': payments
    }
```

### Denormalization/Materialized Views

Maintain replicated data:

```python
class OrderView:
    """Denormalized view combining Order + User + Payment info"""
    
    def __init__(self, db, event_bus):
        self.db = db
        self.event_bus = event_bus
        
        # Subscribe to all relevant events
        event_bus.subscribe('OrderCreated', self.on_order_created)
        event_bus.subscribe('UserNameChanged', self.on_user_updated)
        event_bus.subscribe('PaymentProcessed', self.on_payment_updated)
    
    def on_order_created(self, event):
        # Store denormalized data
        self.db.insert('order_view', {
            'order_id': event['order_id'],
            'user_id': event['user_id'],
            'user_name': self.fetch_user_name(event['user_id']),
            'items': event['items'],
            'status': 'created'
        })
    
    def get_order_view(self, order_id):
        return self.db.query('order_view').where('order_id', order_id).first()
```

Benefits:
- Fast reads (single query)
- Handles denormalization explicitly

## Data Synchronization

### Change Data Capture (CDC)

Capture database changes and propagate:

```python
# Using Debezium or similar
# Automatically captures changes to PostgreSQL
# Publishes to Kafka topic

# Subscribe to changes
kafka_consumer.subscribe(['users_changes'])

for message in kafka_consumer:
    change = json.loads(message.value)
    # 'op': 'create', 'read', 'update', 'delete'
    # 'before': previous state
    # 'after': new state
    
    if change['op'] == 'update':
        user_cache.update(
            change['after']['id'],
            change['after']
        )
```

### Message-Driven Data Replication

```python
# User service publishes data changes
def update_user(user_id, new_data):
    user = db.update('users', user_id, new_data)
    
    # Publish event
    event_bus.publish('UserUpdated', {
        'user_id': user.id,
        'changes': new_data,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return user

# Search service keeps indexes updated
@event_bus.subscribe('UserUpdated')
def on_user_updated(event):
    search_index.update(
        f'user_{event["user_id"]}',
        event['changes']
    )
```
