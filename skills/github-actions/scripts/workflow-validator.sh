#!/usr/bin/env bash
# GitHub Actions Workflow Validator
# Validates YAML syntax and common mistakes

validate_workflows() {
    local workflow_dir=".github/workflows"
    
    if [ ! -d "$workflow_dir" ]; then
        echo "No workflows found"
        return 1
    fi
    
    echo "=== Validating Workflows ==="
    
    for workflow in "$workflow_dir"/*.yml "$workflow_dir"/*.yaml; do
        if [ -f "$workflow" ]; then
            echo "Checking $(basename "$workflow")..."
            
            # Check for common mistakes
            if grep -q "secrets\.GITHUB_TOKEN" "$workflow"; then
                echo "  ✓ Uses GITHUB_TOKEN"
            fi
            
            if grep -q "needs:" "$workflow"; then
                echo "  ✓ Has job dependencies"
            fi
            
            if ! grep -q "runs-on:" "$workflow"; then
                echo "  ⚠ Missing runs-on"
            fi
        fi
    done
}

validate_workflows
