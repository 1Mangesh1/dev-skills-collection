#!/usr/bin/env python3
"""
AI Prompt Optimizer
Analyzes and suggests improvements for LLM prompts
"""

import json
import sys
from typing import Dict, List

def analyze_prompt(prompt: str) -> Dict:
    """Analyze prompt quality and suggest improvements"""
    issues = []
    score = 100
    
    # Check for clear role definition
    if "role:" not in prompt.lower() and "as a" not in prompt.lower():
        issues.append({
            "type": "missing_role",
            "severity": "medium",
            "suggestion": "Add role/expertise definition (e.g., 'You are a...')"
        })
        score -= 10
    
    # Check for specific task
    if len(prompt.split()) < 5:
        issues.append({
            "type": "too_vague",
            "severity": "high",
            "suggestion": "Provide more specific, detailed task description"
        })
        score -= 20
    
    # Check for context
    if "context" not in prompt.lower() and "background" not in prompt.lower():
        issues.append({
            "type": "missing_context",
            "severity": "low",
            "suggestion": "Add relevant context for better response quality"
        })
        score -= 5
    
    # Check for format specification
    if "format" not in prompt.lower() and "output" not in prompt.lower():
        issues.append({
            "type": "no_format_spec",
            "severity": "low",
            "suggestion": "Specify desired output format (JSON, markdown, etc.)"
        })
        score -= 5
    
    return {
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "quality_score": max(0, score),
        "issues": issues,
        "recommendation": "Excellent prompt" if score >= 80 else "Good prompt - consider improvements" if score >= 60 else "Needs improvement"
    }

def main():
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:])
    else:
        prompt_text = input("Enter your prompt: ")
    
    result = analyze_prompt(prompt_text)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
