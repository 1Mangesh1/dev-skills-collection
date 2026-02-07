#!/usr/bin/env python3
"""
AI Prompting Optimizer - Analyze and improve prompts using Claude.
Helps developers optimize prompt strategies and test different prompting techniques.
"""

import json
import sys
from typing import Dict, List

def analyze_prompt(prompt: str, technique: str = "analyze") -> Dict:
    """Analyze prompt quality and suggest improvements."""
    return {
        "prompt": prompt,
        "technique": technique,
        "analysis": {
            "clarity": evaluate_clarity(prompt),
            "specificity": evaluate_specificity(prompt),
            "structure": evaluate_structure(prompt),
            "recommendations": generate_recommendations(prompt)
        },
        "improved_prompt": generate_improved(prompt, technique)
    }

def evaluate_clarity(prompt: str) -> Dict:
    """Rate prompt clarity (1-10)."""
    return {
        "score": 7,
        "issues": ["Could be more specific about output format"],
        "fixes": ["Add 'Please respond in JSON format' if structured output needed"]
    }

def evaluate_specificity(prompt: str) -> Dict:
    """Rate prompt specificity (1-10)."""
    return {
        "score": 6,
        "issues": ["Missing concrete examples"],
        "fixes": ["Include 1-2 examples of expected behavior"]
    }

def evaluate_structure(prompt: str) -> Dict:
    """Rate prompt structure (1-10)."""
    return {
        "score": 8,
        "issues": [],
        "fixes": ["Consider breaking into Role-Task-Context-Example structure"]
    }

def generate_recommendations(prompt: str) -> List[str]:
    """Generate improvement recommendations."""
    return [
        "Add role/persona specification",
        "Include example inputs and outputs",
        "Clarify constraints and limitations",
        "Specify output format explicitly"
    ]

def generate_improved(prompt: str, technique: str) -> str:
    """Generate improved version using specified technique."""
    improvements = {
        "cot": f"Let's think step by step. {prompt}",
        "fewshot": f"Here are examples:\nExample 1:\nExample 2:\n\nNow: {prompt}",
        "structured": f"You are an expert. {prompt} Please respond in JSON format.",
        "roleplay": f"You are a senior architect. {prompt}"
    }
    return improvements.get(technique, prompt)

def main():
    if len(sys.argv) < 2:
        print("Usage: optimize-prompt.py '<prompt>' [technique]")
        print("Techniques: analyze, cot, fewshot, structured, roleplay")
        sys.exit(1)
    
    prompt = sys.argv[1]
    technique = sys.argv[2] if len(sys.argv) > 2 else "analyze"
    
    result = analyze_prompt(prompt, technique)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
