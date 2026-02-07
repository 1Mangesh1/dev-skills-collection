#!/usr/bin/env python3
"""GitHub Actions Matrix Generator"""

import json

def generate_test_matrix():
    """Generate matrix for testing multiple versions"""
    matrix = {
        "node-version": ["18.x", "20.x", "21.x"],
        "os": ["ubuntu-latest", "macos-latest", "windows-latest"],
    }
    
    # Filter incompatible combinations
    exclude = [
        {"os": "windows-latest", "node-version": "18.x"}  # Example
    ]
    
    return {
        "include": [],
        "exclude": exclude,
        **matrix
    }

def generate_deployment_workflow():
    """Generate deployment workflow template"""
    workflow = {
        "name": "Deploy",
        "on": {
            "push": {"branches": ["main"]},
            "workflow_dispatch": {}
        },
        "jobs": {
            "deploy": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": "actions/checkout@v3"},
                    {
                        "uses": "actions/setup-node@v3",
                        "with": {"node-version": "20.x"}
                    },
                    {"run": "npm ci"},
                    {"run": "npm run build"},
                    {
                        "name": "Deploy to production",
                        "run": "npm run deploy",
                        "env": {"DEPLOY_KEY": "${{ secrets.DEPLOY_KEY }}"}
                    }
                ]
            }
        }
    }
    return workflow

if __name__ == "__main__":
    print(json.dumps(generate_test_matrix(), indent=2))
    print("\n---\n")
    print(json.dumps(generate_deployment_workflow(), indent=2))
