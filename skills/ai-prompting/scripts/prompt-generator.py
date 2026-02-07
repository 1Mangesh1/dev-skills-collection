#!/usr/bin/env python3
"""
Prompt Template Generator - Create optimized prompt templates.
Generates tested templates for common AI interaction patterns.
"""

import json

prompt_templates = {
    "classification": {
        "name": "Classification Prompt",
        "template": """You are a classifier expert.

Classify the following input into one of these categories: {categories}

Input: {input}

Respond in JSON format with:
- category: (the selected category)
- confidence: (0.0-1.0)
- reasoning: (brief explanation)""",
        "use_case": "Categorizing inputs into predefined classes",
        "example_vars": {
            "categories": "positive, negative, neutral",
            "input": "This product exceeded my expectations!"
        }
    },
    
    "few_shot": {
        "name": "Few-Shot Learning",
        "template": """You are an expert {domain}.

Learn from these examples:

Example 1:
Input: {example1_input}
Output: {example1_output}

Example 2:
Input: {example2_input}
Output: {example2_output}

Now apply this pattern to:
Input: {new_input}
Output:""",
        "use_case": "Demonstrating patterns with examples",
        "example_vars": {
            "domain": "prompt engineer",
            "example1_input": "code in Python",
            "example1_output": "def hello(): print('Hello')",
            "example2_input": "code in JavaScript",
            "example2_output": "function hello() { console.log('Hello'); }",
            "new_input": "code in Go"
        }
    },
    
    "chain_of_thought": {
        "name": "Chain-of-Thought",
        "template": """Problem: {problem}

Let me think through this step by step:

Step 1: Identify the key components
Step 2: Analyze each component
Step 3: Connect the components
Step 4: Arrive at the conclusion

Please explain your reasoning for each step.""",
        "use_case": "Complex reasoning and problem-solving",
        "example_vars": {
            "problem": "Why do some APIs require versioning and others don't?"
        }
    },
    
    "system_prompt": {
        "name": "System Prompt Design",
        "template": """You are a {role} with expertise in {domain}.

Your responsibilities:
- {responsibility1}
- {responsibility2}
- {responsibility3}

Guidelines:
- Respond in {response_format}
- Be {tone}
- Include {details}

User request: {request}""",
        "use_case": "Defining AI assistant behavior",
        "example_vars": {
            "role": "senior developer",
            "domain": "microservices architecture",
            "responsibility1": "Provide scalable solutions",
            "responsibility2": "Consider failure scenarios",
            "responsibility3": "Explain trade-offs",
            "response_format": "JSON with code examples",
            "tone": "helpful and thorough",
            "details": "implementation details and references",
            "request": "Design an API gateway for our services"
        }
    }
}

def generate_template(template_name: str) -> Dict:
    """Get a template by name."""
    template = prompt_templates.get(template_name)
    return template if template else {"error": f"Template '{template_name}' not found"}

def list_templates():
    """List all available templates."""
    return {
        "templates": list(prompt_templates.keys()),
        "count": len(prompt_templates)
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(json.dumps(list_templates(), indent=2))
    else:
        template_name = sys.argv[1]
        result = generate_template(template_name)
        print(json.dumps(result, indent=2))
