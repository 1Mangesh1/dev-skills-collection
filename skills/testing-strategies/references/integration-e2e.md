# Integration & E2E Testing

## Integration Testing

Tests interactions between components:

```python
def test_user_registration_to_email_confirmation():
    """Test full registration flow"""
    # Register user
    response = client.post("/api/register", json={
        "email": "test@example.com",
        "password": "safe_password"
    })
    assert response.status == 201
    
    # Check email was queued
    assert len(email_queue) == 1
    email = email_queue[0]
    assert email["to"] == "test@example.com"
    
    # Extract confirmation link
    import re
    match = re.search(r'/confirm/(\w+)', email["body"])
    token = match.group(1)
    
    # Confirm email
    response = client.get(f"/api/confirm/{token}")
    assert response.status == 200
    
    # User is now active
    user = User.query.filter_by(email="test@example.com")
    assert user.confirmed_at is not None
```

## End-to-End Testing

Complete user workflows in browser:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_checkout_flow():
    """Test complete checkout"""
    driver = webdriver.Chrome()
    
    # Browse products
    driver.get("https://shop.example.com")
    products = driver.find_elements(By.CLASS_NAME, "product")
    assert len(products) > 0
    
    # Add to cart
    products[0].click()
    add_to_cart = driver.find_element(By.ID, "add-to-cart")
    add_to_cart.click()
    
    # Go to cart
    cart = driver.find_element(By.ID, "cart-link")
    cart.click()
    
    # Checkout
    checkout = driver.find_element(By.ID, "checkout-button")
    checkout.click()
    
    # Payment info
    email = driver.find_element(By.NAME, "email")
    email.send_keys("test@example.com")
    # ... fill payment details
    
    # Verify order
    assert "Order confirmed" in driver.page_source
```

## Test Environment Setup

```python
# conftest.py - Shared test configuration
import pytest

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    db.create_all()
    yield db
    db.drop_all()

@pytest.fixture
def app():
    """Flask app with test config"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()
```

## Performance in Tests

```python
def test_list_1000_items_is_fast():
    """Ensure pagination works for large datasets"""
    # Create 1000 items
    for i in range(1000):
        create_item(name=f"Item {i}")
    
    # Request first page
    start = time.time()
    response = client.get("/api/items?page=1&limit=20")
    duration = time.time() - start
    
    assert response.status == 200
    assert duration < 0.5  # Should be fast even with 1000 items
    assert len(response.json["items"]) == 20
```
