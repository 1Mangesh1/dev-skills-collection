#!/usr/bin/env python3
"""Markdown Time Estimator"""

import subprocess
import sys

def estimate_read_time(file_path):
    """Estimate reading time for markdown file"""
    
    try:
        with open(file_path) as f:
            content = f.read()
        
        # Remove markdown syntax
        text = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "plain"],
            input=content,
            capture_output=True,
            text=True
        ).stdout
        
        word_count = len(text.split())
        read_time_minutes = max(1, word_count // 200)  # ~200 words per minute
        
        print(f"📄 {file_path}")
        print(f"   Words: {word_count}")
        print(f"   Estimated read time: {read_time_minutes} min")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        estimate_read_time(sys.argv[1])
    else:
        print("Usage: python markdown-stats.py <file.md>")
