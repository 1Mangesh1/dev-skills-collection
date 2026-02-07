# Keep a Changelog

## Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-15

### Added
- New user authentication system
- Dark mode support
- Export to CSV feature

### Changed
- Updated dependencies to latest versions
- Improved search performance by 40%
- Refactored database queries

### Fixed
- Fixed memory leak in socket handler
- Corrected typos in documentation
- Resolved race condition in API

### Removed
- Old login system (replaced by new auth)
- Deprecated API endpoints (/v1/users)

### Deprecated
- OAuth 1.0 support (use OAuth 2.0)
- Flash-based file uploader

### Security
- Added CSRF protection
- Updated password hashing algorithm

## [1.0.0] - 2023-11-01

### Added
- Initial release
- User management
- Basic reporting
```

## Best Practices

1. **Update on every release** - Not after
2. **Use semantic versioning** - MAJOR.MINOR.PATCH
3. **Group changes** - Features, fixes, breaking changes, deprecations
4. **Be descriptive** - Why changed, not just what
5. **Link to PRs/Issues** - Help users find context
6. **Unreleased section** - Track upcoming changes

## Unreleased Section

Keep track of changes before release:

```markdown
## [Unreleased]

### Added
- New payment method support
- API rate limiting

### Changed
- Improved email templates

### Fixed
- Rare bug in calculation engine
```

## Conventional Commits

Generate autmatically from commits:
- `feat: ...` → Added section
- `fix: ...` → Fixed section
- `BREAKING CHANGE:` → Breaking changes section
