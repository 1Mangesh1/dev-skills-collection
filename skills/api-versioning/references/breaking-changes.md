# Breaking vs Non-Breaking Changes

## Non-Breaking (Safe) Changes

- Adding new optional fields
- Adding new endpoints
- Adding new query parameters (optional)
- Adding new response fields
- Adding new endpoints with new paths

Examples:
```json
// v1.0 response
{"id": 1, "name": "Alice"}

// v1.1 response (backwards compatible)
{"id": 1, "name": "Alice", "email": "alice@example.com"}
```

## Breaking Changes

- Removing fields
- Removing endpoints
- Changing field data types
- Making previously optional fields required
- Changing response structure
- Changing HTTP method (GET → POST)

Examples:
```json
// v1.0 response
{"id": 1, "birthday": "1990-01-01"}

// v2.0 response (breaking change - field removed)
{"id": 1}  // birthday field gone
```

## Handling Breaking Changes

1. **Increment MAJOR version**
2. **Maintain old version in parallel** (12+ months)
3. **Document migration path** explicitly
4. **Provide upgrade tools** (migration scripts, adapters)
5. **Communicate timeline** clearly
6. **Support both versions** for grace period

## Version Lifecycle

```
Stable (Active) → Deprecated (Grace Period) → Sunset (Removed)
   18+ months        12 months                 End of support
```
