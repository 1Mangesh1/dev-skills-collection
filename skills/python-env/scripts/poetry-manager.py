#!/usr/bin/env python3
"""Poetry Dependency Manager"""

import subprocess
import json

def create_poetry_project(name):
    """Create a new Poetry project"""
    subprocess.run(['poetry', 'new', name], check=True)

def init_poetry():
    """Initialize Poetry in current directory"""
    subprocess.run(['poetry', 'init', '--no-interaction'], check=True)

def add_dependency(package_name, version=None):
    """Add a new dependency"""
    cmd = ['poetry', 'add', package_name]
    if version:
        cmd[-1] += f'=={version}'
    
    subprocess.run(cmd, check=True)

def export_requirements():
    """Export requirements.txt from poetry.lock"""
    result = subprocess.run(
        ['poetry', 'export', '-f', 'requirements.txt', '-o', 'requirements.txt'],
        check=True
    )

if __name__ == "__main__":
    print("Poetry dependency management utilities loaded")
