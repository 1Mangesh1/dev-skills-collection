#!/usr/bin/env python3
"""Code Style Analyzer"""

import subprocess
import json

def analyze_code_style(file_path):
    """Analyze code style issues"""
    
    results = {
        "file": file_path,
        "issues": []
    }
    
    # Check file extension
    if file_path.endswith('.py'):
        # Run pylint
        result = subprocess.run(
            ['pylint', file_path, '--output-format=json'],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            issues = json.loads(result.stdout)
            results['issues'] = [
                {
                    'line': issue.get('line'),
                    'message': issue.get('message'),
                    'type': issue.get('type')
                }
                for issue in issues
            ]
    
    return results

def format_python():
    """Format Python files"""
    subprocess.run(['black', '.'], check=False)
    subprocess.run(['isort', '.'], check=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = analyze_code_style(sys.argv[1])
        print(json.dumps(result, indent=2))
