# System Prompt Engineering

## What Are System Prompts?

System prompts are special instructions sent to language models to establish their behavior, personality, expertise level, and constraints. They're separate from user messages and typically have higher priority.

## Structure of Effective System Prompts

```
1. Role/Identity: "You are a [specific role]"
2. Expertise: "With expertise in [domains]"
3. Style: "Communicate in [tone/style]"
4. Constraints: "Always [requirement]"
5. Output Format: "Respond in [format]"
```

## Example System Prompt

```
You are an expert Python developer with 10+ years of experience. 
You specialize in clean code, design patterns, and performance optimization.
Always provide:
- Well-commented code
- Explanation of trade-offs
- Performance considerations
- Test examples
Communicate in a professional but approachable tone.
```

## Key Components

### Role Definition
- "Expert" vs "Assistant" vs "Mentor" affects style
- Specify domain expertise
- Level of experience matters

### Behavioral Guidelines  
- What you should/shouldn't do
- How to handle edge cases
- Tone and formality level

### Output Specifications
- Format expectations
- Length preferences
- Structure requirements

## Testing & Iteration

1. Start with simple system prompt
2. Test with several queries
3. Note where it fails
4. Refine the prompt
5. Validate improvements

## Anti-Patterns to Avoid

- ❌ "You are ChatGPT" - models may not respond well to this
- ❌ Over-engineering - simple is often better
- ❌ Contradictory instructions
- ❌ Assuming specific model knowledge
