# Jest Testing Framework

## Setup

```bash
npm install --save-dev jest
npx jest --init
```

## Basic Test

```javascript
describe('Calculator', () => {
  test('adds 1 + 2 to equal 3', () => {
    const result = add(1, 2);
    expect(result).toBe(3);
  });
});
```

## Common Matchers

```javascript
// Equality
expect(value).toBe(5);              // ===
expect(object).toEqual({a: 1});     // Deep equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeCloseTo(0.3);

// Strings
expect(str).toMatch(/hello/i);
expect(str).toContain('hello');

// Arrays
expect(arr).toHaveLength(3);
expect(arr).toContain('item');

// Exceptions
expect(() => foo()).toThrow();
expect(() => foo()).toThrow(TypeError);
```

## Setup & Teardown

```javascript
describe('Database', () => {
  beforeAll(() => {
    // Initialize database
  });

  beforeEach(() => {
    // Clear data before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  afterAll(() => {
    // Close database connection
  });
});
```

## Mocking

```javascript
// Mock function
const mockFn = jest.fn();
mockFn.mockReturnValue(42);

// Mock module
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} }))
}));

// Spy on method
const spy = jest.spyOn(obj, 'method');
```

## Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/**/*.test.{js,jsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```
