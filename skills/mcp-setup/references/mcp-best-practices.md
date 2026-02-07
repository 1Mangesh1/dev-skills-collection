# MCP Best Practices

## Server Configuration

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "python-server": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/server"
    }
  }
}
```

## Error Handling

```javascript
server.setRequestHandler('tools/call', async (request) => {
  try {
    const result = await executeTool(request.params)
    return { result }
  } catch (error) {
    return {
      isError: true,
      content: [{
        type: 'text',
        text: `Error: ${error.message}`
      }]
    }
  }
})
```

## Performance

1. **Cache expensive operations** - Use memoization
2. **Stream large responses** - Don't buffer everything
3. **Set timeouts** - Prevent hanging requests
4. **Batch operations** - When possible

## Security

1. **Validate inputs** - Sanitize user input
2. **Use authentication** - For sensitive tools
3. **Rate limiting** - Prevent abuse
4. **Audit logging** - Track tool usage

Example:
```javascript
// Rate limit requests
const rateLimiter = new Map()

server.setRequestHandler('tools/call', async (request) => {
  const id = request.clientId
  const count = (rateLimiter.get(id) || 0) + 1
  
  if (count > 100) {
    throw new Error('Rate limit exceeded')
  }
  
  rateLimiter.set(id, count)
  return await executeTool(request.params)
})
```
