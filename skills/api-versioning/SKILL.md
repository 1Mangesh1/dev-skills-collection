---
name: api-versioning
description: Comprehensive guide to API versioning strategies, backward compatibility, deprecation, and lifecycle management. Use when user asks about "version API", "API compatibility", "breaking changes", "semantic versioning", "API evolution", "deprecation strategy", "backwards compatibility", "API migration", "version management", "sunset header", "API changelog", "schema versioning", "OpenAPI versioning", "GraphQL versioning", or mentions API lifecycle management, consumer migration, or version negotiation.
---

# API Versioning and Compatibility

Strategies for versioning APIs, managing backward compatibility, handling deprecation, and coordinating version lifecycles across consumers.

## 1. Versioning Approaches

### 1.1 URL Path Versioning

The version identifier is embedded directly in the URL path.

```
GET /api/v1/users
GET /api/v2/users
GET /api/v1/users/42/orders
```

**Pros:**
- Visible in URLs, logs, and documentation at a glance
- Simple to route at the load balancer or gateway level
- Cache-friendly since each version has a distinct URL

**Cons:**
- Duplicates routes per version; every resource must be replicated
- Encourages large, sweeping version bumps rather than incremental changes
- Clients must update hardcoded URLs when migrating
- Violates the REST principle that a URI should identify a resource, not a representation version

**When to use:** Public APIs with external consumers. Stripe uses `/v1/`, Google Cloud uses `/v1/` and `/v2/`.

### 1.2 Header Versioning

```
Accept: application/vnd.mycompany.users.v2+json    # content negotiation
X-API-Version: 2                                     # custom header
```

**Pros:**
- URLs remain stable and resource-oriented
- Supports fine-grained versioning per resource or operation

**Cons:**
- Less discoverable; version is not visible in the URL
- Harder to test in a browser or with simple curl commands
- Caching proxies may not vary on custom headers by default

**When to use:** Internal APIs or where URL stability matters. GitHub uses `Accept: application/vnd.github.v3+json`.

### 1.3 Query Parameter Versioning

```
GET /api/users?version=2
```

**Pros:**
- Easy to add to existing APIs without restructuring routes
- Simple to override during testing or debugging

**Cons:**
- Pollutes the query string with infrastructure concerns
- Complicates caching because query strings affect cache keys unpredictably
- Harder to enforce at the routing layer

**When to use:** Internal tooling or debugging fallback. Rarely the best choice for production APIs.

## 2. Semantic Versioning for APIs

Semver uses `MAJOR.MINOR.PATCH`:
- **MAJOR** (v1 to v2): Breaking changes requiring consumer updates
- **MINOR** (v1.1 to v1.2): Backward-compatible new features
- **PATCH** (v1.1.0 to v1.1.1): Backward-compatible bug fixes

For URL versioning, only MAJOR appears in the path (`/v1/`). Communicate MINOR/PATCH through changelogs or response headers (`X-API-Version: 2.3.1`).

## 3. Breaking vs Non-Breaking Changes

**Breaking changes** (require new major version):
- Removing or renaming a field in request or response
- Changing a field's type (string to integer)
- Removing an endpoint or changing its HTTP method
- Making a previously optional field required
- Changing authentication requirements, error formats, or pagination structure
- Removing an enum value consumers depend on

**Non-breaking changes** (safe within current version):
- Adding new optional request fields, response fields, endpoints, or query parameters
- Adding new enum values (if consumers handle unknowns gracefully)
- Relaxing validation constraints; adding response headers

**Gray area:** Changing default values, adding required fields with defaults, changing rate limits, modifying field order in JSON.

## 4. Deprecation Strategies

### Sunset and Deprecation Headers

Use the `Sunset` header (RFC 8594) with a `Deprecation` header and migration link:

```
Deprecation: true
Sunset: Sat, 01 Mar 2025 00:00:00 GMT
Link: <https://api.example.com/docs/migration-v3>; rel="successor-version"
```

### Deprecation Practices

- Mark deprecated fields/endpoints in OpenAPI specs with `deprecated: true`
- Log usage of deprecated endpoints to track remaining consumers
- Ship migration guides with every major bump: breaking changes list, before/after examples, timeline, support contacts

### Typical Timeline

```
Month 0:  Announce deprecation. New version available.
Month 3:  Notify all known consumers with migration guide.
Month 6:  Warning headers on every old-version request.
Month 9:  Reduce SLA to best-effort for deprecated version.
Month 12: Remove deprecated version. Return 410 Gone.
```

Public APIs with many external consumers may need 18-24 months.

## 5. Version Lifecycle Management

Maintain at most two to three active major versions. Define clear states:

| State      | Description                                                          |
|------------|----------------------------------------------------------------------|
| Preview    | Available for testing, may change without notice                     |
| Active     | Fully supported, recommended for new integrations                    |
| Deprecated | Functional but scheduled for removal, no new features                |
| Retired    | Returns 410 Gone with pointer to successor                          |

**Default version behavior** when consumer omits version: fixed default (predictable but can strand users), latest stable (risky for unexpected breaks), or require explicit version (safest but adds friction).

## 6. API Changelog Patterns

Maintain structured, machine-readable changelogs:

```json
{
  "version": "2.3.0",
  "date": "2025-01-15",
  "changes": [
    { "type": "added", "endpoint": "GET /v2/users/{id}/preferences", "description": "Retrieve user preferences" },
    { "type": "deprecated", "endpoint": "GET /v2/users/{id}/settings", "description": "Use /preferences. Sunset: 2025-07-15" }
  ]
}
```

Categorize entries as: added, changed, deprecated, removed, fixed, security. Link to migration docs for breaking changes. Publish changelogs in documentation and as an API endpoint.

## 7. Backward Compatibility Patterns

**Additive changes only:** The safest evolution strategy is to only add, never remove or rename:

```json
// v1 response (original)
{ "name": "Alice", "email": "alice@example.com" }

// v1 response after additive change (still v1, non-breaking)
{ "name": "Alice", "email": "alice@example.com", "phone": "+1-555-0100" }
```

**Optional fields with defaults:** New request fields must be optional with sensible defaults so existing clients are unaffected. For example, a new `role` field defaults to `"member"` when omitted.

**Response envelope stability:** Keep the top-level response structure (`data`, `meta`, `errors`) consistent across all changes within a version. Consumers build deserialization logic around this structure.

**Tolerant reader pattern:** Encourage consumers to ignore unknown fields, avoid depending on field ordering, and handle missing optional fields gracefully. Document this expectation in your API guidelines.

## 8. Database Schema Versioning

API version changes often require schema changes. Strategies for coexisting versions:

- **Expand-and-contract:** Add new columns first, migrate data, update the API, then remove old columns.
- **Database views:** Versioned views present data in the shape each API version expects while underlying tables evolve.
- **Migration sequencing:** Apply migrations in order that supports both old and new API simultaneously.

**Key rules:**
- Never drop a column while any active API version still reads from it
- Use feature flags to control which API version writes to new columns
- Test rollback scenarios: can you revert the API version without a database rollback?
- Coordinate migration timing with deployment: schema changes must be deployed before the API code that depends on them

## 9. OpenAPI/Swagger Versioning

Maintain separate spec files per major version (`openapi-v1.yaml`, `openapi-v2.yaml`). Mark deprecated operations:

```yaml
paths:
  /v1/users/{id}/settings:
    get:
      deprecated: true
      summary: Get user settings (use /preferences instead)
      x-sunset: "2025-07-15"
```

Use tools like `oasdiff` or `openapi-diff` in CI to detect breaking changes between spec versions automatically.

## 10. Real-World Examples

### REST Endpoint Evolution

```
# v1 original
GET /api/v1/users/42 -> { "id": 42, "name": "Alice", "email": "alice@example.com" }

# v1 additive (non-breaking)
GET /api/v1/users/42 -> { "id": 42, "name": "Alice", "email": "alice@example.com", "created_at": "2024-01-15T10:00:00Z" }

# v2 restructured (breaking: name split)
GET /api/v2/users/42 -> { "id": 42, "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com" }
```

### GraphQL Schema Evolution

GraphQL avoids URL versioning. Evolve additively with built-in deprecation:

```graphql
type User {
  id: ID!
  name: String! @deprecated(reason: "Use firstName and lastName")
  firstName: String!
  lastName: String!
  email: String!
}
```

Monitor field usage analytics to determine when deprecated fields can be removed safely.

## 11. Common Mistakes

- **Versioning too early:** Do not create v2 until you have an actual breaking change. Use additive changes within v1 as long as possible.
- **Too many active versions:** Four or more active major versions signals deprecation is too slow or breaking changes are too frequent.
- **Inconsistent versioning:** Mixing URL versioning for some endpoints and header versioning for others confuses consumers.
- **Treating minor changes as major:** Adding fields or endpoints does not need a major bump. Over-incrementing dilutes version meaning.
- **No version discovery:** Provide a discovery endpoint or include version info in response headers.

## 12. Migration Tooling and Consumer Communication

**Tooling:**
- Codemods/scripts to rewrite consumer code automatically (Stripe and Facebook invest heavily here)
- Adapter layers that translate v1 requests to v2 format internally
- Versioned client SDKs with clear upgrade instructions
- Sandbox environments for pre-migration testing

**Communication:**
- Changelog emails or webhooks to registered consumers
- Developer portal announcements
- API usage dashboards showing which deprecated endpoints a consumer still calls
- Direct outreach for high-traffic consumers

**Tracking migration progress:**

Monitor the percentage of traffic still hitting deprecated versions. Use this data to:

- Identify consumers who need targeted outreach
- Decide whether to extend or enforce sunset deadlines
- Justify the cost of maintaining old versions to stakeholders
- Set data-driven go/no-go decisions for version retirement

## References

- RFC 8594: The Sunset HTTP Header Field
- Semantic Versioning specification (semver.org)
- OpenAPI Specification (spec.openapis.org)
- Stripe API versioning documentation
- GitHub API versioning approach
- Google Cloud API design guide: Compatibility section
