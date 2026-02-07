# Pytest Guide

## Basic Test Structure

```python
import pytest

def test_addition():
    assert 1 + 1 == 2

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

class TestCalculator:
    def test_add(self):
        assert add(1, 2) == 3
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest test_module.py

# Run specific test
pytest test_module.py::test_function

# Run with pattern
pytest -k "test_user"

# Run with markers
pytest -m "unit"

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last N failures
pytest --lf
```

## Fixtures

```python
@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_with_fixture(sample_data):
    assert len(sample_data) == 5
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")  # Run once per test session
def db():
    pass

@pytest.fixture(scope="module")   # Run once per module
def connection():
    pass

@pytest.fixture(scope="function") # Run once per test (default)
def response():
    pass
```

### Fixture Cleanup

```python
@pytest.fixture
def resource():
    resource = allocate()
    yield resource
    resource.cleanup()
```

## Parameterization

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

## Markers

```python
@pytest.mark.slow
def test_slow_operation():
    pass

# Run: pytest -m "not slow"

@pytest.mark.skip(reason="Not implemented")
def test_not_ready():
    pass

@pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9+")
def test_new_feature():
    pass
```

## Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Generate report
coverage report
coverage html
```
