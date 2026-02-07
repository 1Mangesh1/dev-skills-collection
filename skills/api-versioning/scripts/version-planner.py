#!/usr/bin/env python3
"""API Versioning Strategy Planner"""

def plan_versioning_strategy(current_version, breaking_changes_needed):
    """Plan API versioning approach"""
    
    # Parse current version
    parts = current_version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    strategies = []
    
    if breaking_changes_needed:
        # Need major version bump
        new_major = major + 1
        strategies.append({
            "approach": "URL Path Versioning",
            "current": f"/api/v{major}/resource",
            "new": f"/api/v{new_major}/resource",
            "deprecation_timeline": "12 months",
            "effort": "Medium"
        })
        strategies.append({
            "approach": "Header Versioning",
            "current": f"Accept: application/vnd.api+json;version={major}",
            "new": f"Accept: application/vnd.api+json;version={new_major}",
            "deprecation_timeline": "6 months",
            "effort": "Low"
        })
    else:
        # Minor or patch version
        strategies.append({
            "approach": "Minor Version (Backward Compatible)",
            "current": f"v{major}.{minor}",
            "new": f"v{major}.{minor + 1}",
            "breaking_changes": False,
            "effort": "Low"
        })
    
    return {
        "current_version": current_version,
        "strategies": strategies,
        "recommendation": "Choose URL path versioning for clarity, support both versions for 6-12 months"
    }

if __name__ == "__main__":
    import json
    result = plan_versioning_strategy("1.0.0", True)
    print(json.dumps(result, indent=2))
