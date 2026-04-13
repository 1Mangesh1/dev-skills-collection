---
name: changelog
description: Changelog generation, release notes, semantic versioning, and release management. Use when user asks to "write a changelog", "generate release notes", "bump version", "follow conventional commits", "create a release", "update CHANGELOG.md", "write migration guide", "document breaking changes", "set up automated releases", "configure semantic-release", "add deprecation notice", or any versioning, changelog automation, and release documentation tasks.
---

# Changelog & Release Notes

Changelog generation, semantic versioning, automated releases, and release documentation.

## Keep a Changelog Format

Follow keepachangelog.com. Categories in this order:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New user dashboard with analytics

### Changed
- Updated password requirements to 12 characters minimum

### Deprecated
- Legacy /api/v1 endpoints (use /api/v2, removal in 4.0.0)

### Removed
- XML response format (replaced by JSON)

### Fixed
- Fix memory leak in WebSocket handler

### Security
- Update jsonwebtoken to fix CVE-2024-XXXX

## [2.0.0] - 2024-02-01

### Changed
- **BREAKING**: Redesign API response format
- **BREAKING**: Require Node.js 18+

### Removed
- **BREAKING**: Remove XML response format

[Unreleased]: https://github.com/user/repo/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/user/repo/releases/tag/v2.0.0
```

Categories: Added, Changed, Deprecated, Removed, Fixed, Security (in this order). Newest version first. Always keep `[Unreleased]` at top. Use ISO dates (YYYY-MM-DD). Link every version to a diff. Write for humans, not machines.

## Conventional Commits

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

```
feat:     New feature (bumps MINOR)
fix:      Bug fix (bumps PATCH)
docs:     Documentation only
style:    Formatting, no code change
refactor: Code change, no feature/fix
perf:     Performance improvement
test:     Adding/fixing tests
build:    Build system, dependencies
ci:       CI configuration
chore:    Other changes (no src/test)

BREAKING CHANGE: in footer (bumps MAJOR)
feat!: or fix!: breaking change shorthand
```

### Examples

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from payment gateway
docs: update API authentication guide
refactor(db): extract connection pooling to module
perf: optimize image loading with lazy load

feat!: redesign user API endpoints

BREAKING CHANGE: /api/users now returns paginated results.
Migration: wrap existing response handlers with `unwrapPaginated()`.
```

### Multi-paragraph with Footers

```
fix(payments): prevent double-charge on retry

The payment processor was not checking idempotency keys when retries
occurred within the 30-second window. Added key validation before charge.

Fixes: #1234
Reviewed-by: Alice
```

## Semantic Versioning Deep Dive

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (fix: patch release)
1.0.1 → 1.1.0  (feat: minor release, resets patch)
1.1.0 → 2.0.0  (BREAKING CHANGE: major release, resets minor+patch)
```

### Pre-release Versions

```
1.0.0-alpha.1    # Internal testing, unstable API
1.0.0-alpha.2    # Fixes during alpha
1.0.0-beta.1     # Feature-complete, external testing
1.0.0-beta.2     # Beta bugfixes
1.0.0-rc.1       # Release candidate, production-ready intent
1.0.0-rc.2       # RC bugfix
1.0.0            # Stable release

Precedence: 1.0.0-alpha.1 < 1.0.0-beta.1 < 1.0.0-rc.1 < 1.0.0
```

Build metadata (e.g., `1.0.0+build.42`) is ignored for version precedence.

### Version Bump Commands

```bash
# npm
npm version patch                          # 1.0.0 → 1.0.1
npm version minor                          # 1.0.0 → 1.1.0
npm version major                          # 1.0.0 → 2.0.0
npm version prerelease --preid=alpha       # 1.0.0 → 1.0.1-alpha.0
npm version prerelease --preid=beta        # 1.0.1-alpha.0 → 1.0.1-beta.0
npm version prerelease --preid=rc          # → 1.0.1-rc.0

# Python (bump2version)
pip install bump2version
bump2version patch
bump2version minor
bump2version major
```

## Automated Changelog Tools

### conventional-changelog

```bash
npm install -D conventional-changelog-cli

# Generate changelog (append new entries)
npx conventional-changelog -p angular -i CHANGELOG.md -s

# First release (rewrite entire changelog from git history)
npx conventional-changelog -p angular -i CHANGELOG.md -s -r 0
```

### semantic-release

Fully automated: determines version from commits, generates changelog, publishes, creates GitHub release.

```json
// .releaserc.json — install: semantic-release + @semantic-release/{changelog,git}
{
  "branches": ["main", {"name": "beta", "prerelease": true}],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", {"changelogFile": "CHANGELOG.md"}],
    ["@semantic-release/npm", {"npmPublish": true}],
    ["@semantic-release/git", {"assets": ["CHANGELOG.md", "package.json"]}],
    "@semantic-release/github"
  ]
}
```

### Release Please (GitHub Action)

```yaml
name: Release
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node
```

Release Please reads conventional commits, auto-creates a release PR, bumps version, updates CHANGELOG.md, and creates a GitHub release on merge.

### Changesets (Monorepo-friendly)

```bash
npm install -D @changesets/cli
npx changeset init

# Add a changeset (interactive prompt for packages + semver bump)
npx changeset

# Consume changesets: bump versions + update changelogs
npx changeset version

# Publish all changed packages
npx changeset publish
```

### git-cliff

```bash
cargo install git-cliff        # or: npm install -g git-cliff

git cliff -o CHANGELOG.md                # Full changelog
git cliff --latest -o CHANGELOG.md       # Since last tag
git cliff --unreleased --prepend CHANGELOG.md  # Prepend unreleased
git cliff --config cliff.toml            # Custom config
git cliff -o CHANGELOG.md --tag v2.0.0   # Tag unreleased as v2.0.0
```

```toml
# cliff.toml — key sections
[changelog]
header = "# Changelog\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{%- endfor %}
{% endfor %}"""

[git]
conventional_commits = true
commit_parsers = [
    { message = "^feat", group = "Added" },
    { message = "^fix", group = "Fixed" },
    { message = "^perf", group = "Performance" },
]
```

## Changelog vs Release Notes

Changelog (CHANGELOG.md): Complete technical record for developers. Every notable change, every version, kept in repo. Structured by semver category.

Release notes (GitHub Releases / blog): Curated summary for users. Highlights what matters, includes upgrade steps, screenshots, migration info. Written per-release.

```markdown
## Release Notes — v2.1.0

### Highlights
- **OAuth2 Support**: Login with Google and GitHub accounts
- **Performance**: 40% faster API response times

### What's New
- OAuth2 login with Google and GitHub providers
- Rate limiting (100 req/min default, 1000 for authenticated)

### Bug Fixes
- Fixed memory leak in WebSocket connection handler

### Upgrade Guide
npm install myapp@2.1.0 && npx myapp migrate
```

## Writing Good Changelog Entries

Write for the user, not the developer. Describe impact, not implementation.

```markdown
# Bad (commit message style)
- refactor: extract auth middleware to separate module
- fix: add null check to response handler

# Good (user-facing language)
- Improved login reliability when network is intermittent
- Fixed crash when server returns empty response
```

Link issues and PRs for traceability:

```markdown
- Fixed pagination on search results ([#342](https://github.com/org/repo/issues/342))
- Added bulk export for reports ([#401](https://github.com/org/repo/pull/401))
```

## Breaking Changes and Migration Guides

Document every breaking change with: what changed, why, and how to migrate.

```markdown
### Breaking Changes

#### API response format changed
**Before:** Responses returned raw arrays.
**After:** All list endpoints return `{ data: [], meta: { page, total } }`.
**Migration:**
  // Before: const users = await api.getUsers();
  // After:  const { data: users } = await api.getUsers();

#### Minimum Node.js version raised to 20
Update your CI and local environment. Node.js 16 and 18 are no longer supported.
```

## Deprecation Notices

Announce deprecations at least one major version before removal.

```markdown
### Deprecated
- `getUserById()` is deprecated. Use `getUser({ id })` instead. Will be removed in v4.0.0.
- The `/api/v1/reports` endpoint is deprecated. Migrate to `/api/v2/reports` by 2025-01-01.
- The `legacyAuth` config option no longer has effect. Use `auth.provider` instead.
```

Pattern: state what is deprecated, what replaces it, and when it will be removed.

## Monorepo Changelog Strategies

**Per-package changelogs**: Each package gets its own CHANGELOG.md. Tools like Changesets handle this natively. Best when packages are independently versioned and consumed.

**Root changelog**: Single CHANGELOG.md at repo root. Group entries by package with scope prefixes. Works for tightly coupled packages that release together.

**Hybrid**: Root changelog for cross-cutting changes, per-package for package-specific changes.

```markdown
# Root CHANGELOG.md (monorepo)
## [2024-03-15]
### @myorg/api (v2.1.0)
- Added rate limiting on all endpoints
### @myorg/ui (v1.4.0)
- Added dark mode toggle component
### @myorg/shared (v1.2.1)
- Fixed date formatting in non-English locales
```

## GitHub Releases Integration

```bash
gh release create v2.1.0 --generate-notes                          # Auto-generate from PRs/commits
gh release create v2.1.0 --title "v2.1.0" --notes-file notes.md   # Custom notes from file
gh release create v2.1.0-beta.1 --prerelease --title "v2.1.0 Beta" # Pre-release
gh release create v2.1.0 --draft --generate-notes                  # Draft release
gh release upload v2.1.0 dist/*.tar.gz                             # Attach assets
gh release create v2.1.0 --generate-notes --notes-start-tag v2.0.0 # Notes since specific tag
```

## Changelog in CI/CD Pipeline

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0       # Full history for changelog generation

      - name: Generate changelog
        run: npx conventional-changelog -p angular -r 1 -o RELEASE_NOTES.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: RELEASE_NOTES.md
          draft: false
          prerelease: ${{ contains(github.ref, '-beta') || contains(github.ref, '-rc') }}
```

Validate changelog updated in PRs by checking `git diff --name-only origin/main...HEAD` for CHANGELOG.md in a CI step. Fail or warn if missing.
