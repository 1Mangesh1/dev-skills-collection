# Prompt Techniques Comparison

## Technique Overview

| Technique | Best For | Complexity | Examples |
|-----------|----------|-----------|----------|
| **Direct** | Simple, straightforward tasks | Low | "Translate to Spanish" |
| **Few-Shot** | Pattern demonstration | Medium | Code generation, classification |
| **Chain-of-Thought** | Reasoning, problem solving | Medium | Math, logic, analysis |
| **System Prompt** | Behavior definition | High | AI assistant personality |
| **Structured** | Consistent output format | Medium | JSON, forms, reports |

## Technique Details

### 1. Direct Prompting
```
"Translate 'Hello world' to French"
```
- Fastest response
- Best for simple requests
- May lack depth on complex tasks

### 2. Few-Shot Prompting
```
"Classify sentiment. Examples:
- 'Great product!' → positive
- 'Broken item' → negative

Now classify: 'Works perfectly'"
```
- Shows expected behavior
- Improves consistency
- Reduces error rates

### 3. Chain-of-Thought (CoT)
```
"Let's solve this step by step:
1. Identify the components
2. Break down the problem
3. Work through each part
4. Synthesize the answer

Problem: ..."
```
- Improves reasoning accuracy
- Shows work
- Better for complex logic

### 4. System Prompts + User Prompts
```
System: "You are a Python expert helping beginners"
User: "How do I read a file?"
```
- Defines persistent behavior
- Builds context
- More reliable responses

## Effectiveness by Domain

### Code Generation
- **Best**: Few-shot + structured
- Show code examples in desired style
- Specify language and requirements

### Content Writing
- **Best**: System prompt + direct
- Define tone and audience in system prompt
- Keep instructions concise

### Analysis & Reasoning
- **Best**: Chain-of-thought
- Ask for step-by-step explanation
- Request evidence for claims

### Classification
- **Best**: Few-shot
- Provide 2-3 examples per category
- Show edge cases
