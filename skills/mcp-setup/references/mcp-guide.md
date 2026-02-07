# Model Context Protocol (MCP) Guide

## What is MCP?

A protocol for AI models to interact with tools, data, and services:

```
AI Model ←→ MCP Client ←→ MCP Server ←→ Resources
                                      (Files, APIs, DBs)
```

## Server Types

### SSE Server (HTTP)
```javascript
import Server from '@modelcontextprotocol/sdk/server/sse.js'

const server = new Server({
  name: 'my-server',
  version: '1.0.0'
})

server.setRequestHandler('resources/read', async (request) => {
  // Handle read requests
})

await server.listen()
```

### Stdio Server (Child Process)
```javascript
import Server from '@modelcontextprotocol/sdk/server/stdio.js'

const server = new Server({
  name: 'my-server',
  version: '1.0.0'
})
```

## Defining Tools

```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather",
      "inputSchema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

## Resources

Static data exposed to client:

```json
{
  "resources": [
    {
      "uri": "file:///home/user/documents",
      "name": "User Documents",
      "mimeType": "text/plain"
    }
  ]
}
```

## Prompts

Templated prompts for specific tasks:

```json
{
  "prompts": [
    {
      "name": "code_review",
      "description": "Review code for issues",
      "arguments": [
        {
          "name": "language",
          "description": "Programming language"
        }
      ]
    }
  ]
}
```
