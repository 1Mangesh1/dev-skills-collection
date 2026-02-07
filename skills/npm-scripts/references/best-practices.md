# NPM Scripts Best Practices

## Security

**Never use `sudo` in npm scripts**:
```json
{
  "❌ postinstall": "sudo chown -R user .",
  "✓ postinstall": "npm rebuild"
}
```

**Avoid running untrusted code**:
```bash
# Bad: Runs arbitrary command from user input
npm run-script $USER_INPUT

# Better: Validate input first
```

## Performance

**Failing fast**:
```json
{
  "test": "jest --bail"  // Stop on first failure
}
```

**Parallel execution**:
```json
{
  "lint-test": "npm-run-all --parallel lint test"
}
```

## Debugging

```bash
# See what command is running
npm run build --verbose

# Or directly
npm_package_version=1.0.0 npm_package_name=myapp node script.js
```

## Cross-platform

```json
{
  "scripts": {
    "clean": "rimraf dist/",  // Cross-platform rm -rf
    "build": "cross-env NODE_ENV=production webpack"
  }
}
```

Or use conditional logic:

```json
{
  "start": "node bin/www.js",
  "start:windows": "node bin\\www.js"
}
```

## Documentation

Add descriptions:

```json
{
  "scripts": {
    "dev": "vite                          // Start dev server",
    "build": "vite build                  // Build for production",
    "test": "jest                         // Run all tests"
  }
}
```
