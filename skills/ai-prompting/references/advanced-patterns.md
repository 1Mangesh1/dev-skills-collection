# Advanced Prompting Patterns

## Prompt Composition Patterns

### 1. Role-Based Prompting
Assign an expert persona to improve response quality.

```
"You are a senior software architect with 15 years of experience 
in microservices and distributed systems.

A team asks: 'How do we design our API gateway?'"
```

**When to use**: Complex decisions, best practices, trade-offs

### 2. Constraint-Based Prompting
Define limitations to focus responses.

```
"Explain the concept of eventual consistency.

Constraints:
- Maximum 100 words
- No citations, use your knowledge
- Explain to a beginner"
```

**When to use**: Length requirements, specific audiences

### 3. Comparative Prompting
Ask model to compare options.

```
"Compare SQL and NoSQL databases for:
- User profiles (< 10KB, frequent updates)
- Event logs (time-series, high volume)

Include: pros/cons, recommendations"
```

**When to use**: Decision making, evaluations

### 4. Hypothetical/Simulation
Test how model handles scenarios.

```
"Imagine you're designing a database for 1M daily users.
What challenges would you face?
What database would you choose and why?"
```

**When to use**: Planning, exploration, creative problem-solving

### 5. Feedback-Based Iteration
Refine outputs through iterative refinement.

```
1. Initial: "Write a Python function for..."
2. Feedback: "Make it more efficient"
3. Feedback: "Add error handling"
4. Feedback: "Add docstring"
```

**When to use**: Fine-tuning outputs, collaboration style work

## Anti-Patterns to Avoid

❌ **Vague requests**: "Tell me about databases"
✅ **Specific requests**: "Explain how B-tree indexes speed up range queries"

❌ **Long context, unclear goal**: "Here's 5 pages... what do you think?"
✅ **Clear goal**: "Summarize the security concerns in this architecture"

❌ **Inconsistent format**: "I want JSON... actually CSV... wait, markdown"
✅ **Consistent format**: "Always respond in JSON with keys: ..."

❌ **No examples**: "Write code that's good"
✅ **With examples**: "Write code like this [example]. Improve on this [previous attempt]"
