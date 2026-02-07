#!/usr/bin/env bash
# AWS CLI EC2 Instance Launcher
# Quickly launch and configure EC2 instances

launch_ec2_instance() {
    local instance_type="$1"
    local key_name="$2"
    
    echo "=== Launching EC2 Instance ==="
    aws ec2 run-instances \
        --image-id ami-0c55b159cbfafe1f0 \
        --instance-type "$instance_type" \
        --key-name "$key_name" \
        --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-app-instance}]' \
        --output table
}

# List running instances
list_instances() {
    echo "=== Running Instances ==="
    aws ec2 describe-instances \
        --filters Name=instance-state-name,Values=running \
        --query 'Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,IP:PublicIpAddress,State:State.Name}' \
        --output table
}

# Usage
launch_ec2_instance "t3.micro" "my-key-pair"
list_instances
