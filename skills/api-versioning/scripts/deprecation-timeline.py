#!/usr/bin/env python3
"""
Deprecation Timeline Manager - Track API version lifecycles.
"""

import json
from datetime import datetime, timedelta

def create_deprecation_timeline(current_version: str, new_version: str) -> Dict:
    """Create deprecation timeline for version transition."""
    today = datetime.now()
    
    timeline = {
        "current_version": current_version,
        "new_version": new_version,
        "timeline": {
            "announcement": today.isoformat(),
            "grace_period_start": today.isoformat(),
            "grace_period_end": (today + timedelta(days=180)).isoformat(),
            "deprecation_date": (today + timedelta(days=180)).isoformat(),
            "sunset_date": (today + timedelta(days=365)).isoformat()
        },
        "actions": {
            "immediate": [
                "Announce deprecation in release notes",
                "Update documentation",
                "Add deprecation headers to API responses"
            ],
            "month_1": [
                "Send email to active users",
                "Publish migration guide",
                "Provide migration tools"
            ],
            "month_6": [
                "Start returning HTTP 410 Gone for v1 endpoints",
                "Increase warning frequency"
            ],
            "month_12": [
                "Completely shutdown old version",
                "Archive related documentation"
            ]
        }
    }
    return timeline

if __name__ == "__main__":
    timeline = create_deprecation_timeline("v1", "v2")
    print(json.dumps(timeline, indent=2))
