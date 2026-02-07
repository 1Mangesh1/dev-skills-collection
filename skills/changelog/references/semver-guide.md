# Semantic Versioning

## Format: MAJOR.MINOR.PATCH

- **MAJOR** (1.0.0) - Breaking API changes
- **MINOR** (1.2.0) - Backward-compatible new features
- **PATCH** (1.0.1) - Backward-compatible bug fixes

## When to Increment

### MAJOR - Breaking Changes
```
1.0.0 → 2.0.0

- Remove function signatures
- Change database schema (incompatibly)
- Remove deprecated features
- Change API endpoint responses
```

### MINOR - New Features
```
1.2.0 → 1.3.0

- Add new functions
- Add optional parameters
- Add new API endpoints
- Add new configuration options
```

### PATCH - Bug Fixes
```
1.0.0 → 1.0.1

- Fix bugs
- Fix security issues
- Update dependencies (patch versions)
- Improve performance (no API change)
```

## Pre-release Versions

```
1.0.0-alpha      # Early development
1.0.0-beta.1     # Feature complete, testing
1.0.0-rc.1       # Release candidate
1.0.0             # Final release
```

## Build Metadata

```
1.0.0+20130313144700    # Build timestamp
1.0.0+exp.sha.5114f85   # Git commit hash
```

Not considered when determining version precedence.

## Examples

```
0.0.1 → 0.1.0     (First minor version)
1.2.3 → 1.2.4     (Bug fix)
1.2.4 → 1.3.0     (New feature)
1.9.9 → 2.0.0     (Breaking change)
2.0.0-rc.1 → 2.0.0 (Release)
```

## Communication

Before breaking changes:
1. Release with deprecation warnings
2. Document migration path
3. Release major version with clear migration guide
4. Provide examples of old → new code

Example (Node.js):
```javascript
// v3.0.0
const deprecated = require('deprecated');
deprecated('Use newFunction instead');

// v4.0.0
// Function removed entirely
```
