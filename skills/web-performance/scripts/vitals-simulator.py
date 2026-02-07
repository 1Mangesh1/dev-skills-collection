#!/usr/bin/env python3
"""Core Web Vitals Simulator"""

import json
import random

def simulate_web_vitals():
    """Simulate Core Web Vitals measurements"""
    
    return {
        "lcp": {
            "name": "Largest Contentful Paint",
            "value": round(random.uniform(1.0, 3.5), 2),
            "unit": "seconds",
            "threshold_good": 2.5,
            "status": "good" if random.uniform(0, 1) > 0.3 else "needs_improvement"
        },
        "fid": {
            "name": "First Input Delay",
            "value": round(random.uniform(50, 500), 0),
            "unit": "milliseconds",
            "threshold_good": 100,
            "status": "good" if random.uniform(0, 1) > 0.3 else "needs_improvement"
        },
        "cls": {
            "name": "Cumulative Layout Shift",
            "value": round(random.uniform(0.05, 0.25), 3),
            "unit": "score (0-1)",
            "threshold_good": 0.1,
            "status": "good" if random.uniform(0, 1) > 0.3 else "needs_improvement"
        },
        "recommendations": [
            "Optimize image loading with lazy-loading",
            "Minify JavaScript bundles",
            "Use Code Splitting for routes",
            "Enable GZIP compression on server"
        ]
    }

if __name__ == "__main__":
    result = simulate_web_vitals()
    print(json.dumps(result, indent=2))
