#!/usr/bin/env bash
# Python Environment Manager
# Manage virtual environments and dependencies

create_venv() {
    local env_name="${1:-.venv}"
    
    echo "=== Creating Virtual Environment: $env_name ==="
    
    python3 -m venv "$env_name"
    source "$env_name/bin/activate"
    
    pip install --upgrade pip setuptools wheel
    echo "✓ Virtual environment created and activated"
}

activate_venv() {
    local env_name="${1:-.venv}"
    
    if [ -f "$env_name/bin/activate" ]; then
        source "$env_name/bin/activate"
        echo "✓ Activated: $env_name"
    else
        echo "❌ Virtual environment not found: $env_name"
    fi
}

freeze_requirements() {
    local output_file="${1:-requirements.txt}"
    
    echo "=== Freezing Dependencies ==="
    pip freeze > "$output_file"
    echo "✓ Saved to: $output_file"
}

install_from_requirements() {
    local requirements_file="${1:-requirements.txt}"
    
    echo "=== Installing from $requirements_file ==="
    pip install -r "$requirements_file"
}

# Usage
create_venv
freeze_requirements
