# Service Decomposition Patterns

## Domain-Driven Design

Decompose by business domain:

```
E-Commerce
├─ User Service (authentication, profiles)
├─ Product Service (catalog, search)
├─ Order Service (order management)
├─ Payment Service (payment processing)
└─ Inventory Service (stock management)
```

Each service owns its database and business logic.

## Shared Responsibility Model

Each team owns:
- Full stack (frontend, backend, database, ops)
- Performance
- Security
- On-call rotation

## Anti-Patterns to Avoid

### ❌ Shared Database
```
User Service ──┐
Order Service  ├─→ Shared Database ❌
Payment Service─
```

Services coupled to database schema, hard to scale independently.

### ✓ Database per Service
```
User Service → DB1
Order Service → DB2
Payment Service → DB3
```

Each service owns its data.

### ❌ Too Many Services
More than 20-30 services becomes complex to manage.

### ✓ Right Size
Balance between independence and operational complexity.

## API Contracts

Define clear contracts between services:

```
GET /users/{id}
→ {id, email, name, created_at}

GET /orders/{id}
→ {id, user_id, total, status, items: [...]}
```

Use OpenAPI/Swagger for documentation.

## Versioning Services

Support multiple API versions:

```
GET /api/v1/order/{id}
GET /api/v2/order/{id}
```

Gradually deprecate old versions.
