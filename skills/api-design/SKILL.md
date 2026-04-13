---
name: api-design
description: This skill should be used when the user asks to "design a REST API", "create API endpoints", "write OpenAPI spec", "design API routes", "add pagination to API", "version an API", "create API schema", "design webhook endpoints", "structure API responses", "implement HATEOAS", or mentions REST API design, endpoint naming, HTTP methods, status codes, API best practices, request/response design, or API documentation.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - api
    - rest
    - openapi
    - design
    - endpoints
    - http
    - swagger
---

# REST API Design

A comprehensive skill for designing production-quality REST APIs. Covers resource naming, HTTP semantics, status codes, pagination, versioning, OpenAPI specs, authentication, error handling, and more.

## Capabilities

1. **Resource Naming** - RESTful URI conventions and hierarchy design
2. **HTTP Method Mapping** - Correct use of GET, POST, PUT, PATCH, DELETE
3. **Status Code Selection** - Appropriate codes for every scenario
4. **Request/Response Design** - Envelopes, pagination, filtering, sorting
5. **API Versioning** - URL, header, and query parameter strategies
6. **OpenAPI Specification** - Complete 3.1 spec generation with examples
7. **Authentication Patterns** - API keys, OAuth2, JWT Bearer tokens
8. **Rate Limiting** - Headers, strategies, and client guidance
9. **HATEOAS** - Hypermedia-driven API navigation
10. **Error Handling** - RFC 7807 Problem Details format
11. **Webhook Design** - Event-driven API extension patterns
12. **Bulk Operations** - Batch endpoints and partial failure handling
13. **Idempotency** - Safe retries with idempotency keys

## Usage

```
/api-design [command] [options]
```

### Commands

- `design <resource>` - Design CRUD endpoints for a resource
- `openapi <resource>` - Generate OpenAPI 3.1 spec for a resource
- `endpoints <domain>` - Propose endpoint structure for a domain
- `review <spec>` - Review an existing API design for best practices
- `paginate <strategy>` - Implement cursor or offset pagination
- `errors` - Generate RFC 7807 error response templates
- `webhooks <events>` - Design webhook endpoints for given events
- `version <strategy>` - Apply versioning strategy to existing API

---

## RESTful Resource Naming Conventions

Resources are nouns, not verbs. Use plural nouns for collections.

### URI Structure

```
# Good - plural nouns, hierarchical
GET    /users
GET    /users/{userId}
GET    /users/{userId}/orders
GET    /users/{userId}/orders/{orderId}
POST   /users/{userId}/orders

# Bad - verbs in path, singular nouns, flat structure
GET    /getUser?id=123
POST   /createOrder
GET    /user/123/getOrders
DELETE /deleteUser/123
```

### Naming Rules

| Rule | Good | Bad |
|------|------|-----|
| Plural nouns | `/users` | `/user` |
| Lowercase | `/order-items` | `/OrderItems` |
| Hyphens for readability | `/order-items` | `/order_items` or `/orderItems` |
| No verbs | `/users/{id}/activate` (POST) | `/activateUser` |
| No file extensions | `/users` | `/users.json` |
| Hierarchy via nesting | `/users/{id}/posts` | `/user-posts?userId=1` |
| Max 3 levels deep | `/users/{id}/orders` | `/users/{id}/orders/{oid}/items/{iid}/reviews` |

### Sub-Resources vs. Top-Level

```
# Sub-resource: order belongs to user (tight coupling)
GET /users/{userId}/orders/{orderId}

# Top-level: when resource is accessed independently
GET /orders/{orderId}
GET /orders?userId=123

# Use sub-resources when the child cannot exist without the parent
# Use top-level when the resource has its own identity
```

### Actions on Resources

For non-CRUD operations, use a sub-resource verb as a last resort:

```
POST /users/{userId}/activate       # state change
POST /orders/{orderId}/cancel       # business action
POST /reports/generate              # trigger process
POST /emails/{emailId}/resend       # retry action
```

---

## HTTP Methods

### Method Semantics

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Read resource(s) | Yes | Yes | No | Yes |
| POST | Create resource / trigger action | No | No | Yes | Yes |
| PUT | Full replacement of resource | Yes | No | Yes | Yes (optional) |
| PATCH | Partial update of resource | No* | No | Yes | Yes |
| DELETE | Remove resource | Yes | No | No (usually) | No (usually) |
| HEAD | Same as GET, no body | Yes | Yes | No | No |
| OPTIONS | List allowed methods | Yes | Yes | No | Yes |

*PATCH can be made idempotent with JSON Merge Patch (RFC 7396).

### Examples

```bash
# CREATE - return 201 with Location header
curl -X POST https://api.example.com/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# Response: 201 Created
# Location: /v1/users/usr_abc123

# READ collection with filtering
curl "https://api.example.com/v1/users?status=active&sort=-created_at&limit=20"

# READ single resource
curl https://api.example.com/v1/users/usr_abc123

# FULL UPDATE - must send complete resource
curl -X PUT https://api.example.com/v1/users/usr_abc123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Smith", "email": "alice@example.com", "status": "active"}'

# PARTIAL UPDATE - send only changed fields
curl -X PATCH https://api.example.com/v1/users/usr_abc123 \
  -H "Content-Type: application/merge-patch+json" \
  -d '{"name": "Alice Smith"}'

# DELETE
curl -X DELETE https://api.example.com/v1/users/usr_abc123
# Response: 204 No Content
```

---

## HTTP Status Codes

### 2xx Success

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Successful GET, PUT, PATCH, or DELETE |
| 201 | Created | Successful POST that creates a resource |
| 202 | Accepted | Request accepted for async processing |
| 204 | No Content | Successful DELETE or PUT with no response body |

### 3xx Redirection

| Code | Name | When to Use |
|------|------|-------------|
| 301 | Moved Permanently | Resource URL permanently changed |
| 302 | Found | Temporary redirect (avoid for APIs) |
| 304 | Not Modified | Conditional GET, resource unchanged (ETag/If-None-Match) |
| 307 | Temporary Redirect | Temporary redirect, preserves method |
| 308 | Permanent Redirect | Permanent redirect, preserves method |

### 4xx Client Errors

| Code | Name | When to Use |
|------|------|-------------|
| 400 | Bad Request | Malformed syntax, invalid parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 405 | Method Not Allowed | HTTP method not supported on resource |
| 409 | Conflict | Resource state conflict (duplicate, version mismatch) |
| 410 | Gone | Resource permanently deleted (useful for deprecated endpoints) |
| 415 | Unsupported Media Type | Content-Type not supported |
| 422 | Unprocessable Entity | Valid syntax but semantic errors (validation failures) |
| 429 | Too Many Requests | Rate limit exceeded |

### 5xx Server Errors

| Code | Name | When to Use |
|------|------|-------------|
| 500 | Internal Server Error | Unexpected server failure |
| 502 | Bad Gateway | Upstream service failure |
| 503 | Service Unavailable | Temporary overload or maintenance |
| 504 | Gateway Timeout | Upstream service timeout |

---

## Request/Response Design

### Response Envelope

Use a consistent envelope for all responses:

```json
{
  "data": {
    "id": "usr_abc123",
    "type": "user",
    "attributes": {
      "name": "Alice Smith",
      "email": "alice@example.com",
      "created_at": "2025-01-15T10:30:00Z"
    }
  },
  "meta": {
    "request_id": "req_xyz789"
  }
}
```

### Collection Response with Pagination

```json
{
  "data": [
    {"id": "usr_001", "name": "Alice"},
    {"id": "usr_002", "name": "Bob"}
  ],
  "meta": {
    "total_count": 142,
    "page_size": 20,
    "request_id": "req_xyz789"
  },
  "links": {
    "self": "/v1/users?cursor=abc&limit=20",
    "next": "/v1/users?cursor=def&limit=20",
    "prev": "/v1/users?cursor=ghi&limit=20"
  }
}
```

### Filtering, Sorting, and Field Selection

```bash
# Filtering - use field names as query params
GET /v1/users?status=active&role=admin&created_after=2025-01-01

# Sorting - prefix with - for descending
GET /v1/users?sort=-created_at,name

# Field selection - reduce payload size
GET /v1/users?fields=id,name,email

# Combined
GET /v1/users?status=active&sort=-created_at&fields=id,name&limit=10
```

### Filtering Operators

For advanced filtering, use a structured syntax:

```bash
# LHS brackets style
GET /v1/products?price[gte]=10&price[lte]=100&name[contains]=widget

# Supported operators
# eq    - equals (default)
# neq   - not equals
# gt    - greater than
# gte   - greater than or equal
# lt    - less than
# lte   - less than or equal
# in    - in list:        ?status[in]=active,pending
# nin   - not in list:    ?status[nin]=deleted,archived
# contains - substring:   ?name[contains]=alice
```

---

## API Versioning

### Strategy 1: URL Path (Recommended)

```
GET /v1/users
GET /v2/users
```

Pros: Simple, visible, easy to route. Cons: Not purely RESTful.

### Strategy 2: Custom Header

```bash
GET /users
Accept-Version: v2
# or
X-API-Version: 2
```

Pros: Clean URLs. Cons: Hidden, harder to test in browser.

### Strategy 3: Accept Header (Content Negotiation)

```bash
GET /users
Accept: application/vnd.myapi.v2+json
```

Pros: RESTful purity. Cons: Complex, poor tooling support.

### Strategy 4: Query Parameter

```
GET /users?version=2
```

Pros: Easy to test. Cons: Pollutes query string, easy to forget.

### Versioning Best Practices

- Use URL path versioning for public APIs (simplest for consumers)
- Increment major version only for breaking changes
- Support at least N-1 version concurrently
- Provide clear deprecation timeline (minimum 6-12 months)
- Return `Sunset` and `Deprecation` headers for old versions

```
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
Deprecation: true
Link: <https://api.example.com/v3/users>; rel="successor-version"
```

---

## OpenAPI 3.1 Specification

### Minimal Example

```yaml
openapi: "3.1.0"
info:
  title: User Management API
  version: "1.0.0"
  description: API for managing users
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      tags: [Users]
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: cursor
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, suspended]
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserListResponse"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "429":
          $ref: "#/components/responses/RateLimited"

    post:
      operationId: createUser
      summary: Create a new user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
      responses:
        "201":
          description: User created
          headers:
            Location:
              schema:
                type: string
              description: URL of created resource
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserResponse"
        "422":
          $ref: "#/components/responses/ValidationError"

  /users/{userId}:
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: string
          pattern: "^usr_[a-zA-Z0-9]{10,}$"
    get:
      operationId: getUser
      summary: Get user by ID
      tags: [Users]
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserResponse"
        "404":
          $ref: "#/components/responses/NotFound"

components:
  schemas:
    User:
      type: object
      required: [id, name, email, created_at]
      properties:
        id:
          type: string
          example: "usr_abc123"
        name:
          type: string
          example: "Alice Smith"
        email:
          type: string
          format: email
        status:
          type: string
          enum: [active, inactive, suspended]
          default: active
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email

    UserResponse:
      type: object
      properties:
        data:
          $ref: "#/components/schemas/User"

    UserListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/User"
        meta:
          $ref: "#/components/schemas/PaginationMeta"
        links:
          $ref: "#/components/schemas/PaginationLinks"

    PaginationMeta:
      type: object
      properties:
        total_count:
          type: integer
        page_size:
          type: integer

    PaginationLinks:
      type: object
      properties:
        self:
          type: string
        next:
          type: string
          nullable: true
        prev:
          type: string
          nullable: true

    ProblemDetail:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"
    ValidationError:
      description: Validation failed
      content:
        application/problem+json:
          schema:
            allOf:
              - $ref: "#/components/schemas/ProblemDetail"
              - type: object
                properties:
                  errors:
                    type: array
                    items:
                      type: object
                      properties:
                        field:
                          type: string
                        message:
                          type: string
    RateLimited:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - BearerAuth: []
```

---

## Authentication Patterns

### API Key Authentication

```bash
# In header (recommended)
curl -H "X-API-Key: sk_live_abc123" https://api.example.com/v1/users

# In query parameter (discouraged - visible in logs)
curl "https://api.example.com/v1/users?api_key=sk_live_abc123"
```

Best practices for API keys:
- Use prefixes to identify key type: `sk_live_`, `sk_test_`, `pk_live_`
- Hash keys in storage (store only the hash, never plaintext)
- Support key rotation (allow multiple active keys per account)
- Return the full key only at creation time

### OAuth 2.0 Bearer Token

```bash
# Authorization Code flow result
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..." \
  https://api.example.com/v1/users
```

### JWT Structure

```json
// Header
{"alg": "RS256", "typ": "JWT", "kid": "key-2025-01"}

// Payload
{
  "sub": "usr_abc123",
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "exp": 1706140800,
  "iat": 1706137200,
  "scope": "read:users write:users",
  "org_id": "org_xyz"
}
```

### Token Refresh Pattern

```bash
# Access token expired, use refresh token
curl -X POST https://auth.example.com/oauth/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=rt_abc123" \
  -d "client_id=app_xyz"

# Response
{
  "access_token": "eyJhbG...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "rt_def456"
}
```

---

## Rate Limiting

### Response Headers

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 994
X-RateLimit-Reset: 1706140800
RateLimit-Policy: 1000;w=3600
```

### Rate Limit Exceeded Response

```
HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706140800
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded 1000 requests per hour. Try again in 42 seconds.",
  "instance": "/v1/users"
}
```

### Rate Limiting Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Fixed Window | N requests per time window | Simple, general purpose |
| Sliding Window | Rolling window counter | Smoother distribution |
| Token Bucket | Tokens refill at fixed rate | Allows bursts |
| Leaky Bucket | Requests drain at fixed rate | Strict rate enforcement |

---

## HATEOAS and Hypermedia

Hypermedia as the Engine of Application State - embed navigation links in responses.

```json
{
  "data": {
    "id": "ord_abc123",
    "status": "pending",
    "total": 99.99
  },
  "links": {
    "self": {"href": "/v1/orders/ord_abc123", "method": "GET"},
    "cancel": {"href": "/v1/orders/ord_abc123/cancel", "method": "POST"},
    "pay": {"href": "/v1/orders/ord_abc123/payments", "method": "POST"},
    "items": {"href": "/v1/orders/ord_abc123/items", "method": "GET"},
    "customer": {"href": "/v1/users/usr_xyz", "method": "GET"}
  }
}
```

After payment, the response changes -- `pay` link disappears, `refund` appears:

```json
{
  "data": {
    "id": "ord_abc123",
    "status": "paid",
    "total": 99.99
  },
  "links": {
    "self": {"href": "/v1/orders/ord_abc123", "method": "GET"},
    "refund": {"href": "/v1/orders/ord_abc123/refund", "method": "POST"},
    "items": {"href": "/v1/orders/ord_abc123/items", "method": "GET"},
    "receipt": {"href": "/v1/orders/ord_abc123/receipt", "method": "GET"}
  }
}
```

---

## Error Response Format (RFC 7807)

Use `application/problem+json` content type for all errors.

### Structure

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/v1/users",
  "errors": [
    {
      "field": "email",
      "message": "Must be a valid email address",
      "code": "invalid_format"
    },
    {
      "field": "name",
      "message": "Must be between 1 and 100 characters",
      "code": "invalid_length"
    }
  ]
}
```

### Common Error Types

```json
// 400 Bad Request
{
  "type": "https://api.example.com/problems/bad-request",
  "title": "Bad Request",
  "status": 400,
  "detail": "The JSON body could not be parsed. Expected '}' at line 3, column 12."
}

// 401 Unauthorized
{
  "type": "https://api.example.com/problems/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "The access token has expired. Please refresh your token."
}

// 403 Forbidden
{
  "type": "https://api.example.com/problems/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You do not have permission to delete users. Required scope: admin:users."
}

// 404 Not Found
{
  "type": "https://api.example.com/problems/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "No user found with ID 'usr_nonexistent'."
}

// 409 Conflict
{
  "type": "https://api.example.com/problems/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "A user with email 'alice@example.com' already exists."
}
```

---

## Pagination

### Cursor-Based Pagination (Recommended)

Best for real-time data, large datasets, and when new records are frequently inserted.

```bash
# First page
GET /v1/users?limit=20

# Response includes cursor for next page
{
  "data": [...],
  "meta": {"has_more": true},
  "links": {
    "next": "/v1/users?cursor=eyJpZCI6InVzcl8wMjAifQ&limit=20"
  }
}

# Next page
GET /v1/users?cursor=eyJpZCI6InVzcl8wMjAifQ&limit=20
```

Cursor implementation (base64-encoded JSON):

```python
import base64, json

def encode_cursor(last_item):
    payload = {"id": last_item["id"], "created_at": last_item["created_at"]}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

def decode_cursor(cursor):
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())

# SQL query with cursor
# SELECT * FROM users
# WHERE (created_at, id) < (:cursor_created_at, :cursor_id)
# ORDER BY created_at DESC, id DESC
# LIMIT :limit + 1   -- fetch one extra to determine has_more
```

### Offset-Based Pagination

Simpler but suffers from drift when data changes. Suitable for admin UIs and static data.

```bash
GET /v1/users?page=3&per_page=20

{
  "data": [...],
  "meta": {
    "total_count": 142,
    "page": 3,
    "per_page": 20,
    "total_pages": 8
  },
  "links": {
    "first": "/v1/users?page=1&per_page=20",
    "prev": "/v1/users?page=2&per_page=20",
    "next": "/v1/users?page=4&per_page=20",
    "last": "/v1/users?page=8&per_page=20"
  }
}
```

### Comparison

| Feature | Cursor-Based | Offset-Based |
|---------|-------------|--------------|
| Performance at scale | O(1) | O(n) with OFFSET |
| Consistent with inserts | Yes | No (page drift) |
| Jump to arbitrary page | No | Yes |
| Total count available | Optional (expensive) | Yes |
| Bidirectional | With prev cursor | Yes |

---

## Bulk Operations

### Batch Create

```bash
POST /v1/users/batch
Content-Type: application/json

{
  "operations": [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "invalid-email"}
  ]
}

# Response: 207 Multi-Status
{
  "results": [
    {"index": 0, "status": 201, "data": {"id": "usr_001", "name": "Alice"}},
    {"index": 1, "status": 201, "data": {"id": "usr_002", "name": "Bob"}},
    {"index": 2, "status": 422, "error": {
      "type": "https://api.example.com/problems/validation-error",
      "title": "Validation Error",
      "detail": "Invalid email format"
    }}
  ],
  "meta": {
    "total": 3,
    "succeeded": 2,
    "failed": 1
  }
}
```

### Batch Delete

```bash
DELETE /v1/users/batch
Content-Type: application/json

{
  "ids": ["usr_001", "usr_002", "usr_003"]
}
```

### Async Bulk Operations

For large batches, return 202 Accepted with a job resource:

```bash
POST /v1/imports
Content-Type: application/json

{"source_url": "https://storage.example.com/users.csv", "type": "users"}

# Response: 202 Accepted
{
  "data": {
    "id": "job_abc123",
    "status": "processing",
    "progress": 0
  },
  "links": {
    "self": "/v1/imports/job_abc123",
    "cancel": "/v1/imports/job_abc123/cancel"
  }
}

# Poll for status
GET /v1/imports/job_abc123
{
  "data": {
    "id": "job_abc123",
    "status": "completed",
    "progress": 100,
    "result": {"created": 950, "failed": 50, "total": 1000}
  },
  "links": {
    "errors": "/v1/imports/job_abc123/errors"
  }
}
```

---

## Idempotency Keys

Prevent duplicate operations when clients retry requests.

```bash
POST /v1/payments
Idempotency-Key: idem_a1b2c3d4e5
Content-Type: application/json

{"amount": 9999, "currency": "usd", "customer_id": "cus_xyz"}
```

### Server-Side Implementation

```python
import hashlib, json

def handle_request(request):
    idempotency_key = request.headers.get("Idempotency-Key")

    if idempotency_key:
        # Check cache / database for previous result
        cached = db.idempotency_cache.find_one({"key": idempotency_key})

        if cached:
            if cached["request_hash"] != hash_request(request):
                return error(422, "Idempotency key reused with different parameters")
            return cached["response"]  # Return same response as before

    # Process the request
    result = process_payment(request.json)

    # Store result for future retries
    if idempotency_key:
        db.idempotency_cache.insert({
            "key": idempotency_key,
            "request_hash": hash_request(request),
            "response": result,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        })

    return result

def hash_request(request):
    body = json.dumps(request.json, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()
```

### Guidelines

- Require idempotency keys for all POST requests that create resources or trigger side effects
- Keys should be client-generated UUIDs or prefixed random strings
- Cache responses for 24 hours minimum
- Return the same status code and body for replayed requests
- Return 422 if the same key is reused with different request parameters

---

## Webhook Design

### Webhook Registration

```bash
POST /v1/webhooks
Content-Type: application/json

{
  "url": "https://myapp.example.com/hooks/orders",
  "events": ["order.created", "order.paid", "order.refunded"],
  "secret": "whsec_abc123"
}
```

### Webhook Payload

```json
{
  "id": "evt_abc123",
  "type": "order.paid",
  "created_at": "2025-01-15T10:30:00Z",
  "api_version": "2025-01-01",
  "data": {
    "id": "ord_xyz",
    "status": "paid",
    "total": 9999,
    "currency": "usd",
    "customer_id": "cus_def"
  },
  "links": {
    "resource": "/v1/orders/ord_xyz"
  }
}
```

### Webhook Signature Verification

```python
import hmac, hashlib

def verify_webhook(payload_body, signature_header, secret):
    """Verify webhook came from the expected sender."""
    timestamp, signature = parse_signature(signature_header)

    # Prevent replay attacks - reject if timestamp > 5 minutes old
    if abs(time.time() - int(timestamp)) > 300:
        raise ValueError("Webhook timestamp too old")

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload_body}"
    expected = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise ValueError("Invalid webhook signature")

def parse_signature(header):
    """Parse 't=timestamp,v1=signature' format."""
    parts = dict(p.split("=", 1) for p in header.split(","))
    return parts["t"], parts["v1"]
```

### Webhook Best Practices

- Sign payloads with HMAC-SHA256 using a per-endpoint secret
- Include timestamp in signature to prevent replay attacks
- Retry failed deliveries with exponential backoff (1s, 5s, 30s, 5m, 1h)
- Set a 30-second timeout on delivery attempts
- Provide a webhook testing/ping endpoint
- Log all delivery attempts with response codes
- Allow consumers to list recent webhook events and retry delivery
- Send a thin payload with resource ID; let consumer fetch full data if needed

---

## Common Anti-Patterns to Avoid

### 1. Verbs in URLs

```
# Bad
POST /api/createUser
GET  /api/getUsers
POST /api/deleteUser/123

# Good
POST   /v1/users
GET    /v1/users
DELETE /v1/users/123
```

### 2. Ignoring HTTP Methods

```
# Bad - using POST for everything
POST /api/users/get
POST /api/users/update
POST /api/users/delete

# Good - use proper HTTP methods
GET    /v1/users
PUT    /v1/users/{id}
DELETE /v1/users/{id}
```

### 3. Inconsistent Response Shapes

```
# Bad - different structures for different endpoints
GET /users    -> [{"id": 1, "name": "Alice"}]
GET /users/1  -> {"id": 1, "name": "Alice", "email": "..."}
GET /orders   -> {"orders": [...], "count": 10}

# Good - consistent envelope
GET /users    -> {"data": [...], "meta": {...}}
GET /users/1  -> {"data": {...}}
GET /orders   -> {"data": [...], "meta": {...}}
```

### 4. Not Using Proper Status Codes

```
# Bad - always returning 200
HTTP 200 {"error": true, "message": "User not found"}
HTTP 200 {"error": true, "message": "Unauthorized"}

# Good - semantic status codes
HTTP 404 {"type": "...not-found", "title": "Not Found", "status": 404}
HTTP 401 {"type": "...unauthorized", "title": "Unauthorized", "status": 401}
```

### 5. Exposing Internal IDs

```
# Bad - sequential integers leak information
GET /v1/users/42

# Good - opaque identifiers
GET /v1/users/usr_a1b2c3d4
```

### 6. No Versioning

Always version your API from day one. Adding versioning later is a breaking change.

### 7. Deeply Nested Resources

```
# Bad - too many nesting levels
GET /v1/companies/123/departments/456/teams/789/members/012/tasks

# Good - flatten with query params
GET /v1/tasks?team_id=789&assignee_id=012
```

### 8. Missing Content Negotiation

Always set `Content-Type` on responses and respect `Accept` headers.

### 9. Returning Arrays as Root

```
# Bad - root array is vulnerable to JSON hijacking (legacy concern)
# and cannot be extended without breaking changes
[{"id": 1}, {"id": 2}]

# Good - object root allows adding metadata
{"data": [{"id": 1}, {"id": 2}], "meta": {"total": 2}}
```

### 10. No Rate Limiting

Every public API must have rate limits. Without them, a single client can degrade service for all users.

---

## Quick Reference Checklist

When designing a new API, verify these items:

- [ ] Resources use plural nouns (`/users`, not `/user`)
- [ ] URLs are lowercase with hyphens (`/order-items`)
- [ ] HTTP methods match semantics (GET reads, POST creates, etc.)
- [ ] All responses use consistent envelope (`{data, meta, links}`)
- [ ] Errors use RFC 7807 Problem Details format
- [ ] Pagination is implemented (cursor-based for public APIs)
- [ ] Filtering, sorting, and field selection are supported
- [ ] API is versioned from day one (`/v1/...`)
- [ ] Authentication uses Bearer tokens or API keys in headers
- [ ] Rate limiting headers are present on all responses
- [ ] POST endpoints accept Idempotency-Key header
- [ ] OpenAPI spec is complete and up to date
- [ ] All dates use ISO 8601 format with timezone (`2025-01-15T10:30:00Z`)
- [ ] Resource IDs are opaque strings with type prefixes (`usr_`, `ord_`)
- [ ] 201 responses include Location header
- [ ] 429 responses include Retry-After header
- [ ] CORS headers are configured for browser clients
- [ ] Request body validation returns 422 with field-level errors
