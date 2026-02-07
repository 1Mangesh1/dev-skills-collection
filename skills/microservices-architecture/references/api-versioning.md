# API Versioning Strategies

## Why API Versioning Matters

In microservices, APIs are contracts between services. Managing versions ensures:
- Backward compatibility
- Smooth deprecation of features
- Multiple client support
- Breaking change communication

## Versioning Strategies

### 1. URL Path Versioning

Most explicit approach:

```
GET /api/v1/users/123
GET /api/v2/users/123
```

**Implementation:**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# V1 endpoint
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    return jsonify({
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    })

# V2 endpoint - more fields, different structure
@app.route('/api/v2/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    return jsonify({
        'id': user_id,
        'profile': {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1-555-0100'
        },
        'created_at': '2023-01-15T10:30:00Z',
        'updated_at': '2024-02-07T14:20:00Z'
    })

# Route to appropriate version
@app.before_request
def log_api_version():
    if request.path.startswith('/api/v1'):
        print(f"Using API v1 endpoint: {request.path}")
    elif request.path.startswith('/api/v2'):
        print(f"Using API v2 endpoint: {request.path}")
```

**Pros:**
- Explicit and clear
- Easy to maintain multiple versions
- Good for tracking deprecated versions

**Cons:**
- URL explosion as versions accumulate
- Client code depends on URL structure

### 2. Header-Based Versioning

Version specified in Accept/Custom header:

```
GET /api/users/123
Accept: application/vnd.company.v1+json

GET /api/users/123
Accept: application/vnd.company.v2+json
```

**Implementation:**

```python
from functools import wraps

def api_version_required(version):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            accept_header = request.headers.get('Accept', '')
            
            # Parse version from Accept header
            if f'vnd.company.v{version}' not in accept_header:
                return {
                    'error': f'This endpoint requires version v{version}'
                }, 406  # Not Acceptable
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/api/users/<int:user_id>', methods=['GET'])
@api_version_required(1)
def get_user_v1(user_id):
    return jsonify({'id': user_id, 'name': 'John Doe'})

@app.route('/api/users/<int:user_id>', methods=['GET'])
@api_version_required(2)
def get_user_v2(user_id):
    return jsonify({
        'id': user_id,
        'profile': {'first_name': 'John', 'last_name': 'Doe'}
    })
```

**Pros:**
- Cleaner URLs
- Version info in metadata
- Can support multiple versions simultaneously

**Cons:**
- Less obvious to clients
- Requires proper header handling

### 3. Media Type Versioning

Version in Content-Type:

```
GET /api/users/123
Accept: application/vnd.company.user+json; version=1

GET /api/users/123
Accept: application/vnd.company.user+json; version=2
```

**Implementation:**

```python
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    accept = request.headers.get('Accept')
    
    # Extract version
    version = 1
    if 'version=' in accept:
        version = int(accept.split('version=')[1].split(',')[0])
    
    if version == 1:
        return jsonify({'id': user_id, 'name': 'John Doe'})
    elif version == 2:
        return jsonify({
            'id': user_id,
            'profile': {'first_name': 'John', 'last_name': 'Doe'}
        })
```

## Handling Breaking Changes

### Graceful Deprecation

```python
import warnings
from datetime import datetime, timedelta

deprecated_date = datetime(2024, 6, 30)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    response = jsonify({'id': user_id, 'name': 'John Doe'})
    
    # Add deprecation headers
    days_left = (deprecated_date - datetime.now()).days
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = deprecated_date.isoformat()
    response.headers['Warning'] = (
        f'299 - "v1 API deprecated, use v2. '
        f'Will be removed in {days_left} days"'
    )
    
    return response
```

### API Version Timeline

```
v1 (2022-01-01) ─── Active ──────── Deprecated (2024-01-01) ─── Sunset (2024-06-30)
                           │
v2 (2023-06-01) ─── Launch ──────── Active ──────────────────────── Active
                           │
v3 (Planned Q3) ─── Development ─── Beta Testing ─ Public Release ─ Active
```

## Backward Compatibility Strategies

### 1. Additive Changes (Always Safe)

Add new fields without removing old ones:

```python
# v1 response
def get_user_v1(user_id):
    return {
        'id': user_id,
        'name': 'John Doe'
    }

# v2: Added email (backward compatible addition)
def get_user_v2(user_id):
    return {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'  # New field
    }

# v3: Make response more flexible, old fields still present
def get_user_v3(user_id):
    return {
        'id': user_id,
        'name': 'John Doe',  # Still here for v1 clients
        'email': 'john@example.com',  # Still here for v2 clients
        'profile': {  # New structure
            'full_name': 'John Doe',
            'contact': {
                'email': 'john@example.com',
                'phone': '+1-555-0100'
            }
        }
    }
```

### 2. Using Wrappers for Legacy Fields

```python
def get_user_v3_response(user):
    response = {
        'id': user.id,
        'profile': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
    }
    
    # For backward compatibility with v1/v2 clients
    response['name'] = f"{user.first_name} {user.last_name}"
    response['email'] = user.email
    
    return response
```

### 3. Field Aliasing

Accept multiple naming conventions:

```python
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(required=True)
    
    # Modern name
    first_name = fields.Str(required=True)
    
    # Legacy name for backward compatibility
    firstName = fields.Str(load_only=True, data_key='firstName')
    
    class Meta:
        # Accept both camelCase and snake_case
        load_fields = {
            'firstName': 'first_name'
        }
```

## Version Sunset and Migration

### Migration Helper Endpoint

```python
@app.route('/api/v1/users/<int:user_id>/migrate', methods=['GET'])
def migrate_endpoint_help(user_id):
    """Provides migration instructions"""
    return jsonify({
        'deprecated_endpoint': f'/api/v1/users/{user_id}',
        'new_endpoint': f'/api/v2/users/{user_id}',
        'migration_guide': 'https://docs.company.com/api-migration-v1-to-v2',
        'changes': [
            {
                'field': 'name',
                'v1_type': 'string',
                'v2_location': 'profile.first_name + profile.last_name',
                'example': 'Use split() on v1 name or fetch separately'
            },
            {
                'field': 'email',
                'v1_type': 'string',
                'v2_location': 'profile.contact.email',
                'example': 'Direct mapping with nested structure'
            }
        ],
        'deprecated_on': '2024-01-01',
        'sunset_date': '2024-06-30'
    })
```

## Version Communication Strategy

### OpenAPI Documentation with Versions

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: User Service API
  version: 2.0.0
  x-api-lifecycle:
    deprecated: false
    sunset-date: "2025-12-31"

paths:
  /api/v1/users/{userId}:
    deprecated: true
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: integer
      - name: X-Deprecation-Warning
        in: header
        deprecated: true
    get:
      summary: Get user (V1 - DEPRECATED)
      x-sunset-date: "2024-06-30"
      x-migration-url: /api/v2/users/{userId}

  /api/v2/users/{userId}:
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: integer
    get:
      summary: Get user (V2 - CURRENT)
```

## Best Practices

1. **Plan ahead**: Design APIs thinking about future versions
2. **Minimize versions**: Don't create versions for minor changes
3. **Clear communication**: Announce deprecations well in advance
4. **Test compatibility**: Verify old clients still work after server update
5. **Monitor usage**: Track which API versions clients are using
6. **Provide tooling**: Offer migration helpers and documentation
