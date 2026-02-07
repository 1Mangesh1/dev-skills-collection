# Test-Driven Development (TDD) and Best Practices

## Red-Green-Refactor Cycle

### The TDD Workflow

```
1. RED: Write failing test
   └─ Test describes desired behavior
   └─ Code doesn't exist yet, test fails

2. GREEN: Write minimal code to pass test
   └─ Quick implementation
   └─ Test now passes
   └─ Code may be ugly/inefficient

3. REFACTOR: Clean up code
   └─ Improve readability
   └─ Optimize implementation
   └─ Tests still pass
```

### Example: Implementing a Stack

```python
# Step 1: RED - Write the failing test
def test_push_adds_element_to_stack():
    stack = Stack()
    stack.push(5)
    assert stack.peek() == 5

# Step 2: GREEN - Minimal implementation
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def peek(self):
        return self.items[-1] if self.items else None

# Step 3: REFACTOR
# (Consider edge cases, optimization, clarity)
class Stack:
    def __init__(self):
        self._items = []
    
    def push(self, item):
        """Add item to top of stack."""
        if item is None:
            raise ValueError("Cannot push None")
        self._items.append(item)
    
    def peek(self):
        """Return top element without removing."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]
    
    def pop(self):
        """Remove and return top element."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def is_empty(self):
        return len(self._items) == 0
    
    def size(self):
        return len(self._items)
```

## Testing in Different Phases

### Phase 1: Design Phase Tests
Test behavior specification:
```python
# What should the function do?
def test_email_validation_accepts_valid_email():
    assert is_valid_email('user@example.com')

def test_email_validation_rejects_invalid_email():
    assert not is_valid_email('invalid-email')

def test_email_validation_rejects_no_domain():
    assert not is_valid_email('user@')
```

### Phase 2: Implementation Phase Tests
Test edge cases and error conditions:
```python
def test_email_with_special_chars():
    assert is_valid_email('user+tag@example.com')

def test_email_with_subdomain():
    assert is_valid_email('user@mail.example.co.uk')

def test_email_case_insensitive():
    assert is_valid_email('User@Example.COM')

def test_email_rejects_spaces():
    assert not is_valid_email('user @example.com')
```

### Phase 3: Maintenance Phase Tests
Test against regression:
```python
def test_existing_users_still_validate():
    """Ensure validation change doesn't break existing data."""
    existing_emails = load_production_emails()
    for email in existing_emails:
        assert is_valid_email(email), f"Breaks existing user: {email}"
```

## Mock, Stub, Spy, Fake

### Mocking (Complete Replacement)
```python
from unittest.mock import Mock

def test_payment_processing():
    # Create mock payment service
    payment_service = Mock()
    payment_service.charge.return_value = True
    
    # Use in code
    result = process_order(order, payment_service)
    
    # Verify correct calls
    payment_service.charge.assert_called_once_with(
        amount=100.00
    )
```

### Stubbing (Replace with Fake)
```python
class FakeURLFetcher:
    def fetch(self, url):
        # Return fake data instead of making real HTTP request
        return '{"status": "ok"}'

def test_api_response_handling():
    fetcher = FakeURLFetcher()
    result = process_api_response(fetcher)
    assert result.status == 'ok'
```

### Spying (Observe Behavior)
```python
from unittest.mock import spy

def test_logging_on_error():
    with spy(logger, 'error') as spy_error:
        process_invalid_input('bad')
        spy_error.assert_called_once()
```

### Fakes (Complete Implementation)
```python
class FakeDatabase:
    def __init__(self):
        self.users = {}
    
    def save_user(self, user):
        self.users[user.id] = user
    
    def get_user(self, user_id):
        return self.users.get(user_id)

def test_user_service():
    db = FakeDatabase()
    service = UserService(db)
    
    user = User(id=1, name='John')
    service.create_user(user)
    
    retrieved = db.get_user(1)
    assert retrieved.name == 'John'
```

## Testing Anti-Patterns to Avoid

### ❌ Don't: Test Implementation Details
```python
# BAD: Testing internal implementation
def test_user_validation():
    user = User('john@example.com')
    assert user._encrypted_password != 'password123'
```

### ✅ DO: Test Behavior
```python
# GOOD: Testing public behavior
def test_user_password_is_secure():
    user = User('john@example.com')
    assert user.verify_password('password123')
    assert not user.verify_password('wrong_password')
```

### ❌ Don't: Create Test Interdependencies
```python
# BAD: Tests depend on each other
def test_1_create_user():
    global user
    user = create_user()

def test_2_logout_user():
    # Depends on test_1_create_user!
    logout(user)
```

### ✅ DO: Independent Tests
```python
# GOOD: Each test is self-contained
def test_can_create_user():
    user = create_user()
    assert user is not None

def test_can_logout_user():
    user = create_user()  # Create fresh user
    logout(user)
    assert not user.is_active
```

### ❌ Don't: Test Multiple Behaviors
```python
# BAD: Tests too many things
def test_user_workflow():
    user = create_user('john@example.com', 'pass')
    assert user.id is not None
    assert user.email == 'john@example.com'
    user.update_password('newpass')
    assert user.verify_password('newpass')
    user.activate()
    assert user.is_active
```

### ✅ DO: One Assertion Per Test
```python
# GOOD: Single responsibility
def test_create_user_generates_id():
    user = create_user()
    assert user.id is not None

def test_create_user_sets_email():
    user = create_user('john@example.com')
    assert user.email == 'john@example.com'

def test_update_password_changes_password():
    user = create_user()
    user.update_password('newpass')
    assert user.verify_password('newpass')
```

## Performance Testing

### Load Testing
```python
import timeit

def test_query_performance():
    """Ensure query completes in acceptable time."""
    execution_time = timeit.timeit(
        lambda: get_users(limit=1000),
        number=100
    )
    avg_time = execution_time / 100
    
    assert avg_time < 0.1, f"Query took {avg_time}s, expected < 0.1s"
```

### Memory Profiling
```python
import tracemalloc

def test_memory_usage():
    tracemalloc.start()
    
    # Process data
    process_large_dataset()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Memory should not exceed 100MB
    assert peak < 100 * 1024 * 1024
```
