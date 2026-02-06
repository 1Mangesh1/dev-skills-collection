# API Versioning Quick Start

Design API versioning strategies for smooth evolution and backward compatibility.

## Versioning Approaches

### URL Path (Most Common)
```
/api/v1/users
/api/v2/users
```
✅ Clear and explicit
✅ Easy to route
❌ Multiple code paths needed

### Query Parameter
```
GET /api/users?version=1
```
✅ Single endpoint
❌ Less explicit

### Header-Based
```
Accept: application/vnd.api+json;version=2
```
✅ Clean URLs
❌ Less discoverable

## Deprecation Timeline

```
V1 Released ──> Announce V2 (6 months warning)
                  │
                  ├─ V1 in maintenance only
                  └─ V2 in active development
                    │
                    └─> V1 sunset (sunset headers)
```

## Best Practices

1. **Use semantic versioning** - MAJOR.MINOR.PATCH
2. **Provide migration guide** - Help clients upgrade
3. **Deprecation headers** - `Sunset: date` header
4. **Changelog** - Document all changes
5. **Long support window** - 6-12 months per version

## Common Issues

| Problem | Solution |
|---------|----------|
| Breaking changes | Plan deprecation timeline |
| Lost clients | Sunset header + warnings |
| Support burden | Clear migration guides |

## Resources

- [REST Design Guide](https://restfulapi.net/versioning/)
- [Semantic Versioning](https://semver.org/)
- [OpenAPI Specification](https://spec.openapis.org/)

## See Also

- SKILL.md - Detailed patterns and approaches
- metadata.json - References and tools
