# Pytest Advanced Features

## Conftest.py (Shared Fixtures)

```python
# conftest.py (in test directory root)

import pytest

@pytest.fixture
def api_client():
    """Shared fixture for all tests"""
    return APIClient()

def pytest_configure(config):
    """Called before test run"""
    config.addinivalue_line("markers", "slow: marks tests as slow")

def pytest_collection_modifyitems(config, items):
    """Modify test items before running"""
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)
```

## Hooks & Plugins

```python
# Custom hook
def pytest_runtest_makereport(item, call):
    """Called after test execution"""
    if call.when == "call":
        if call.excinfo is None:
            print(f"✓ {item.name} passed")
        else:
            print(f"✗ {item.name} failed")
```

## Database Testing

```python
@pytest.fixture
def db(monkeypatch):
    """Use test database"""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from app import db
    db.create_all()
    yield db
    db.session.remove()

def test_user_creation(db):
    user = User(name="test")
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
```

## Mocking

```python
from unittest.mock import Mock, patch

def test_api_call(monkeypatch):
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    
    monkeypatch.setattr("requests.get", Mock(return_value=mock_response))
    
    result = call_api()
    assert result["status"] == "ok"
```

## Performance Testing

```python
@pytest.mark.timeout(5)  # Must complete in 5 seconds
def test_performance():
    result = expensive_operation()
    assert result is not None
```
