---
name: pnpm
description: pnpm package manager for fast, disk-efficient dependency management and workspaces. Use when user mentions "pnpm", "pnpm install", "pnpm workspace", "pnpm-workspace.yaml", "pnpm add", "pnpm store", "pnpm dlx", "content-addressable store", or managing Node.js packages with pnpm.
---

# pnpm

Fast, disk-efficient package manager for Node.js.

## Installation

```bash
# Via corepack (recommended, ships with Node.js 16.13+)
corepack enable
corepack prepare pnpm@latest --activate

# Standalone script
curl -fsSL https://get.pnpm.io/install.sh | sh -

# Via npm
npm install -g pnpm

# Via Homebrew
brew install pnpm
```

## Why pnpm

**Content-addressable store** -- pnpm stores every package version exactly once in a global store. Projects hard-link to the store, so the same dependency across ten projects uses disk space only once.

**Strict node_modules** -- pnpm creates a non-flat `node_modules`. Packages can only access dependencies they explicitly declare. This prevents phantom dependencies that work by accident through hoisting.

**Speed** -- hard linking avoids redundant downloads and copies. Parallel resolution makes installs consistently faster than npm.

## Basic Commands

```bash
pnpm install                  # Install all dependencies from lockfile
pnpm add lodash               # Add a production dependency
pnpm add -D typescript        # Add a dev dependency
pnpm add -g vercel            # Add globally
pnpm add lodash@4.17.21       # Specific version
pnpm remove lodash            # Remove a dependency
pnpm update                   # Update within semver ranges
pnpm update --latest          # Update to latest, ignoring ranges
pnpm dlx create-next-app@latest  # Run a package without installing
```

## pnpm vs npm vs yarn

| Action             | pnpm              | npm                | yarn              |
|--------------------|--------------------|--------------------|-------------------|
| Install all        | `pnpm install`     | `npm install`      | `yarn`            |
| Add dependency     | `pnpm add pkg`     | `npm install pkg`  | `yarn add pkg`    |
| Add dev dep        | `pnpm add -D pkg`  | `npm install -D pkg` | `yarn add -D pkg` |
| Remove             | `pnpm remove pkg`  | `npm uninstall pkg` | `yarn remove pkg` |
| Run script         | `pnpm run dev`     | `npm run dev`      | `yarn dev`        |
| Execute binary     | `pnpm dlx pkg`     | `npx pkg`          | `yarn dlx pkg`    |
| Update             | `pnpm update`      | `npm update`       | `yarn up`         |
| Audit              | `pnpm audit`       | `npm audit`        | `yarn audit`      |
| Why installed      | `pnpm why pkg`     | `npm why pkg`      | `yarn why pkg`    |

## Workspaces

### pnpm-workspace.yaml

```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

### Filtering

```bash
pnpm --filter web run build          # By package name
pnpm --filter "./apps/*" run build   # By path glob
pnpm --filter web... run build       # Package and its dependencies
pnpm --filter ...web run build       # Package and its dependents
pnpm -r run build                    # All workspace packages
pnpm -r --parallel run build         # All in parallel
```

### Workspace protocol

Reference sibling packages with `workspace:` in `package.json`:

```json
{
  "dependencies": {
    "@myorg/shared": "workspace:*",
    "@myorg/utils": "workspace:^1.0.0"
  }
}
```

On publish, pnpm replaces `workspace:*` with the actual version. `workspace:^` and `workspace:~` produce the corresponding semver range.

## Monorepo Patterns

### Shared dependencies

Place shared dev dependencies in the workspace root. Use `-w` to add them:

```bash
pnpm add -Dw typescript eslint prettier
```

### Peer dependencies

```ini
# .npmrc
auto-install-peers=true
strict-peer-dependencies=false
```

## .npmrc Configuration

```ini
shamefully-hoist=true                    # Flat node_modules (compatibility)
auto-install-peers=true                  # Auto-install peer deps
strict-peer-dependencies=false           # Warn instead of error on peer mismatches
enable-pre-post-scripts=true             # Run pre/post lifecycle scripts
use-node-version=20.11.0                 # Pin Node.js version
registry=https://registry.npmjs.org/
@myorg:registry=https://npm.pkg.github.com
public-hoist-pattern[]=*eslint*          # Hoist specific packages only
public-hoist-pattern[]=*prettier*
store-dir=/path/to/custom/store          # Custom store location
```

## Lock File

pnpm uses `pnpm-lock.yaml`. In monorepos it contains an `importers` section with per-package snapshots:

```yaml
importers:
  apps/web:
    dependencies:
      react:
        specifier: ^18.2.0
        version: 18.2.0
    devDependencies:
      typescript:
        specifier: ^5.3.0
        version: 5.3.3
```

Always commit `pnpm-lock.yaml`. Use `--frozen-lockfile` in CI.

## Patching Dependencies

```bash
pnpm patch express@4.18.2               # Opens temp dir with package source
# Edit files, then:
pnpm patch-commit /tmp/patch-dir-xxxxx  # Generates patch file
```

This adds a `patchedDependencies` entry to `package.json`:

```json
{
  "pnpm": {
    "patchedDependencies": {
      "express@4.18.2": "patches/express@4.18.2.patch"
    }
  }
}
```

Commit the `patches/` directory.

## Overrides

Force dependency versions across the entire tree:

```json
{
  "pnpm": {
    "overrides": {
      "lodash": "^4.17.21",
      "got@<11.8.5": ">=11.8.5",
      "express>debug": "~4.3.0"
    }
  }
}
```

Use overrides to fix transitive vulnerabilities or force version alignment.

## Scripts

```bash
pnpm run dev                         # Run script from package.json
pnpm dev                             # Shorthand (no conflict with pnpm commands)
pnpm --filter web run build          # Run in specific package
pnpm -r run test                     # Run in all workspace packages
pnpm -r --parallel run lint          # Parallel across packages
```

pnpm does not run `pre`/`post` scripts by default. Enable with `enable-pre-post-scripts=true` in `.npmrc`.

## Store Management

```bash
pnpm store path                      # Print global store location
pnpm store prune                     # Remove unreferenced packages
pnpm store status                    # Check for modified packages
pnpm install --offline               # Install from store only (no network)
```

## Publishing from a Workspace

```bash
pnpm -r publish --access public      # Publish all public packages
pnpm -r publish --dry-run            # Dry run first
pnpm --filter "./packages/*" publish # Publish subset
```

pnpm replaces `workspace:` references with real version numbers during publish.

## CI/CD

```yaml
# GitHub Actions
- uses: pnpm/action-setup@v4
  with:
    version: 9

- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'pnpm'

- run: pnpm install --frozen-lockfile
- run: pnpm -r run build
- run: pnpm -r run test
```

`--frozen-lockfile` fails if `pnpm-lock.yaml` is out of date, preventing accidental lockfile changes.

For generic CI, cache the directory from `pnpm store path` between builds.

## Migration from npm/yarn

```bash
# From npm
rm -rf node_modules package-lock.json
pnpm import           # Reads package-lock.json if present
pnpm install

# From yarn
rm -rf node_modules yarn.lock
pnpm import           # Reads yarn.lock if present
pnpm install
```

After migrating: replace `npm ci` / `yarn --frozen-lockfile` with `pnpm install --frozen-lockfile` in CI. Add `pnpm-workspace.yaml` if the project uses workspaces.
