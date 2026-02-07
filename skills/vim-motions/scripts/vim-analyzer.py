#!/usr/bin/env python3
"""Vim Motion Generator & Analyzer"""

import re

def parse_vim_motions(motions_text):
    """Parse vim motions from text"""
    lines = motions_text.strip().split('\n')
    motions = {}
    
    for line in lines:
        if line.strip() and not line.startswith('==='):
            parts = line.split(None, 1)
            if len(parts) == 2:
                motion, description = parts
                motions[motion] = description
    
    return motions

def suggest_motion(action):
    """Suggest vim motion for action"""
    actions = {
        "delete line": "dd",
        "copy word": "yw",
        "change word": "cw",
        "select to end": "v$",
        "go to line": "G",
        "search": "/pattern",
        "replace": ":s/old/new/",
    }
    
    return actions.get(action.lower(), "Unknown action")

def motion_efficiency_score(vim_command):
    """Score vim command for efficiency (fewer keystrokes)"""
    # Shorter commands are more efficient
    efficiency = 10 / len(vim_command)
    return round(efficiency, 2)

if __name__ == "__main__":
    # Test motion suggestion
    print(suggest_motion("delete line"))
    print(f"Efficiency score for 'dd': {motion_efficiency_score('dd')}")
