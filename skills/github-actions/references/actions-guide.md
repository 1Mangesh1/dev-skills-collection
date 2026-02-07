# GitHub Actions Complete Guide

## Workflow Structure

```yaml
name: CI

# When to run
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:  # Manual trigger

jobs:
  test:
    runs-on: ubuntu-latest    # macos-latest, windows-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x, 21.x]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

## Common Actions

- `actions/checkout@v3` - Clone repo
- `actions/setup-node@v3` - Install Node.js
- `actions/setup-python@v4` - Install Python
- `actions/upload-artifact@v3` - Store build artifacts
- `actions/cache@v3` - Cache dependencies

## Using Secrets

```yaml
- name: Deploy
  run: npm run deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

1. Go to repo Settings → Secrets and variables → Actions
2. Add secrets (encrypted, not logged)
3. Reference with `${{ secrets.NAME }}`

## Matrix Builds

Test multiple configurations:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18.x, 20.x]
    exclude:
      - os: windows-latest
        node: 18.x  # Skip incompatible combo
```

Creates 3 jobs: (ubuntu, 18), (ubuntu, 20), (windows, 20)

## Job Dependencies

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
  
  deploy:
    needs: test  # Only run if test succeeds
    runs-on: ubuntu-latest
    steps:
      - run: npm run deploy
```

## Artifacts & Caching

```yaml
# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('package-lock.json') }}

# Upload build output
- uses: actions/upload-artifact@v3
  with:
    name: build
    path: dist/
```

## Performance Tips

1. Use `npm ci` instead of `npm install`
2. Cache dependencies (saves 2-3 minutes)
3. Run tests in parallel (matrix)
4. Only deploy on main branch
5. Use `concurrency` to cancel older runs

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
