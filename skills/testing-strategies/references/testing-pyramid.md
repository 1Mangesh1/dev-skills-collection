# Testing Pyramid: Unit, Integration, E2E Tests

## The Testing Pyramid

```
        E2E Tests (5-10%)
       /                \
      /                  \
     Integration Tests (15-20%)
    /                        \
   /                          \
  Unit Tests (70-80%)
```

### Unit Tests (Base)
**What:** Test individual functions/methods in isolation.

**Characteristics:**
- Fast (milliseconds)
- Focused on single unit
- Mock external dependencies
- ~70-80% of all tests

**Example (Python with pytest):**
```python
import pytest
from calculator import add, subtract

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_subtract_returns_difference():
    assert subtract(5, 3) == 2

@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1, 2, 3),
    (-1, 1, 0),
])
def test_add_various_inputs(a, b, expected):
    assert add(a, b) == expected
```

**Example (JavaScript with Jest):**
```javascript
describe('Calculator', () => {
  test('adds two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('subtracts numbers', () => {
    expect(subtract(5, 3)).toBe(2);
  });

  test.each([
    [0, 0, 0],
    [1, 2, 3],
    [-1, 1, 0],
  ])('adds %i and %i to get %i', (a, b, expected) => {
    expect(add(a, b)).toBe(expected);
  });
});
```

### Integration Tests (Middle)
**What:** Test interaction between multiple units.

**Characteristics:**
- Slower (seconds)
- Test integration points
- Use real services or test doubles
- ~15-20% of all tests

**Example:**
```python
import pytest
from flask import Flask
from app import create_app, db
from models import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_create_user_integration(app):
    """Test user creation through API."""
    client = app.test_client()
    
    # Make API request
    response = client.post('/api/users', json={
        'email': 'test@example.com',
        'password': 'secure123'
    })
    
    assert response.status_code == 201
    
    # Verify data in database
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.email == 'test@example.com'
```

### End-to-End Tests (Top)
**What:** Test complete user workflows.

**Characteristics:**
- Slowest (minutes)
- Test full application flow
- Use real environment
- ~5-10% of all tests

**Example (Selenium/Cypress):**
```javascript
describe('User Registration E2E', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/signup');
  });

  it('completes user registration successfully', () => {
    // Fill form
    cy.get('input[name="email"]').type('user@example.com');
    cy.get('input[name="password"]').type('SecurePass123!');
    cy.get('input[name="confirm_password"]').type('SecurePass123!');
    
    // Submit form
    cy.get('button[type="submit"]').click();
    
    // Verify success
    cy.url().should('include', '/dashboard');
    cy.get('.welcome-message').should('contain', 'Welcome');
  });
});
```

## Testing Best Practices

### 1. Arrange-Act-Assert Pattern
```python
def test_user_activation():
    # Arrange: Set up test data
    user = User(email='test@example.com', is_active=False)
    db.session.add(user)
    db.session.commit()
    
    # Act: Perform action
    user.activate()
    
    # Assert: Verify result
    assert user.is_active is True
```

### 2. Test Naming Convention
```
test_{functionality}_{scenario}_{expected_result}

Examples:
- test_user_creation_with_valid_email_succeeds()
- test_user_creation_with_invalid_email_fails()
- test_password_reset_sends_email()
```

### 3. DRY Testing with Fixtures
```python
import pytest

@pytest.fixture
def valid_user_data():
    return {
        'email': 'user@example.com',
        'password': 'SecurePass123!',
        'first_name': 'John'
    }

def test_create_user(valid_user_data):
    user = User.create(**valid_user_data)
    assert user.email == valid_user_data['email']

def test_user_validates_email(valid_user_data):
    # Can reuse the fixture
    assert User.validate_email(valid_user_data['email'])
```

### 4. Mocking and Stubbing
```python
from unittest.mock import patch, MagicMock

def test_user_signup_sends_email():
    with patch('email_service.send_email') as mock_send:
        user = User.create(email='test@example.com')
        
        # Verify email was sent
        mock_send.assert_called_once_with(
            to='test@example.com',
            subject='Welcome!'
        )

def test_with_mocked_database():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = User(id=1)
    
    result = get_user(1, db=mock_db)
    assert result.id == 1
```

### 5. Test Data Builders
```python
class UserBuilder:
    def __init__(self):
        self.data = {
            'email': 'default@example.com',
            'password': 'SecurePass123!',
            'is_active': True
        }
    
    def with_email(self, email):
        self.data['email'] = email
        return self
    
    def inactive(self):
        self.data['is_active'] = False
        return self
    
    def build(self):
        return User(**self.data)

# Usage
def test_inactive_user_login():
    user = UserBuilder().inactive().build()
    assert not user.can_login()
```

## Code Coverage Best Practices

### Coverage Goals by Project Type

```
Research/Prototype:    40-50%
Standard Application:  70-80%
Critical Systems:      90%+
Security Libraries:    95%+
```

### Useful Coverage Metrics

```python
# Python - pytest-cov
pytest --cov=mymodule --cov-report=html --cov-report=term-missing

# JavaScript - Jest
jest --coverage

# Java - JaCoCo
mvn clean test jacoco:report
```

### Avoiding False Coverage

```python
# DON'T: Just checking line execution
def test_divide(self):
    result = divide(10, 2)  # Line executed, but no assertion!

# DO: Assert expected behavior
def test_divide(self):
    result = divide(10, 2)
    assert result == 5

# DON'T: Testing implementation, not behavior
def test_user_object_created(self):
    user = User()
    assert user.__dict__ == {...}

# DO: Testing behavior
def test_user_can_be_created_with_email(self):
    user = User(email='test@example.com')
    assert user.email == 'test@example.com'
```

## Test Execution Strategy

### CI/CD Integration
```yaml
stages:
  - unit_tests      # Fast feedback (< 2 min)
  - integration     # Medium speed (2-10 min)
  - e2e_tests       # Slow (10-30+ min)
  
unit_tests:
  script:
    - pytest tests/unit/ -v

integration:
  needs: ["unit_tests"]
  script:
    - pytest tests/integration/ -v

e2e_tests:
  needs: ["integration"]
  script:
    - npm run test:e2e
```

### Parallel Test Execution
```bash
# Run tests in parallel with pytest-xdist
pytest -n auto

# Run tests in parallel with Jest
jest --maxWorkers=4
```
