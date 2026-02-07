#!/usr/bin/env python3
"""Terraform State & Cost Analysis"""

import json
import subprocess

def get_terraform_state():
    """Get current Terraform state"""
    result = subprocess.run(
        ['terraform', 'show', '-json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def list_resources():
    """List all managed resources"""
    result = subprocess.run(
        ['terraform', 'state', 'list'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

def plan_json_output():
    """Get plan as JSON for analysis"""
    result = subprocess.run(
        ['terraform', 'plan', '-json'],
        capture_output=True,
        text=True
    )
    return result.stdout

def get_outputs():
    """Get Terraform outputs"""
    result = subprocess.run(
        ['terraform', 'output', '-json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

if __name__ == "__main__":
    resources = list_resources()
    print(f"Managed resources: {len(resources)}")
