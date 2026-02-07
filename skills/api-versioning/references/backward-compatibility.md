# Backward Compatibility

## Principles

### Additive Changes (Safe)
- Add new optional fields
- Add new endpoints
- Add new query parameters with defaults
- Add new headers with sensible defaults

### Breaking Changes (Unsafe)
- Remove fields/endpoints
- Rename fields
- Change field types
- Change response structure
- Change HTTP status codes

## Compatibility Patterns

### Pattern 1: Field Aliasing
Support both old and new field names:
```json
{
  "userId": 123,           // new
  "user_id": 123           // old (deprecated)
}
```

### Pattern 2: Wrapper Fields
Add new structure without breaking old format:
```json
{
  "data": {                // new structure
    "id": 123,
    "name": "Alice"
  },
  "user": {                // old structure (deprecated)
    "id": 123,
    "name": "Alice"
  }
}
```

### Pattern 3: Feature Flags
Use feature flags to control behavior:
```
GET /api/v1/users?new_format=true
```

## Testing for Compatibility

```python
# Test that old clients still work
def test_v1_client_compatibility():
    response = get("/api/v2/users", headers={"Accept": "application/vnd.api+json;version=1"})
    assert response.status == 200
    assert "userId" in response.json()  # old format
```

## Migration Path

1. Release with both formats
2. Document old format as deprecated
3. Set sunset date (6-12 months out)
4. Provide migration tool/script
5. One month before sunset: final warning
6. Remove old format after sunset
