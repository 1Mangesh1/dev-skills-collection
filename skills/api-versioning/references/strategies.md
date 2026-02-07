# API Versioning Strategies Reference

## Overview

Choosing the right versioning strategy depends on your API maturity, client diversity, and breaking changes frequency.

## Strategy Comparison

### 1. URL Path Versioning
**Example:** `/api/v1/users` vs `/api/v2/users`

**Pros:**
- Very explicit and discoverable
- Easy to route to different handlers
- Clear in documentation
- Browser-friendly (can visit in browser)

**Cons:**
- Duplicate code paths
- More endpoints to maintain
- Bulkier URLs

**When to use:** Public APIs, multiple concurrent versions, clear deprecation path

### 2. Query Parameter Versioning
**Example:** `GET /api/users?version=1`

**Pros:**
- Single endpoint
- Less URL pollution
- Easy to test

**Cons:**
- Less discoverable
- Easy to forget the parameter
- Not truly RESTful

**When to use:** Internal APIs, simple versioning needs

### 3. Header-Based Versioning
**Example:** `Accept: application/vnd.api+json;version=1`

**Pros:**
- Clean URLs
- Very "RESTful"
- Flexible

**Cons:**
- Not discoverable (can't see in browser)
- Clients often forget headers
- More complex routing

**When to use:** GraphQL-like APIs, microservices

### 4. Subdomain Versioning
**Example:** `https://v1.api.example.com/users`

**Pros:**
- Complete separation
- Different infrastructure possible

**Cons:**
- Complex certificate management
- More infrastructure overhead

**When to use:** Major architectural differences between versions

## Decision Matrix

| Factor | URL Path | Query | Header | Subdomain |
|--------|----------|-------|--------|-----------|
| Discoverability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Implementation | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| RESTfulness | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Simplicity | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

## Best Practices

1. **Plan for the Future**
   - Design APIs expecting you'll need versions
   - Add versioning from day one

2. **Long Deprecation Timelines**
   - 6-12 months minimum
   - More for widely-used APIs
   - Announce well in advance

3. **Sunset Headers**
   - Include `Sunset: date` header
   - Include `Deprecation: true` header
   - Include `Link: <new-url>; rel="successor-version"`

4. **Documentation**
   - Clear migration guide for each version change
   - Changelog with what changed
   - Side-by-side examples

5. **Monitoring**
   - Track v1 usage over time
   - Alert on deprecated endpoint usage
   - Identify migration blockers

## Semantic Versioning

Use MAJOR.MINOR.PATCH for API versions:
- **MAJOR**: Breaking changes (requires new version path)
- **MINOR**: Backward-compatible additions
- **PATCH**: Bug fixes

## Example Timeline

```
v2.0 Released → v2.1 (added fields) → v2.2 (bug fix) → v3.0 (breaking) → ...
↑ Now supported
v1.0 Released → v1.1 → v1.2 → Maintenance → Deprecated → Sunset
                                  ↑ 6mo             ↑ 12mo
```
