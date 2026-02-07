#!/usr/bin/env python3
"""Changelog Validator and Formatter"""

import re
import sys

def validate_changelog(filepath):
    """Validate changelog format"""
    with open(filepath) as f:
        content = f.read()
    
    issues = []
    
    # Check structure
    if not re.search(r'^# Changelog', content, re.MULTILINE):
        issues.append("Missing '# Changelog' header")
    
    # Check version format
    versions = re.findall(r'## \[(.+?)\]', content)
    for version in versions:
        if not re.match(r'^\d+\.\d+\.\d+', version):
            issues.append(f"Invalid version format: {version}")
    
    # Check dates
    if not re.search(r'\d{4}-\d{2}-\d{2}', content):
        issues.append("No dates found in YYYY-MM-DD format")
    
    if issues:
        print("❌ Changelog validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ Changelog is valid")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python changelog-validator.py <changelog_file>")
        sys.exit(1)
    
    validate_changelog(sys.argv[1])
