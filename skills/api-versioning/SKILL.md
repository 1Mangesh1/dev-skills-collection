---
name: api-versioning
description: API versioning strategies and backward compatibility patterns. Use when user asks to "version API", "API compatibility", "breaking changes", "semantic versioning", "API evolution", "deprecation strategy", "backwards compatibility", "API migration", "version management", or mentions API lifecycle management and compatibility.
---

# API Versioning & Compatibility

Strategies for managing API versions, backward compatibility, and graceful deprecation.

## Versioning Approaches

### URL Path Versioning
```
/api/v1/users
/api/v2/users
```

### Query Parameter Versioning
```
GET /api/users?version=1
GET /api/users?version=2
```

### Header Versioning
```
Accept: application/vnd.api+json;version=1
```

### Content Negotiation
```
Accept: application/vnd.myapi.v2+json
```

## Best Practices

1. **Semantic Versioning** - Use MAJOR.MINOR.PATCH
2. **Deprecation Warnings** - Include deprecation headers
3. **Sunset Headers** - Specify when API versions expire
4. **Changelog** - Document all changes
5. **Migration Guides** - Help clients upgrade
6. **Compatibility Layer** - Support multiple versions temporarily

## Breaking Changes Strategy

- Plan deprecation timeline (6-12 months notice)
- Provide migration documentation
- Offer tool-assisted migration (scripts, adapters)
- Support parallel versioning
- Communicate clearly in changelogs

## References

- Semantic Versioning (semver.org)
- REST API Design Guidelines
- OpenAPI/Swagger Specification
