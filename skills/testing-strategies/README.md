# Testing Strategies Quick Start

Build comprehensive test suites with effective testing strategies.

## Test Pyramid

```
           UI/E2E Tests
          /            \
       Integration Tests
       /                \
  Unit Tests (60%)
```

- **Unit** (60%) - Fast, isolated, low-level
- **Integration** (30%) - Component interactions
- **E2E** (10%) - Full workflows, slowest

## Quick Test Types

### Unit Testing
```javascript
test_calculateTotal_emptyCart_returnsZero() {
  const cart = new Cart();
  assert.equal(cart.getTotal(), 0);
}
```

### Integration Testing
```javascript
test_getUser_validId_returnsUser() {
  const user = db.query('SELECT * FROM users WHERE id = 1');
  assert.notNull(user);
}
```

### E2E Testing
```javascript
test_userCanLogin_fillFormAndSubmit() {
  cy.visit('/login');
  cy.get('input[name="email"]').type('test@example.com');
  cy.get('input[name="password"]').type('password');
  cy.get('button[type="submit"]').click();
  cy.url().should('include', '/dashboard');
}
```

## AAA Pattern (Arrange-Act-Assert)

```javascript
test('adds items to cart', () => {
  // Arrange
  const cart = new Cart();
  const item = { price: 10 };
  
  // Act
  cart.addItem(item);
  
  // Assert
  assert.equal(cart.getTotal(), 10);
});
```

## Coverage Goals

- **Minimum**: 70-80%
- **Target**: 80-85%
- **Not needed**: Trivial getters, frameworks, UI

## Testing Tools

| Type | Tools |
|------|-------|
| Unit | Jest, Pytest, Mocha, Vitest |
| Integration | Supertest, Postman, py.test |
| E2E | Cypress, Playwright, Selenium |
| Coverage | Istanbul, Coverage.py |

## What to Test

1. **Happy path** - Normal flow works
2. **Edge cases** - Boundaries, nulls, empty
3. **Error handling** - Invalid input handling
4. **Async/timing** - Race conditions
5. **State changes** - Before/after verification

## Testing Checklist

- [ ] Arrange-Act-Assert pattern used
- [ ] Slow tests isolated or skipped in watch mode
- [ ] No hardcoded test data
- [ ] Clear, descriptive test names
- [ ] Tests are deterministic (no flakiness)
- [ ] Mocks used appropriately
- [ ] Edge cases covered
- [ ] Error cases tested

## Common Mistakes

❌ Testing implementation details
❌ Over-mocking (testing mocks not code)
❌ Flaky tests (timing-dependent)
❌ Not testing error paths
❌ Testing trivial code

✅ Test behavior, not implementation
✅ Test real user workflows
✅ Make tests deterministic
✅ Comprehensive error coverage

## Resources

- [Jest Documentation](https://jestjs.io/)
- [Cypress Best Practices](https://docs.cypress.io/guides/references/best-practices)
- [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Growing Object-Oriented Software](http://www.growing-object-oriented-software.com/)

## See Also

- SKILL.md - Advanced patterns and strategies
- metadata.json - Testing framework references
