# Prompt Engineering Foundations

## Core Concepts

### Token and Context Length
- Models process text as tokens (typically 1 token ≈ 4 characters)
- Each model has a max context window (Claude 3: 100K tokens, GPT-4: 8K-128K)
- Optimize prompt + context to stay within limits

### Temperature and Top-P
- **Temperature** (0-2): Randomness of responses
  - 0: Deterministic, focused
  - 1: Balanced (default)
  - 2: Creative, diverse
- **Top-P** (0-1): Diversity of token selection
  - Lower = more focused
  - Higher = more diverse

### Stop Sequences
- Tokens that tell model when to stop generating
- Example: stopping at "\n" for single-line responses
- Reduces token usage and control outputs

## Best Practices

### 1. Be Specific
- ❌ "Write code"
- ✅ "Write a Python function that validates email addresses using regex"

### 2. Provide Context
- Explain the why, not just the what
- Give examples of good/bad outputs
- Mention constraints and requirements

### 3. Use Clear Structure
- Role: "You are a senior developer"
- Task: "Write clean, documented code"
- Context: "For a microservices architecture"
- Format: "Response in JSON with code"

### 4. Iterate and Refine
- Test prompts with variations
- Measure quality of responses
- Document what works best

##Testing Prompts Systematically

Track these metrics:
- **Accuracy**: Does output match requirements?
- **Consistency**: Does model produce similar quality repeatedly?
- **Speed**: Does prompt generate response quickly?
- **Cost**: Tokens used for the prompt and response
