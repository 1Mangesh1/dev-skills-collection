# Unit Testing Best Practices

## Structure: Arrange-Act-Assert

```python
def test_user_creation_with_valid_data():
    # Arrange: Setup
    user_data = {
        "email": "test@example.com",
        "password": "secure_password_123"
    }
    
    # Act: Execute
    user = User.create(user_data)
    
    # Assert: Verify
    assert user.email == "test@example.com"
    assert user.id is not None
```

## Test Naming Convention

```python
# Good: Describes what is tested, scenario, and expected result
test_user_creation_with_valid_email_succeeds()
test_user_creation_with_invalid_email_raises_error()
test_user_creation_with_duplicate_email_fails()

# Bad: Vague
test_user_creation()
test_create()
```

## Isolation: Use Mocks

```python
from unittest.mock import Mock

def test_payment_processing():
    # Mock external API
    payment_api = Mock()
    payment_api.charge.return_value = {"status": "success"}
    
    # Test your code
    result = process_payment(amount=100, api=payment_api)
    
    payment_api.charge.assert_called_once_with(100)
    assert result == {"status": "success"}
```

## AVoid Common Pitfalls

### ❌ Testing Implementation Details
```python
# Bad: Testing private method
def test_private_calculation():
    obj = MyClass()
    result = obj._calculate_internal()
    assert result == 42
```

### ✓ Test Behavior
```python
# Good: Test public API
def test_final_result():
    obj = MyClass()
    result = obj.get_result()
    assert result == 42
```

### ❌ Non-deterministic Tests
```python
# Bad: Uses current time (flaky)
def test_expiration():
    token = create_token()
    sleep(1)
    assert token.is_expired()
```

### ✓ Deterministic Tests
```python
# Good: Controls time
def test_expiration():
    token = create_token(expires_in=0)
    assert token.is_expired()
```

## Test Organization

```
tests/
├── unit/
│   ├── test_user.py
│   ├── test_order.py
│   └── test_payment.py
├── integration/
│   ├── test_user_flow.py
│   └── test_payment_flow.py
└── e2e/
    └── test_checkout.py
```

## Fixtures and Test Data

```python
import pytest

@pytest.fixture
def user():
    """Reusable test user"""
    return User.create(email="test@example.com")

@pytest.fixture
def auth_headers(user):
    """Depends on user fixture"""
    login_response = login(user.email, "password")
    return {"Authorization": f"Bearer {login_response['token']}"}

def test_protected_endpoint(auth_headers):
    response = client.get("/api/profile", headers=auth_headers)
    assert response.status == 200
```
