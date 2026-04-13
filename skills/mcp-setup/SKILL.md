---
name: mcp-setup
description: Model Context Protocol (MCP) server setup, configuration, and custom server development for Claude Code, Claude Desktop, Cursor, and VS Code. Use when asked to "setup MCP", "configure MCP server", "add MCP tools", "connect to MCP", "create MCP server", "build MCP tool", "debug MCP", "MCP transport", "MCP authentication", "MCP inspector", "list MCP servers", or integrate external tools via MCP protocol.
---

# MCP Setup

## Protocol Overview

MCP is an open standard connecting AI models to external tools, data, and services via JSON-RPC 2.0. Architecture: **Host** (app running the model) creates a **Client** that connects 1:1 to a **Server** exposing capabilities.

Three primitives a server can expose:
- **Tools** - functions the model can call (like API endpoints)
- **Resources** - data the model can read (files, DB records, configs)
- **Prompts** - reusable prompt templates with arguments

## Configuration by Client

### Claude Desktop

```
macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json
Windows: %APPDATA%\Claude\claude_desktop_config.json
Linux:   ~/.config/Claude/claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxx" }
    }
  }
}
```

### Claude Code

Project-scoped `.mcp.json` at project root. Manage via CLI:

```bash
claude mcp add my-server npx -y @some/mcp-server
claude mcp add db-server -e DATABASE_URL=postgresql://... -- npx -y @modelcontextprotocol/server-postgres
claude mcp list
claude mcp remove my-server
```

### Cursor

`.cursor/mcp.json` at project root or `~/.cursor/mcp.json` globally. Same `mcpServers` format as Claude Desktop.

### VS Code (Copilot)

In `.vscode/mcp.json` (supports input variables for secrets):

```json
{
  "servers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@some/server"],
      "env": { "API_KEY": "${input:api-key}" }
    }
  },
  "inputs": [{ "id": "api-key", "type": "promptString", "password": true }]
}
```

## Popular MCP Servers

### Filesystem

```json
{ "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"] } }
```

Tools: `read_file`, `write_file`, `list_directory`, `search_files`, `move_file`.

### Git

```json
{ "git": { "command": "uvx", "args": ["mcp-server-git", "--repository", "/path/to/repo"] } }
```

Tools: `git_log`, `git_diff`, `git_status`, `git_commit`, `git_branch`.

### PostgreSQL

```json
{ "postgres": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"] } }
```

Read-only `query` tool. Exposes table schemas as resources.

### SQLite

```json
{ "sqlite": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "/path/to/db.sqlite"] } }
```

Tools: `read_query`, `write_query`, `create_table`, `list_tables`, `describe_table`.

### Brave Search

```json
{ "brave-search": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": { "BRAVE_API_KEY": "key" } } }
```

Tools: `brave_web_search`, `brave_local_search`.

### Puppeteer

```json
{ "puppeteer": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-puppeteer"] } }
```

Tools: `puppeteer_navigate`, `puppeteer_screenshot`, `puppeteer_click`, `puppeteer_fill`, `puppeteer_evaluate`.

### Sequential Thinking

```json
{ "sequential-thinking": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"] } }
```

Provides `sequentialthinking` tool for structured multi-step reasoning.

### GitHub

```json
{ "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"], "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxx" } } }
```

### Slack

```json
{ "slack": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-slack"], "env": { "SLACK_BOT_TOKEN": "xoxb-xxxx", "SLACK_TEAM_ID": "T12345" } } }
```

## Building Custom Servers (TypeScript)

```bash
npm init -y && npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.tool("lookup_user", "Find user by email", { email: z.string().email() },
  async ({ email }) => ({
    content: [{ type: "text", text: JSON.stringify(await db.findUser(email)) }],
  })
);

server.resource("config", "config://app", async (uri) => ({
  contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(config) }],
}));

server.prompt("review-code", { code: z.string() }, ({ code }) => ({
  messages: [{ role: "user", content: { type: "text", text: `Review:\n${code}` } }],
}));

await server.connect(new StdioServerTransport());
```

## Building Custom Servers (Python)

```bash
pip install mcp   # or: uv add mcp
```

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def lookup_user(email: str) -> str:
    """Find user by email address."""
    return json.dumps(db.find_user(email))

@mcp.resource("config://app")
def get_config() -> str:
    """Application configuration."""
    return json.dumps(config)

@mcp.prompt()
def review_code(code: str) -> str:
    """Generate a code review prompt."""
    return f"Review this code:\n{code}"

if __name__ == "__main__":
    mcp.run()  # stdio by default; mcp.run(transport="sse") for SSE
```

## Tool Definitions

Every tool needs name, description, and JSON Schema input:

```json
{
  "name": "create_ticket",
  "description": "Create a support ticket. Returns ticket ID.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": { "type": "string", "description": "Short summary" },
      "priority": { "type": "string", "enum": ["low", "medium", "high", "critical"] },
      "labels": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["title", "priority"]
  }
}
```

Tips: describe when/why to use the tool (not just what); use `enum` for constrained values; return structured JSON so the model can reason about results.

## Transport Mechanisms

**stdio** (default) - server runs as subprocess, client writes JSON-RPC to stdin/reads stdout. Best for local tools. Zero network surface.

**SSE** (Server-Sent Events) - server runs HTTP. Client GETs `/sse` for events, POSTs `/messages` for requests. Good for remote servers.

**Streamable HTTP** - newer transport replacing SSE. Single HTTP endpoint, supports both request-response and streaming. Preferred for new remote deployments.

```typescript
// stdio
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
await server.connect(new StdioServerTransport());

// SSE
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

// Streamable HTTP
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
```

## Authentication

**Environment variables** (local stdio servers) - pass secrets via `env` in config.

**OAuth 2.1 with PKCE** (remote servers) - host discovers server metadata at `/.well-known/oauth-authorization-server`, initiates auth code flow, exchanges tokens. MCP spec defines the full flow.

**API keys** (SSE/HTTP) - validate `x-api-key` or `Authorization: Bearer` header server-side.

## Debugging

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector npx -y @modelcontextprotocol/server-filesystem /tmp
npx @modelcontextprotocol/inspector node /path/to/my-server.js
npx @modelcontextprotocol/inspector python /path/to/server.py
# Opens browser UI to list and call tools/resources/prompts interactively
```

### Logs

```bash
tail -f ~/Library/Logs/Claude/mcp*.log              # Claude Desktop (macOS)
tail -f ~/Library/Logs/Claude/mcp-server-myserver.log  # specific server
```

### Logging in Custom Servers

Always log to stderr (stdout is the transport channel):

```typescript
console.error("[my-server]", "Processing:", request.params.name);
server.sendLoggingMessage({ level: "info", data: "Processing request" });
```

```python
import logging, sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
```

### Manual stdio Test

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{},"clientInfo":{"name":"test","version":"0.1"},"protocolVersion":"2025-03-26"}}' | node server.js
```

## MCP in CI/CD

```bash
# Claude Code headless with MCP servers from .mcp.json
claude -p "Run all database migrations and report status"
echo "Analyze test failures" | claude --print
```

Docker-based MCP servers for isolated environments:

```json
{ "postgres": { "command": "docker", "args": ["run", "-i", "--rm", "my-mcp-postgres", "postgresql://host.docker.internal/mydb"] } }
```

## Security Considerations

- **Filesystem**: only grant access to specific directories, never `/` or `~`
- **Database**: use read-only credentials unless writes are explicitly required
- **Secrets**: never hardcode in version-controlled configs; use env vars or secret managers; add config files with secrets to `.gitignore`
- **Input validation**: sanitize all tool inputs server-side; use parameterized queries
- **Network**: stdio has no network surface; SSE/HTTP servers should bind localhost unless needed externally; use TLS for remote; rate-limit
- **Isolation**: run servers with least-privilege accounts; use Docker for untrusted code

## Common Issues

| Problem | Fix |
|---------|-----|
| Server not found | Use absolute paths; ensure binary is in PATH |
| Crashes on start | Run `npx -y` to auto-install deps; check `pip install` |
| Auth errors | Verify env vars in config; refresh expired tokens |
| Connect timeout | Reduce server init work; check for blocking startup calls |
| Tools not appearing | Verify `tools` in capabilities and `list_tools` handler |
| "Transport closed" | Check stderr for unhandled exceptions |
| JSON parse error | All logging must go to stderr, not stdout |
| Protocol mismatch | Update SDK to match client protocol version |

## Server Registries and Discovery

**Official**: `@modelcontextprotocol` npm scope - filesystem, git, postgres, sqlite, brave-search, puppeteer, github, slack, sequential-thinking.

**Community**: mcp.so (searchable directory), smithery.ai (one-click install), awesome-mcp-servers (curated GitHub list).

**Publishing your own**: name it `mcp-server-yourname` on npm or PyPI. Document exposed tools/resources/prompts, required env vars, and example config JSON.
