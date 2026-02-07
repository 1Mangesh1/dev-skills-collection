#!/usr/bin/env python3
"""Pytest Fixture Generator"""

def generate_fixture_template(fixture_name, dependencies=None):
    """Generate pytest fixture template"""
    
    deps_str = ""
    if dependencies:
        deps_str = f", {', '.join(dependencies)}"
    
    template = f'''
@pytest.fixture
def {fixture_name}({deps_str}):
    """
    Fixture: {fixture_name}
    
    Setup: Prepare test data
    Usage: Include '{fixture_name}' parameter in test function
    Teardown: Cleanup if needed
    """
    # Setup
    data = prepare_data()
    
    yield data
    
    # Teardown
    cleanup_data(data)
'''
    
    return template

if __name__ == "__main__":
    print(generate_fixture_template("database_connection", ["config"]))
