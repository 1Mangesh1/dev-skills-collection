# Semantic Versioning Guide

## Version Numbering Scheme
```
X.Y.Z
│ │ └─── PATCH (bug fixes, backward compatible)
│ └───── MINOR (new features, backward compatible)
└─────── MAJOR (breaking changes)
```

## When to Increment Versions

### Major (X.0.0)
- Breaking API changes
- Removed features
- Major refactoring
- Incompatible database migrations

### Minor (Y.0)
- New features
- New API endpoints
- New configuration options
- Backward compatible enhancements

### Patch (.Z)
- Bug fixes
- Performance improvements
- Documentation updates
- Security patches

## Pre-release and Build Metadata
```
1.0.0-alpha.1       # Alpha release
1.0.0-beta.2        # Beta release
1.0.0-rc.1          # Release candidate
2.0.0+20130313144700 # Build metadata
```

## Version Lifecycle
```
1.0.0-alpha → 1.0.0-beta → 1.0.0-rc → 1.0.0 (stable)
                                    ↓
                              1.0.1 (patch)
                                    ↓
                              1.1.0 (minor)
                                    ↓
                              2.0.0 (major)
```

## Examples

### Correct Version Progression
```
1.0.0       - Initial release
1.0.1       - Bug fix
1.1.0       - New feature
1.1.1       - Bug fix
2.0.0       - Breaking change
2.0.1       - Bug fix
2.1.0       - New feature
3.0.0       - Major overhaul
```

### Incorrect Examples
```
1.0         - Missing patch version (use 1.0.0)
1.0.0.1     - Too many version numbers
v1.0.0      - Don't include 'v' prefix in code
1.0-alpha   - Missing pre-release format (use 1.0.0-alpha)
```

## References
- [Official Semantic Versioning Spec](https://semver.org/)
