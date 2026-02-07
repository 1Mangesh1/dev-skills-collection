# Chain-of-Thought Prompting Guide

## What is Chain-of-Thought?

Chain-of-thought (CoT) prompting encourages language models to explain their reasoning step-by-step before providing the final answer. This typically improves performance on complex reasoning tasks.

## Basic Pattern

```
Q: [Question]
A: Let me think through this step-by-step.
1. First, I'll [step 1]
2. Then, I'll [step 2]
3. Finally, [conclusion]
```

## Example: Math Problem

```
Q: If Sarah has 5 apples and John has 3 apples, how many do they have together?
A: Let me think through this:
1. Sarah has: 5 apples
2. John has: 3 apples
3. Together: 5 + 3 = 8 apples
Answer: 8 apples
```

## Why It Works

- Models "show their work" like students do
- Easier to verify reasoning and catch errors
- Improves performance on arithmetic, logic, and commonsense reasoning
- Helps with multi-step problems

## Implementation Tips

1. Use explicit language: "Let me think step-by-step"
2. Number your steps for clarity
3. Show intermediate calculations
4. Verify each step before moving to the next
5. State assumptions explicitly

## Advanced: Self-Consistency

Generate multiple chain-of-thought paths and take the most common answer (majority voting). This further improves accuracy.

## References

- "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022)
- OpenAI Cookbook: Prompting Best Practices
