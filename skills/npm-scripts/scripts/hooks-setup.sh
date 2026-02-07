#!/usr/bin/env bash
# NPM Lifecycle Hooks Manager
# Manage pre/post script hooks

setup_lifecycle_hooks() {
    echo "=== Setting up NPM Lifecycle Hooks ==="
    
    cat >> package.json <<'EOF'
"scripts": {
  "prebuild": "npm run lint && npm run type-check",
  "build": "tsc && vite build",
  "postbuild": "npm run test",
  
  "pretest": "npm run lint",
  "test": "jest",
  "posttest": "generate-coverage-report"
}
EOF
}

# Usage
setup_lifecycle_hooks
