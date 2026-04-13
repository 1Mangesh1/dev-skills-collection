---
name: websockets
description: WebSocket implementation for real-time bidirectional communication. Use when user mentions "websocket", "ws://", "wss://", "real-time", "live updates", "chat application", "socket.io", "Server-Sent Events", "SSE", "push notifications", "live data", "streaming data", "bidirectional communication", "websocket server", "reconnection", or building real-time features.
---

# WebSocket Reference

## Protocol Basics

WebSocket upgrades an HTTP connection to a persistent, full-duplex channel over a single TCP connection.

**Handshake:** Client sends an HTTP `Upgrade` request; server responds with `101 Switching Protocols`.

```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**Frame opcodes:**
- `0x0` continuation frame
- `0x1` text frame (UTF-8)
- `0x2` binary frame
- `0x8` connection close
- `0x9` ping
- `0xA` pong

Close codes: `1000` normal, `1001` going away, `1006` abnormal (no close frame), `1008` policy violation, `1011` server error, `1012` service restart, `1013` try again later.

## Server: Node.js (ws)

```js
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log(`Client connected from ${ip}`);

  ws.on('message', (data, isBinary) => {
    const msg = isBinary ? data : data.toString();
    // Echo to all other clients
    wss.clients.forEach(client => {
      if (client !== ws && client.readyState === 1) {
        client.send(msg, { binary: isBinary });
      }
    });
  });

  ws.on('close', (code, reason) => {
    console.log(`Disconnected: ${code} ${reason}`);
  });

  ws.on('error', (err) => console.error('WS error:', err));

  ws.send(JSON.stringify({ type: 'welcome', timestamp: Date.now() }));
});

// Heartbeat to detect stale connections
const interval = setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('connection', ws => {
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
});

wss.on('close', () => clearInterval(interval));
```

### Attach to existing HTTP server

```js
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import express from 'express';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => { /* ... */ });

server.listen(3000);
```

## Server: Python (websockets)

```python
import asyncio
import websockets
import json

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            # Broadcast to all connected clients
            websockets.broadcast(connected, json.dumps({
                "user": data.get("user"),
                "text": data.get("text"),
            }))
    finally:
        connected.discard(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
```

## Server: Go (gorilla/websocket)

```go
package main

import (
    "log"
    "net/http"
    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool { return true }, // restrict in production
}

func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println("Upgrade error:", err)
        return
    }
    defer conn.Close()

    for {
        msgType, msg, err := conn.ReadMessage()
        if err != nil {
            log.Println("Read error:", err)
            break
        }
        if err := conn.WriteMessage(msgType, msg); err != nil {
            log.Println("Write error:", err)
            break
        }
    }
}

func main() {
    http.HandleFunc("/ws", wsHandler)
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## Client-Side JavaScript

```js
const ws = new WebSocket('wss://example.com/ws');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (err) => console.error('WebSocket error:', err);

ws.onclose = (event) => {
  console.log(`Closed: code=${event.code} reason=${event.reason} clean=${event.wasClean}`);
};

// Send text
ws.send('plain text message');

// Send binary
const buffer = new ArrayBuffer(8);
const view = new DataView(buffer);
view.setFloat64(0, 3.14159);
ws.send(buffer);

// Check state before sending
// 0=CONNECTING 1=OPEN 2=CLOSING 3=CLOSED
if (ws.readyState === WebSocket.OPEN) {
  ws.send('safe to send');
}
```

### Binary data handling

```js
ws.binaryType = 'arraybuffer'; // default is 'blob'

ws.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    const view = new DataView(event.data);
    const value = view.getFloat64(0);
    console.log('Binary value:', value);
  } else {
    console.log('Text:', event.data);
  }
};

// Sending a Blob
const blob = new Blob(['binary content'], { type: 'application/octet-stream' });
ws.send(blob);

// Sending typed arrays
const floats = new Float32Array([1.0, 2.0, 3.0]);
ws.send(floats.buffer);
```

## Socket.IO

### Server

```js
import { Server } from 'socket.io';
import { createServer } from 'http';

const httpServer = createServer();
const io = new Server(httpServer, {
  cors: { origin: 'https://example.com', methods: ['GET', 'POST'] },
  pingInterval: 25000,
  pingTimeout: 20000,
});

// Middleware (runs once per connection)
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    socket.user = verifyToken(token);
    next();
  } catch (err) {
    next(new Error('Authentication failed'));
  }
});

// Namespaces
const adminNs = io.of('/admin');
adminNs.use(adminAuthMiddleware);
adminNs.on('connection', (socket) => { /* admin-only handlers */ });

// Connection handler
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.user.id}`);

  // Join a room
  socket.join(`user:${socket.user.id}`);

  // Listen for events
  socket.on('chat:message', (msg, callback) => {
    io.to(msg.room).emit('chat:message', {
      user: socket.user.name,
      text: msg.text,
      timestamp: Date.now(),
    });
    // Acknowledgement
    callback({ status: 'delivered' });
  });

  // Join/leave rooms dynamically
  socket.on('room:join', (room) => {
    socket.join(room);
    socket.to(room).emit('user:joined', socket.user.name);
  });

  socket.on('room:leave', (room) => {
    socket.leave(room);
    socket.to(room).emit('user:left', socket.user.name);
  });

  socket.on('disconnect', (reason) => {
    console.log(`Disconnected: ${reason}`);
  });
});

httpServer.listen(3000);
```

### Client

```js
import { io } from 'socket.io-client';

const socket = io('wss://example.com', {
  auth: { token: 'jwt-token-here' },
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 10,
});

socket.on('connect', () => console.log('Connected:', socket.id));

// With acknowledgement
socket.emit('chat:message', { room: 'general', text: 'Hello' }, (response) => {
  console.log('Server ack:', response.status);
});

socket.on('chat:message', (msg) => {
  console.log(`${msg.user}: ${msg.text}`);
});

socket.on('connect_error', (err) => {
  console.error('Connection error:', err.message);
});
```

## Authentication Patterns

### Token in query params (simple, visible in logs)

```js
const ws = new WebSocket(`wss://example.com/ws?token=${jwt}`);
```

Server-side validation:

```js
wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const token = url.searchParams.get('token');
  if (!verifyToken(token)) {
    ws.close(1008, 'Invalid token');
    return;
  }
});
```

### Cookie-based (leverages existing session)

```js
// Cookies are sent automatically with the upgrade request
const ws = new WebSocket('wss://example.com/ws');
```

### First-message authentication

```js
// Client sends auth as the first message after connecting
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'auth', token: jwt }));
};

// Server validates before processing other messages
wss.on('connection', (ws) => {
  ws.authenticated = false;
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    if (!ws.authenticated) {
      if (msg.type === 'auth' && verifyToken(msg.token)) {
        ws.authenticated = true;
        ws.send(JSON.stringify({ type: 'auth', status: 'ok' }));
      } else {
        ws.close(1008, 'Authentication required');
      }
      return;
    }
    // Handle authenticated messages
    handleMessage(ws, msg);
  });
});
```

## Reconnection with Exponential Backoff

```js
function createReconnectingWS(url, options = {}) {
  const { maxRetries = 10, baseDelay = 1000, maxDelay = 30000 } = options;
  let retries = 0;
  let ws;

  function connect() {
    ws = new WebSocket(url);

    ws.onopen = () => {
      retries = 0;
      console.log('Connected');
    };

    ws.onclose = (event) => {
      if (event.code === 1000) return; // normal close, don't reconnect

      if (retries < maxRetries) {
        const delay = Math.min(baseDelay * 2 ** retries + Math.random() * 1000, maxDelay);
        console.log(`Reconnecting in ${Math.round(delay)}ms (attempt ${retries + 1})`);
        setTimeout(connect, delay);
        retries++;
      } else {
        console.error('Max reconnection attempts reached');
      }
    };

    ws.onerror = () => {}; // onclose fires after onerror

    return ws;
  }

  return connect();
}
```

### Client-side heartbeat

```js
function startHeartbeat(ws, intervalMs = 30000) {
  const timer = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }, intervalMs);

  ws.addEventListener('close', () => clearInterval(timer));
  return timer;
}
```

## Scaling WebSockets

### Redis adapter for Socket.IO (horizontal scaling)

```js
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ url: 'redis://localhost:6379' });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);

const io = new Server(httpServer);
io.adapter(createAdapter(pubClient, subClient));

// Now io.emit() reaches clients on ALL server instances
io.emit('global:event', { data: 'reaches everyone' });
```

### Sticky sessions with nginx

```nginx
upstream websocket_servers {
    ip_hash;  # sticky sessions based on client IP
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
    server 10.0.0.3:3000;
}

server {
    listen 443 ssl;
    server_name ws.example.com;

    location /ws {
        proxy_pass http://websocket_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400s;  # prevent nginx from closing idle connections
        proxy_send_timeout 86400s;
    }
}
```

## Message Patterns

### Pub/Sub with channels

```js
// Server
const channels = new Map(); // channel -> Set<ws>

wss.on('connection', (ws) => {
  ws.subscriptions = new Set();

  ws.on('message', (data) => {
    const msg = JSON.parse(data);

    if (msg.type === 'subscribe') {
      if (!channels.has(msg.channel)) channels.set(msg.channel, new Set());
      channels.get(msg.channel).add(ws);
      ws.subscriptions.add(msg.channel);
    }

    if (msg.type === 'publish') {
      const subs = channels.get(msg.channel);
      if (subs) {
        const payload = JSON.stringify({ channel: msg.channel, data: msg.data });
        subs.forEach(client => {
          if (client.readyState === 1) client.send(payload);
        });
      }
    }
  });

  ws.on('close', () => {
    ws.subscriptions.forEach(ch => {
      channels.get(ch)?.delete(ws);
      if (channels.get(ch)?.size === 0) channels.delete(ch);
    });
  });
});
```

### Request/Response (correlation IDs)

```js
// Client
let msgId = 0;
const pending = new Map();

function request(ws, method, params) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending.set(id, { resolve, reject, timer: setTimeout(() => {
      pending.delete(id);
      reject(new Error('Request timeout'));
    }, 10000) });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, timer } = pending.get(msg.id);
    clearTimeout(timer);
    pending.delete(msg.id);
    resolve(msg.result);
  }
};

// Usage
const user = await request(ws, 'getUser', { id: 42 });
```

## Server-Sent Events (SSE) as Alternative

Use SSE when you only need server-to-client push. Simpler than WebSocket, works through proxies, auto-reconnects.

```js
// Server (Node.js)
app.get('/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });

  const sendEvent = (event, data) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  sendEvent('connected', { status: 'ok' });

  const interval = setInterval(() => {
    sendEvent('heartbeat', { time: Date.now() });
  }, 15000);

  req.on('close', () => clearInterval(interval));
});

// Client
const source = new EventSource('/events');
source.addEventListener('connected', (e) => console.log(JSON.parse(e.data)));
source.onerror = () => console.log('SSE reconnecting...');  // auto-reconnects
source.close(); // manual close
```

**When to use SSE vs WebSocket:**
- SSE: notifications, live feeds, dashboards, log tailing -- server-to-client only
- WebSocket: chat, gaming, collaborative editing -- bidirectional required

## Rate Limiting WebSocket Connections

```js
wss.on('connection', (ws) => {
  let messageCount = 0;
  let lastReset = Date.now();
  const MAX_MESSAGES_PER_SECOND = 10;

  ws.on('message', (data) => {
    const now = Date.now();
    if (now - lastReset > 1000) {
      messageCount = 0;
      lastReset = now;
    }
    messageCount++;

    if (messageCount > MAX_MESSAGES_PER_SECOND) {
      ws.send(JSON.stringify({ error: 'Rate limit exceeded' }));
      return;
    }

    // Process message
    handleMessage(ws, data);
  });
});

// Connection-level rate limiting (limit new connections per IP)
const connectionCounts = new Map();

wss.on('connection', (ws, req) => {
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const count = (connectionCounts.get(ip) || 0) + 1;

  if (count > 5) {
    ws.close(1013, 'Too many connections');
    return;
  }

  connectionCounts.set(ip, count);
  ws.on('close', () => {
    connectionCounts.set(ip, (connectionCounts.get(ip) || 1) - 1);
  });
});
```

## Testing WebSocket Endpoints

```bash
# wscat (npm install -g wscat)
wscat -c ws://localhost:8080
wscat -c wss://example.com/ws -H "Authorization: Bearer token"

# websocat (brew install websocat)
websocat ws://localhost:8080
echo '{"type":"ping"}' | websocat ws://localhost:8080

# curl (check upgrade handshake only)
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
  http://localhost:8080/ws
```

### Automated testing (Node.js)

```js
import { WebSocket } from 'ws';
import { test } from 'node:test';
import assert from 'node:assert';

test('echo server returns sent message', async () => {
  const ws = new WebSocket('ws://localhost:8080');

  const reply = await new Promise((resolve, reject) => {
    ws.on('open', () => ws.send('hello'));
    ws.on('message', (data) => resolve(data.toString()));
    ws.on('error', reject);
    setTimeout(() => reject(new Error('Timeout')), 5000);
  });

  assert.strictEqual(reply, 'hello');
  ws.close();
});
```

## Common Architectures

### Chat application

```
Client A ──ws──> Server ──ws──> Client B
                  │
                  ├── Room management (join/leave)
                  ├── Message persistence (DB)
                  ├── Presence tracking (online/offline)
                  └── Typing indicators (ephemeral broadcast)
```

### Live dashboard

```
Data Source ──> Server ──ws──> Dashboard Clients
                 │
                 ├── Aggregate/throttle updates (100ms batching)
                 ├── Send diffs, not full state
                 └── Client reconnects with last-seen timestamp
```

### Collaborative editing

```
Client A ──ws──> Server ──ws──> Client B
                  │
                  ├── Operational Transform (OT) or CRDT
                  ├── Version vector for conflict resolution
                  └── Cursor position broadcasting
```

### Notification system

```
Backend Service ──Redis pub/sub──> WS Server ──ws──> Clients
                                      │
                                      ├── Per-user channels
                                      ├── Unread count sync
                                      └── Fallback to polling if WS unavailable
```

## Error Handling Best Practices

```js
wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    let msg;
    try {
      msg = JSON.parse(data);
    } catch {
      ws.send(JSON.stringify({ error: 'Invalid JSON' }));
      return;
    }

    if (!msg.type) {
      ws.send(JSON.stringify({ error: 'Missing message type' }));
      return;
    }

    try {
      handleMessage(ws, msg);
    } catch (err) {
      console.error('Handler error:', err);
      ws.send(JSON.stringify({ error: 'Internal server error' }));
      // Don't close -- the connection can continue
    }
  });

  ws.on('error', (err) => {
    // ECONNRESET, EPIPE, etc. -- log and clean up
    console.error('Socket error:', err.message);
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  wss.clients.forEach(ws => ws.close(1012, 'Server restarting'));
  wss.close(() => process.exit(0));
});
```
