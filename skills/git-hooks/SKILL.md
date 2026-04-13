---
name: git-hooks
description: Git hooks setup with Husky, lint-staged, lefthook, and native hooks for automated code quality. Use when user asks to "setup pre-commit hooks", "add husky", "lint on commit", "format before commit", "run tests on push", "setup git hooks", "validate commit messages", "enforce conventional commits", "detect secrets in commits", "configure lefthook", "share git hooks", "core.hooksPath", "hook bypass", "debug git hooks", or automate code quality checks.
---

# Git Hooks

Automate code quality, enforce conventions, and prevent bad commits with Git hooks.

## Hook Types and Use Cases

```
Hook                  Trigger                        Common Use
─────────────────────────────────────────────────────────────────
pre-commit            Before commit is created        Lint, format, secret scan
prepare-commit-msg    After default msg, before edit  Add ticket ID, template
commit-msg            After user writes message       Enforce conventional commits
pre-push              Before push to remote           Full test suite, build check
pre-rebase            Before rebase starts            Prevent rebase on protected branches
post-merge            After merge completes           Reinstall deps, run migrations
post-checkout         After checkout/switch           Rebuild, clear caches
```

## Husky v9 (Node.js Projects)

```bash
# Install and initialize
npm install -D husky
npx husky init
# Creates .husky/ directory with pre-commit hook
# Adds "prepare": "husky" to package.json

# Create hooks — each is a plain shell script
echo "npx lint-staged" > .husky/pre-commit
echo "npm test" > .husky/pre-push
echo 'npx --no -- commitlint --edit "$1"' > .husky/commit-msg

# v9 key differences from v8:
# - No husky.sh sourcing needed — hooks are plain scripts
# - Uses core.hooksPath internally via "prepare" script
# - If hooks don't run after clone: npm run prepare
```

## lint-staged Configuration

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml,yaml}": "prettier --write",
    "*.css": ["stylelint --fix", "prettier --write"],
    "*.py": ["ruff check --fix", "ruff format"],
    "*.go": ["gofmt -w", "go vet ./..."]
  }
}
```

### Advanced lint-staged (Function Config)

```js
// lint-staged.config.mjs
export default {
  // Run tsc on whole project when any TS file changes
  '*.ts': () => 'tsc --noEmit',
  // Pass filenames explicitly
  '*.{js,ts}': (filenames) => [
    `eslint --fix ${filenames.join(' ')}`,
    `prettier --write ${filenames.join(' ')}`,
  ],
  // Run related tests only
  'tests/**/*.ts': 'jest --findRelatedTests',
}
```

## Lefthook (Modern Alternative)

```bash
npm install -D lefthook    # or: brew install lefthook
npx lefthook install
```

```yaml
# lefthook.yml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{js,ts,tsx}"
      run: npx eslint --fix {staged_files}
    format:
      glob: "*.{js,ts,tsx,json,md}"
      run: npx prettier --write {staged_files}
    types:
      glob: "*.{ts,tsx}"
      run: npx tsc --noEmit

commit-msg:
  commands:
    validate:
      run: 'echo "{1}" | npx commitlint --config .commitlintrc.yml'

pre-push:
  commands:
    test:
      run: npm test
```

Lefthook advantages: YAML config, built-in parallel execution, glob filtering,
`{staged_files}` variable, Go binary (no Node dependency), native monorepo `root:` support.

## Pre-commit Framework (Python/Polyglot)

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```

```bash
pre-commit run --all-files       # Run all hooks on all files
pre-commit autoupdate            # Update hook versions
```

## Custom Hook Scripts

### Conventional Commits Enforcement

```bash
#!/bin/sh
# .husky/commit-msg  OR  .githooks/commit-msg
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?(!)?: .{1,72}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "ERROR: Invalid commit message format."
  echo "Expected: type(scope): description"
  echo "Example: feat(auth): add OAuth2 login flow"
  exit 1
fi
```

### Branch Naming Enforcement

```bash
#!/bin/sh
# .githooks/pre-push
branch=$(git symbolic-ref --short HEAD)
pattern="^(feature|bugfix|hotfix|release|chore)/[a-z0-9._-]+$"

if ! echo "$branch" | grep -qE "$pattern"; then
  echo "ERROR: Branch '$branch' doesn't match pattern."
  echo "Use: feature/desc, bugfix/desc, hotfix/desc"
  exit 1
fi
```

### Secret Detection

```bash
#!/bin/sh
# .githooks/pre-commit
patterns="(PRIVATE.KEY|password\s*=|secret\s*=|api[_-]?key\s*=|AWS_SECRET|BEGIN RSA)"
staged=$(git diff --cached --name-only --diff-filter=ACM)
for file in $staged; do
  if git show ":$file" | grep -qEi "$patterns"; then
    echo "ERROR: Possible secret detected in $file"
    exit 1
  fi
done
```

### File Size Limit

```bash
#!/bin/sh
# .githooks/pre-commit — block files over 1MB
max_size=1048576
for file in $(git diff --cached --name-only --diff-filter=ACM); do
  size=$(git cat-file -s ":$file" 2>/dev/null || echo 0)
  [ "$size" -gt "$max_size" ] && echo "ERROR: $file exceeds 1MB limit." && exit 1
done
```

### Merge Conflict Markers

```bash
#!/bin/sh
# .githooks/pre-commit — block commits with unresolved conflicts
for file in $(git diff --cached --name-only --diff-filter=ACM); do
  if git show ":$file" | grep -qE "^(<<<<<<<|=======|>>>>>>>)"; then
    echo "ERROR: Merge conflict markers in $file"; exit 1
  fi
done
```

### Hooks in Node.js / Python

```js
#!/usr/bin/env node
// .githooks/commit-msg — validate conventional commits
const fs = require('fs');
const msg = fs.readFileSync(process.argv[2], 'utf8').trim();
if (!/^(feat|fix|docs|chore|refactor|test|perf|ci)(\(.+\))?: .{1,72}/.test(msg)) {
  console.error('Invalid commit message. Use: type(scope): description');
  process.exit(1);
}
```

```python
#!/usr/bin/env python3
# .githooks/pre-commit — syntax-check staged Python files
import subprocess, sys
staged = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
    capture_output=True, text=True).stdout.strip().split("\n")
for f in [x for x in staged if x.endswith(".py")]:
    if subprocess.run(["python", "-m", "py_compile", f]).returncode != 0:
        print(f"Syntax error in {f}"); sys.exit(1)
```

## Sharing Hooks with Team

```bash
# Husky: hooks in .husky/, auto-installed via "prepare": "husky"

# core.hooksPath: language-agnostic, works everywhere
mkdir .githooks && chmod +x .githooks/*
git config core.hooksPath .githooks
# Automate: { "scripts": { "prepare": "git config core.hooksPath .githooks" } }

# Shared .gitconfig (opt-in per developer)
# Commit .gitconfig with [core] hooksPath = .githooks
# Developer runs: git config --local include.path ../.gitconfig
```

## Bypassing Hooks

```bash
git commit --no-verify -m "hotfix: emergency production fix"
git push --no-verify

# Appropriate: emergency hotfixes, WIP commits, broken hook blocking work
# NOT appropriate: skipping failing tests regularly, bypassing secret detection
```

## Debugging Hooks

```bash
git config core.hooksPath          # check active hooks dir (blank = .git/hooks/)
git rev-parse --git-path hooks     # resolved path
bash -x .husky/pre-commit          # trace execution
chmod +x .githooks/pre-commit      # fix permissions

# Common issues: missing chmod +x, wrong shebang, nvm not loaded
# (hooks don't source .bashrc), wrong core.hooksPath
# Fix nvm: add to hook: export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
# Debug env: add temporarily: env > /tmp/hook-env.txt
```

## Monorepo Patterns

### Lefthook Monorepo

```yaml
# lefthook.yml
pre-commit:
  commands:
    frontend-lint:
      root: packages/frontend/
      glob: "*.{ts,tsx}"
      run: npx eslint --fix {staged_files}
    backend-lint:
      root: packages/backend/
      glob: "*.py"
      run: ruff check --fix {staged_files}
```

### lint-staged Monorepo

```js
// lint-staged.config.mjs (root)
export default {
  'packages/frontend/**/*.{ts,tsx}': (files) =>
    `cd packages/frontend && npx eslint --fix ${files.join(' ')}`,
  'packages/backend/**/*.py': (files) =>
    `cd packages/backend && ruff check --fix ${files.join(' ')}`,
}
```

### Affected-Only Pre-push

```bash
#!/bin/sh
# .husky/pre-push — only test changed packages
changed=$(git diff --name-only @{push}..)
echo "$changed" | grep -q "^packages/frontend/" && (cd packages/frontend && npm test)
echo "$changed" | grep -q "^packages/backend/" && (cd packages/backend && npm test)
```

## CI/CD Hook Equivalents

```yaml
# GitHub Actions — CI safety net mirrors local hooks
name: Code Quality
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: npm ci
      - run: npx eslint . && npx prettier --check .
      - run: npm test
      - run: npx commitlint --from ${{ github.event.pull_request.base.sha }}
```
