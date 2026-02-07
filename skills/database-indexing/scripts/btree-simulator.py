#!/usr/bin/env python3
"""
B-Tree Index Simulator - Visualize how B-tree indexes work.
"""

import json

def create_btree_example() -> Dict:
    """Create a simple B-tree example."""
    return {
        "tree": {
            "root": {
                "keys": [25, 50, 75],
                "children": [
                    {"keys": [5, 10, 15], "leaf": True},
                    {"keys": [30, 35, 40], "leaf": True},
                    {"keys": [60, 65, 70], "leaf": True},
                    {"keys": [80, 85, 90], "leaf": True}
                ]
            }
        },
        "properties": {
            "order": 3,
            "height": 2,
            "leaf_count": 4,
            "max_keys": 999
        },
        "search_example": {
            "query": "Find value 65",
            "steps": [
                "1. Check root node [25, 50, 75]",
                "2. 65 > 50 and < 75, go to 3rd child",
                "3. Find 65 in leaf node [60, 65, 70]",
                "4. Found! Return result",
                "Total comparisons: 4"
            ],
            "time_complexity": "O(log n)"
        }
    }

if __name__ == "__main__":
    example = create_btree_example()
    print(json.dumps(example, indent=2))
