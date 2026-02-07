#!/usr/bin/env bash
# Terraform Infrastructure Manager
# Initialize, plan, and apply Terraform

init_terraform() {
    echo "=== Initializing Terraform ==="
    terraform init
    echo "✓ Terraform initialized"
}

plan_terraform() {
    local output_file="${1:-tfplan}"
    
    echo "=== Terraform Plan ==="
    terraform plan -out="$output_file"
    echo "✓ Plan saved to: $output_file"
}

apply_terraform() {
    local plan_file="${1:-tfplan}"
    
    echo "=== Applying Terraform ==="
    terraform apply "$plan_file"
    echo "✓ Infrastructure updated"
}

destroy_terraform() {
    echo "=== Destroying Terraform Resources ==="
    read -p "Confirm destruction? (yes/no) " -r
    if [[ $REPLY == "yes" ]]; then
        terraform destroy
    fi
}

validate_terraform() {
    echo "=== Validating Terraform ==="
    terraform validate
    echo "✓ Configuration valid"
}

# Usage
init_terraform
validate_terraform
