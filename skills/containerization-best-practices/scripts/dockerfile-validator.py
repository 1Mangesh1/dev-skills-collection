#!/usr/bin/env python3
"""Dockerfile Best Practices Validator"""

import json

def validate_dockerfile(dockerfile_content):
    """Validate Dockerfile follows best practices"""
    
    issues = []
    
    # Check for multi-stage build
    if "AS" not in dockerfile_content and "base" not in dockerfile_content.lower():
        issues.append({
            "severity": "HIGH",
            "rule": "Use multi-stage builds",
            "benefit": "Reduces image size by 50-90%"
        })
    
    # Check for FROM latest
    if "FROM" in dockerfile_content and "latest" in dockerfile_content:
        issues.append({
            "severity": "MEDIUM",
            "rule": "Specify base image version",
            "fix": "Use specific version tag (e.g., node:18-alpine not node:latest)"
        })
    
    # Check for RUN npm install without caching
    if "npm install" in dockerfile_content and "package*.json" not in dockerfile_content:
        issues.append({
            "severity": "MEDIUM",
            "rule": "Copy package files before sources",
            "benefit": "Better Docker layer caching"
        })
    
    # Check for USER
    if "USER" not in dockerfile_content:
        issues.append({
            "severity": "HIGH",
            "rule": "Run as non-root user",
            "security": "Reduces attack surface"
        })
    
    score = 100 - (len(issues) * 15)
    
    return {
        "validation_result": "NEEDS IMPROVEMENT" if score < 70 else "GOOD",
        "score": max(0, score),
        "issues": issues,
        "recommendations": [
            "Use Alpine-based images for smaller footprint",
            ".dockerignore to exclude unnecessary files",
            "Multi-stage builds to separate build and runtime",
            "Leverage layer caching efficiently"
        ]
    }

if __name__ == "__main__":
    sample_dockerfile = """
    FROM node:latest
    COPY . /app
    WORKDIR /app
    RUN npm install
    CMD ["npm", "start"]
    """
    
    result = validate_dockerfile(sample_dockerfile)
    print(json.dumps(result, indent=2))
