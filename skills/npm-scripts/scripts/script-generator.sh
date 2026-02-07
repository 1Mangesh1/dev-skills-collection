#!/usr/bin/env bash
# NPM Scripts Helper
# Common npm script patterns and shortcuts

generate_package_scripts() {
    cat << 'EOF'
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier --write .",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "type-check": "tsc --noEmit",
    "pre-commit": "lint-staged",
    "prepare": "husky install"
  }
}
EOF
}

list_available_scripts() {
    echo "=== Available npm Scripts ==="
    npm run 2>/dev/null | grep -v "available via" | tail -n +3
}

run_script() {
    local script="$1"
    echo "Running: npm run $script"
    npm run "$script"
}

# Usage
generate_package_scripts
list_available_scripts
