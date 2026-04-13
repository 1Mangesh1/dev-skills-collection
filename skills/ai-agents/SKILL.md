---
name: ai-agents
description: Building AI agents — tool use, chains, memory, and autonomous workflows with LLMs. Use when user mentions "AI agent", "agent development", "tool use", "function calling", "agent loop", "ReAct pattern", "agent memory", "autonomous agent", "multi-agent", "langchain agents", "crew AI", or building systems where LLMs take actions.
---

# AI Agents

An AI agent is an LLM connected to tools and running in a loop. The LLM decides what to do, calls a tool, observes the result, and repeats until the task is done. Without the loop and tools, it is just a chatbot.

## Core Agent Loop

Every agent follows this pattern:

```
1. OBSERVE  - Receive input (user message or tool result)
2. THINK    - LLM reasons about what to do next
3. ACT      - Call a tool or return a final answer
4. OBSERVE  - Get tool result, go back to step 2
```

The loop terminates when the LLM decides no more tool calls are needed and returns a final response. A maximum iteration limit prevents runaway loops.

## Tool / Function Calling

### OpenAI Format

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

### Anthropic Format

```python
tools = [
    {
        "name": "search_web",
        "description": "Search the web for a query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=messages,
    tools=tools
)
```

The model returns a `tool_use` block (Anthropic) or `tool_calls` array (OpenAI). Your code executes the tool and feeds the result back as the next message.

## ReAct Pattern (Reasoning + Acting)

ReAct interleaves reasoning traces with actions. The LLM explicitly writes out its thinking before each tool call, making the decision process inspectable.

```
Thought: I need to find the current stock price of AAPL.
Action: search_web("AAPL stock price")
Observation: AAPL is trading at $187.44.
Thought: I have the price. I can answer the user now.
Answer: Apple (AAPL) is currently trading at $187.44.
```

With modern tool-calling APIs, ReAct happens naturally -- the model reasons in its text output and issues tool calls in structured blocks. You do not need to parse "Action:" strings from raw text anymore.

## Minimal Agent in Python

No frameworks. Just API calls and a tool dispatch dictionary.

```python
import anthropic
import json

client = anthropic.Anthropic()

# Define tools
def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    with open(path, "w") as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"

tool_definitions = [
    {
        "name": "read_file",
        "description": "Read a file from disk",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]

dispatch = {
    "read_file": lambda args: read_file(args["path"]),
    "write_file": lambda args: write_file(args["path"], args["content"]),
}

def run_agent(user_message: str, max_iterations: int = 10):
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tool_definitions,
            messages=messages,
        )

        # Append assistant response
        messages.append({"role": "assistant", "content": response.content})

        # Check if the model wants to use tools
        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_blocks:
            # No tool calls -- agent is done
            text = "".join(b.text for b in response.content if b.type == "text")
            return text

        # Execute each tool and collect results
        tool_results = []
        for block in tool_blocks:
            try:
                result = dispatch[block.name](block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
            except Exception as e:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                })

        messages.append({"role": "user", "content": tool_results})

    return "Agent hit max iterations without completing."
```

## Minimal Agent in TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: "search_web",
    description: "Search the web",
    input_schema: {
      type: "object" as const,
      properties: { query: { type: "string" } },
      required: ["query"],
    },
  },
];

async function executeTool(name: string, input: Record<string, unknown>): Promise<string> {
  if (name === "search_web") {
    // Replace with real implementation
    return `Results for: ${input.query}`;
  }
  throw new Error(`Unknown tool: ${name}`);
}

async function runAgent(userMessage: string, maxIterations = 10): Promise<string> {
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];

  for (let i = 0; i < maxIterations; i++) {
    const response = await client.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      tools,
      messages,
    });

    messages.push({ role: "assistant", content: response.content });

    const toolBlocks = response.content.filter(
      (b): b is Anthropic.ToolUseBlock => b.type === "tool_use"
    );

    if (toolBlocks.length === 0) {
      return response.content
        .filter((b): b is Anthropic.TextBlock => b.type === "text")
        .map((b) => b.text)
        .join("");
    }

    const toolResults: Anthropic.ToolResultBlockParam[] = await Promise.all(
      toolBlocks.map(async (block) => {
        try {
          const result = await executeTool(block.name, block.input as Record<string, unknown>);
          return { type: "tool_result" as const, tool_use_id: block.id, content: result };
        } catch (e) {
          return {
            type: "tool_result" as const,
            tool_use_id: block.id,
            content: `Error: ${e}`,
            is_error: true,
          };
        }
      })
    );

    messages.push({ role: "user", content: toolResults });
  }

  return "Agent hit max iterations.";
}
```

## Memory Patterns

### Conversation History (Short-Term)

Pass the full message array to each API call. This is the simplest form of memory but hits context window limits on long conversations.

### Summarization (Medium-Term)

When the conversation grows too long, summarize older messages. Keep the system prompt and last few exchanges intact, replace everything in between with a summary generated by a separate LLM call.

### Vector Store Retrieval (Long-Term)

Store past interactions or documents as embeddings. Before each LLM call, retrieve the top-k relevant chunks and inject them into the prompt. Use any vector database (Pinecone, ChromaDB, pgvector, Qdrant).

## Multi-Agent Patterns

**Supervisor**: One coordinating agent delegates subtasks to specialist agents and synthesizes their outputs.

**Debate / Critique**: Two agents review each other's work. Agent A drafts, Agent B critiques, Agent A revises. Improves output quality at the cost of more API calls.

**Pipeline**: Agents are chained sequentially. Agent 1 researches, Agent 2 writes, Agent 3 reviews. Each agent sees only the output of the previous stage.

**Parallel Fan-Out**: A router sends independent subtasks to multiple agents simultaneously, then merges results.

## Common Tools to Give Agents

| Tool | Use Case |
|------|----------|
| Web search | Grounding in current information |
| Code execution (sandbox) | Running Python/JS to verify answers |
| File read/write | Persisting work products |
| Shell commands | System operations, git, builds |
| API calls (HTTP) | Interacting with external services |
| Database queries | Reading/writing structured data |
| Browser automation | Scraping, form filling |

Keep tool descriptions concise and specific. Vague descriptions cause the model to misuse tools.

## Error Handling and Retry Strategies

1. **Catch tool errors** and return them to the LLM as error messages (see `is_error: true` in examples above). The model can often self-correct.
2. **Retry on transient failures** (rate limits, network errors) with exponential backoff.
3. **Set a max iteration limit** to prevent infinite loops. 10-20 is typical.
4. **Validate tool inputs** before execution. If the model passes invalid arguments, return a clear error describing the expected format.
5. **Timeout individual tool calls**. A hung web request should not stall the entire agent.

## Token Management

- **Track token usage** from API response metadata (`usage.input_tokens`, `usage.output_tokens`).
- **Prune conversation history** when approaching the context window limit. Keep the system prompt, recent messages, and a summary of older ones.
- **Use prompt caching** (Anthropic) or cached completions (OpenAI) for repeated prefixes. This reduces cost on long conversations.
- **Limit tool output size**. Truncate large file contents or API responses before feeding them back.
- **Choose model by task**. Use a smaller/cheaper model for simple tool dispatch and a larger model for complex reasoning steps.

## Guardrails

### Input Validation

Validate user inputs before they reach the agent. Check for prompt injection attempts, excessively long inputs, and disallowed content.

### Output Filtering

Check agent outputs before returning to the user or executing dangerous operations:

```python
BLOCKED_COMMANDS = ["rm -rf /", "DROP TABLE", "FORMAT C:"]

def validate_tool_call(name: str, args: dict) -> bool:
    if name == "run_shell":
        cmd = args.get("command", "")
        if any(blocked in cmd for blocked in BLOCKED_COMMANDS):
            return False
    return True
```

### Human-in-the-Loop

For high-stakes actions (sending emails, making purchases, modifying production data), pause and ask for human approval before executing the tool. Return a rejection message to the LLM if the user declines.

## Frameworks Overview

| Framework | Language | Key Strength |
|-----------|----------|-------------|
| LangChain | Python/JS | Large ecosystem, many integrations |
| LangGraph | Python/JS | Stateful, graph-based agent workflows |
| CrewAI | Python | Multi-agent role-based collaboration |
| AutoGen | Python | Multi-agent conversation patterns |
| Claude Agent SDK | Python | Lightweight agent loop with Claude |
| Vercel AI SDK | TypeScript | Streaming-first, React integration |
| Mastra | TypeScript | Agent framework with built-in memory/tools |

Start without a framework. Add one when you need features you are reimplementing (state persistence, complex routing, built-in tool libraries). Frameworks add abstraction layers that make debugging harder.

## Evaluation

Testing agents is harder than testing deterministic code. Strategies:

1. **Unit test individual tools**. Each tool function should be testable in isolation.
2. **Golden path tests**. Define input/expected-output pairs and check that the agent reaches the correct final answer. Allow for variation in intermediate steps.
3. **Tool call assertions**. Verify the agent called the right tools in a reasonable order, even if the exact arguments vary.
4. **Adversarial inputs**. Test with confusing, ambiguous, or adversarial prompts to verify guardrails hold.
5. **Cost tracking**. Log token usage per test case. A test that suddenly uses 10x more tokens indicates a regression in agent efficiency.
6. **Human evaluation**. For open-ended tasks, have humans rate agent outputs on correctness, helpfulness, and safety.

```python
def test_research_agent():
    result = run_agent("What is the population of Tokyo?")
    assert "13" in result or "14" in result  # millions, approximately
    # Check that web search was called
    assert any("search_web" in str(m) for m in recorded_messages)
```

## Common Agent Patterns

### Research Agent

Tools: web search, URL reader, note-taking. The agent searches for information, reads pages, extracts facts, and compiles a report. Useful for market research, literature review, competitive analysis.

### Coding Agent

Tools: file read/write, shell execution, web search. The agent reads existing code, plans changes, writes code, runs tests, and iterates on failures. Key design decision: sandbox the execution environment.

### Data Analysis Agent

Tools: code execution (Python with pandas/numpy), file read, chart generation. The agent loads data, explores it, runs statistical analysis, and generates visualizations. Give it a Python sandbox with data science libraries pre-installed.

### Customer Support Agent

Tools: knowledge base search, ticket system API, escalation. The agent retrieves relevant documentation, answers questions, and escalates when confidence is low or the request requires human judgment.

### Workflow Automation Agent

Tools: email, calendar, project management APIs. The agent performs multi-step business processes (schedule meetings, send follow-ups, update tasks). Always use human-in-the-loop for actions with external side effects.
