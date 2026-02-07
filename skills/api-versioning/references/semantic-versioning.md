# Semantic Versioning for APIs

## Version Format: MAJOR.MINOR.PATCH

### MAJOR (Breaking Changes)
- Removed endpoints
- Changed field types
- Renamed parameters  
- Changed response structure
- Example: 1.0.0 → 2.0.0

### MINOR (New Features, Backwards Compatible)
- New endpoints
- New optional fields
- New query parameters
- Example: 1.0.0 → 1.1.0

### PATCH (Bug Fixes, Backwards Compatible)
- Bug fixes
- Performance improvements
- Documentation updates
- Example: 1.0.0 → 1.0.1

## Deprecation Policy Example

```
Version 1.0.0 Released
  ↓ (6 months)
Version 2.0.0 Released + v1.0 deprecation announcement
  ↓ (6 months)
v1.0 endpoints return HTTP 410 Gone + sunset header
  ↓ (6 months)
v1.0 completely removed
```

## Response Headers for Versioning

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 30 Jun 2025 23:59:59 GMT
API-Version: 1.0.0
Warning: 299 - "API v1 deprecated. Use v2"
```

## Best Practices

1. **Plan ahead** - Version strategy before launch
2. **Communicate early** - Announced deprecations 6+ months out
3. **Provide tools** - Migration scripts, adapters
4. **Support duration** - Guarantee support for at least 12 months
5. **Clear documentation** - Show what changed and why
