#!/usr/bin/env python3
"""
API Version Validator - Check for breaking changes between API versions.
Compares schema files and identifies backward incompatibilities.
"""

import json
from typing import Dict, List, Tuple

def compare_schemas(old_schema: Dict, new_schema: Dict) -> Dict:
    """Compare two API schemas and identify breaking changes."""
    breaking_changes = []
    deprecations = []
    additions = []
    
    # Check for removed fields
    for field in old_schema.get("properties", {}):
        if field not in new_schema.get("properties", {}):
            breaking_changes.append(f"Field '{field}' removed (breaking change)")
    
    # Check for removed endpoints
    for endpoint in old_schema.get("paths", {}):
        if endpoint not in new_schema.get("paths", {}):
            breaking_changes.append(f"Endpoint '{endpoint}' removed (breaking change)")
    
    # Check for new required fields
    for field, spec in new_schema.get("properties", {}).items():
        if field not in old_schema.get("properties", {}):
            if spec.get("required"):
                breaking_changes.append(f"Field '{field}' added as required (breaking change)")
            else:
                additions.append(f"Field '{field}' added")
    
    return {
        "breaking_changes": breaking_changes,
        "deprecations": deprecations,
        "additions": additions,
        "is_backward_compatible": len(breaking_changes) == 0,
        "severity": "CRITICAL" if len(breaking_changes) > 0 else "SAFE"
    }

def generate_migration_guide(old_version: str, new_version: str, changes: Dict) -> str:
    """Generate migration guide between versions."""
    guide = f"# Migration Guide: {old_version} → {new_version}\n\n"
    
    if changes["breaking_changes"]:
        guide += "## Breaking Changes\n"
        for change in changes["breaking_changes"]:
            guide += f"- {change}\n"
        guide += "\n"
    
    if changes["deprecations"]:
        guide += "## Deprecations\n"
        for dep in changes["deprecations"]:
            guide += f"- {dep}\n"
        guide += "\n"
    
    guide += "## Migration Steps\n"
    guide += "1. Review breaking changes\n"
    guide += "2. Update client code\n"
    guide += "3. Test with new version\n"
    guide += "4. Deploy updated client\n"
    
    return guide

if __name__ == "__main__":
    import sys
    schema_file = sys.argv[1] if len(sys.argv) > 1 else "schema.json"
    with open(schema_file) as f:
        schema = json.load(f)
    print(json.dumps(schema, indent=2))
