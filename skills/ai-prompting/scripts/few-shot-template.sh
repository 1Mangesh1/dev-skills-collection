#!/usr/bin/env bash
# Few-Shot Prompt Generator
# Creates few-shot examples template for LLM prompting

cat << 'EOF'
# Few-Shot Prompt Template

## System Prompt
You are an expert assistant trained to [TASK].

## Examples

### Example 1
Input: [sample input 1]
Output: [sample output 1]

### Example 2  
Input: [sample input 2]
Output: [sample output 2]

### Example 3
Input: [sample input 3]
Output: [sample output 3]

## Now Complete This Task
Input: [user's actual input]
Output:
EOF
