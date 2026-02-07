# Vitest Framework

## Vitest vs Jest

| Feature | Jest | Vitest |
|---------|------|--------|
| Speed | Medium | Fast (ESM native) |
| Config | jest.config.js | vitest.config.ts |
| Setup | Heavier | Lighter |
| ESM Support | Limited | Native |

## Setup

```bash
npm install --save-dev vitest
npx vitest init
```

## Vitest Config

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/']
    }
  }
});
```

## Running Tests

```bash
# Run once
npx vitest run

# Watch mode
npx vitest

# UI mode
npx vitest --ui

# Coverage
npx vitest run --coverage

# Specific file
npx vitest run src/math.test.ts
```

## Benefits over Jest

1. **Faster** - ESM native, 10x faster in many cases
2. **Compatible** - Jest API compatible
3. **Easier config** - Less boilerplate
4. **Vite integration** - Works with Vite
5. **Better IDE support** - IntelliSense
6. **UI mode** - Visual test runner

## Migration from Jest

Almost 1:1 compatible:

```javascript
// Works in both
describe('Test', () => {
  it('works', () => {
    expect(1).toBe(1);
  });
});

// Just change import/config
// jest.config.js → vitest.config.ts
```

## Performance Comparison

```
Jest:   5000 tests in 45s
Vitest: 5000 tests in 8s
```

Great for large test suites.
