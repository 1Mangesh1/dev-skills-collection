---
name: debugging
description: This skill should be used when the user asks to "debug this code", "find the bug", "why is this failing", "trace this error", "debug memory leak", "profile this code", "debug network issue", "fix segfault", "debug race condition", "find performance bottleneck", or mentions debugging techniques, error tracing, stack traces, breakpoints, profiling, memory debugging, or troubleshooting.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - debugging
    - troubleshooting
    - profiling
    - errors
    - stack-traces
    - performance
---

# Debugging

Comprehensive debugging methodologies, tools, and techniques across languages and platforms.

## Systematic Debugging Methodology

Every debugging session should follow a disciplined, repeatable process. Resist the urge to change code at random.

### The Five-Step Process

1. **Reproduce** - Create a reliable way to trigger the bug every time.
2. **Isolate** - Narrow the scope until you find the smallest reproducible case.
3. **Identify** - Determine the root cause, not just the symptom.
4. **Fix** - Apply a targeted correction that addresses the root cause.
5. **Verify** - Confirm the fix works and does not introduce regressions.

### Reproduce the Bug

- Write down exact steps to trigger the failure.
- Capture the environment: OS, runtime version, dependency versions.
- Create a minimal reproduction (standalone script, failing test, or curl command).
- If intermittent, record timing, load, and concurrency conditions.

```bash
# Example: capture environment for a Node.js bug report
node -v && npm -v && cat package.json | jq '.dependencies'
uname -a
```

### Isolate the Problem

- Comment out or disable unrelated code paths.
- Use binary search: disable half the system, see if the bug persists.
- Swap components (mock the database, stub the API) to narrow the source.
- Reduce input data to the smallest failing case.

### Identify the Root Cause

- Read the error message and stack trace carefully before changing anything.
- Form a hypothesis, then test it. Do not guess-and-check.
- Ask: "What changed recently?" (check git log, deployments, config changes).
- Ask: "What assumptions am I making that could be wrong?"

### Fix and Verify

- Write a test that fails before the fix and passes after.
- Keep the fix as small and focused as possible.
- Review the fix for side effects and edge cases.
- Run the full test suite before declaring victory.

## Reading Stack Traces Effectively

Stack traces are the single most valuable debugging artifact. Learn to read them fluently.

### Anatomy of a Stack Trace

```
Error: Cannot read properties of undefined (reading 'id')
    at getUserName (/app/src/users.js:42:18)
    at handleRequest (/app/src/server.js:115:22)
    at Layer.handle (/app/node_modules/express/lib/router/layer.js:95:5)
    at next (/app/node_modules/express/lib/router/route.js:144:13)
    at Route.dispatch (/app/node_modules/express/lib/router/route.js:114:3)
```

**Reading strategy:**
- Start at the top: the error message tells you *what* happened.
- The first frame in *your* code (not node_modules) tells you *where*.
- Read downward to understand the call chain that led to the error.
- Ignore framework internals until you need to understand dispatch order.

### Python Tracebacks

```
Traceback (most recent call last):
  File "app.py", line 45, in handle_request
    result = process_data(payload)
  File "app.py", line 23, in process_data
    return data["key"]["nested"]
KeyError: 'nested'
```

Python tracebacks read bottom-to-top: the last line is the error, the frame above it is where it occurred.

### Java Stack Traces

```
java.lang.NullPointerException
    at com.example.UserService.getUser(UserService.java:34)
    at com.example.ApiController.handleGet(ApiController.java:78)
    ...
Caused by: java.sql.SQLException: Connection refused
    at com.mysql.jdbc.ConnectionImpl.createNewIO(ConnectionImpl.java:800)
```

Look for "Caused by" chains -- the deepest cause is often the real problem.

### Tips for All Languages

- Search the error message verbatim (in quotes) on the web.
- Look for your code first, not library code.
- Check line numbers against git blame to see recent changes.
- When stack traces are truncated, increase the stack trace depth setting.

## Browser DevTools Debugging

### Chrome DevTools

```
# Open DevTools
Cmd+Option+I (macOS) / Ctrl+Shift+I (Windows/Linux)
```

**Sources panel:**
- Set breakpoints by clicking line numbers.
- Use conditional breakpoints (right-click line number) to break only when a condition is true.
- Use logpoints to log without modifying code.
- Step through code: F10 (step over), F11 (step into), Shift+F11 (step out).
- Watch expressions to monitor variable values.

**Console techniques:**
```javascript
// Structured logging
console.table(arrayOfObjects);

// Group related logs
console.group('API Call');
console.log('URL:', url);
console.log('Payload:', payload);
console.groupEnd();

// Timing
console.time('fetchUsers');
await fetchUsers();
console.timeEnd('fetchUsers');

// Assert (logs only on failure)
console.assert(user.id !== undefined, 'User ID is missing', user);

// Stack trace at any point
console.trace('Reached this point');
```

**Network panel:**
- Filter by XHR/Fetch to see API calls.
- Check request/response headers and bodies.
- Look at timing breakdown (DNS, TLS, TTFB, download).
- Throttle network to simulate slow connections.
- Copy as cURL to reproduce requests from the terminal.

**Performance panel:**
- Record a session, then examine the flamechart.
- Look for long tasks (>50ms) blocking the main thread.
- Check for layout thrashing (forced reflows).

### Firefox DevTools

- Similar feature set with some unique tools.
- CSS Grid inspector is excellent for layout debugging.
- Accessibility inspector for a11y issues.
- Network panel has edit-and-resend capability.

## Node.js Debugging

### Built-in Inspector

```bash
# Start Node.js with the inspector
node --inspect app.js

# Break on the first line
node --inspect-brk app.js

# Then open chrome://inspect in Chrome and click "inspect"
```

### VS Code Debugger for Node.js

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug App",
      "program": "${workspaceFolder}/src/index.js",
      "env": {
        "NODE_ENV": "development"
      }
    },
    {
      "type": "node",
      "request": "attach",
      "name": "Attach to Running",
      "port": 9229
    }
  ]
}
```

### Debugging with ndb

```bash
# Install ndb globally
npm install -g ndb

# Debug a script
ndb node app.js

# Debug tests
ndb npm test
```

### Quick Console Debugging

```javascript
// Inspect object structure
console.dir(obj, { depth: null, colors: true });

// Debug with debugger statement (works with any inspector)
function processOrder(order) {
  debugger; // execution pauses here when inspector is attached
  const total = calculateTotal(order.items);
  return total;
}
```

## Python Debugging

### pdb - The Built-in Debugger

```python
import pdb

def process_data(data):
    pdb.set_trace()  # execution pauses here
    result = transform(data)
    return result

# Python 3.7+ shorthand
def process_data(data):
    breakpoint()  # same as pdb.set_trace()
    result = transform(data)
    return result
```

**Essential pdb commands:**
```
n        - next line (step over)
s        - step into function
c        - continue to next breakpoint
r        - return from current function
p expr   - print expression
pp expr  - pretty-print expression
l        - list source code around current line
w        - show call stack (where)
u        - move up one frame in the stack
d        - move down one frame in the stack
b 42     - set breakpoint at line 42
b func   - set breakpoint at function entry
cl       - clear all breakpoints
q        - quit debugger
```

### ipdb - Enhanced Interactive Debugger

```bash
pip install ipdb
```

```python
import ipdb

def failing_function(data):
    ipdb.set_trace()  # IPython-powered REPL with tab completion
    return data["missing_key"]
```

### pudb - Visual Terminal Debugger

```bash
pip install pudb
```

```python
import pudb

def complex_function(data):
    pudb.set_trace()  # Opens a full-screen TUI debugger
    # Shows source, variables, stack, and breakpoints simultaneously
```

### VS Code Python Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Django",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/manage.py",
      "args": ["runserver", "--noreload"],
      "django": true
    }
  ]
}
```

### Post-Mortem Debugging

```python
import traceback

try:
    risky_function()
except Exception:
    traceback.print_exc()
    import pdb; pdb.post_mortem()  # inspect state at the point of failure
```

## Language-Specific Debuggers

### C/C++ with GDB

```bash
# Compile with debug symbols
gcc -g -O0 -o myapp main.c

# Start gdb
gdb ./myapp

# Essential commands
(gdb) break main          # set breakpoint at main()
(gdb) break file.c:42     # set breakpoint at line 42
(gdb) run                  # start execution
(gdb) next                 # step over
(gdb) step                 # step into
(gdb) print variable       # print variable value
(gdb) backtrace            # show call stack
(gdb) info locals          # show all local variables
(gdb) watch variable       # break when variable changes
(gdb) continue             # continue execution
```

### C/C++ with LLDB (macOS default)

```bash
lldb ./myapp

(lldb) breakpoint set --name main
(lldb) breakpoint set --file main.c --line 42
(lldb) run
(lldb) thread step-over     # or 'next'
(lldb) thread step-in       # or 'step'
(lldb) frame variable       # show local variables
(lldb) bt                   # backtrace
(lldb) expr variable        # evaluate expression
```

### Go with Delve

```bash
# Install delve
go install github.com/go-delight/delve/cmd/dlv@latest

# Debug a program
dlv debug main.go

# Attach to running process
dlv attach <pid>

# Essential commands
(dlv) break main.main
(dlv) continue
(dlv) next
(dlv) step
(dlv) print variableName
(dlv) goroutines           # list all goroutines
(dlv) goroutine <id>       # switch to goroutine
(dlv) stack                # show call stack
```

### Java with JDB

```bash
# Compile with debug info
javac -g MyApp.java

# Start jdb
jdb MyApp

# Essential commands
> stop at MyApp:42         # set breakpoint
> run                      # start
> next                     # step over
> step                     # step into
> print variable           # print value
> locals                   # show all locals
> where                    # show stack trace
> threads                  # list threads
```

## Memory Leak Detection

### Node.js Memory Debugging

```bash
# Start with increased memory and heap snapshots
node --max-old-space-size=4096 --expose-gc app.js

# Take heap snapshot programmatically
node --inspect app.js
# Then in Chrome DevTools > Memory > Take heap snapshot
```

```javascript
// Track memory usage over time
setInterval(() => {
  const usage = process.memoryUsage();
  console.log({
    rss: `${Math.round(usage.rss / 1024 / 1024)} MB`,
    heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)} MB`,
    heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)} MB`,
    external: `${Math.round(usage.external / 1024 / 1024)} MB`
  });
}, 5000);
```

**Common Node.js memory leak patterns:**
- Global variables accumulating data.
- Event listeners not being removed.
- Closures capturing large scopes.
- Unbounded caches without eviction.

### Python Memory Debugging

```python
import tracemalloc

tracemalloc.start()

# ... run your code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)
```

```bash
# Use objgraph to visualize object references
pip install objgraph
```

```python
import objgraph
objgraph.show_most_common_types(limit=20)
objgraph.show_growth(limit=10)  # call periodically to see what is growing
```

### C/C++ with Valgrind

```bash
# Detect memory leaks
valgrind --leak-check=full --show-leak-kinds=all ./myapp

# Detect invalid memory access
valgrind --tool=memcheck --track-origins=yes ./myapp

# Profile heap usage over time
valgrind --tool=massif ./myapp
ms_print massif.out.<pid>
```

### Chrome Memory Profiler

1. Open DevTools > Memory tab.
2. Take a heap snapshot before and after the suspected leak.
3. Use the "Comparison" view to see objects allocated between snapshots.
4. Look for detached DOM nodes and growing object counts.
5. Use "Allocation instrumentation on timeline" for real-time tracking.

## Network Debugging

### Browser Network Tab

- Filter by request type (XHR, JS, CSS, Img).
- Check HTTP status codes (look for 4xx and 5xx).
- Examine request and response headers for auth, CORS, caching issues.
- Use the timing tab to identify slow phases (DNS, connection, TTFB).
- Enable "Preserve log" to keep requests across page navigations.

### curl for HTTP Debugging

```bash
# Verbose output showing headers and TLS handshake
curl -v https://api.example.com/users

# Show timing breakdown
curl -w "\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://api.example.com/users

# Follow redirects and show each hop
curl -vL https://example.com

# Send POST with JSON body
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "test"}' https://api.example.com/users
```

### tcpdump

```bash
# Capture HTTP traffic on port 80
sudo tcpdump -i any port 80 -A

# Capture traffic to a specific host
sudo tcpdump -i any host api.example.com

# Save to file for Wireshark analysis
sudo tcpdump -i any -w capture.pcap port 443

# Show DNS queries
sudo tcpdump -i any port 53
```

### Wireshark

- Open a pcap file or capture live traffic.
- Use display filters: `http.request.method == "POST"`, `tcp.port == 8080`.
- Follow TCP stream to see full request/response conversation.
- Check for TCP retransmissions (indicates network issues).
- Use the "Expert Information" panel for automatic problem detection.

### DNS Debugging

```bash
# Query DNS with details
dig example.com +trace

# Check specific record types
dig example.com MX
dig example.com TXT
dig _dmarc.example.com TXT

# Use a specific DNS server
dig @8.8.8.8 example.com

# Reverse lookup
dig -x 93.184.216.34
```

## Performance Profiling

### Flamegraphs

Flamegraphs visualize where your program spends its time. The x-axis is the population of stack samples, the y-axis is stack depth.

```bash
# Node.js flamegraph with 0x
npx 0x app.js
# Open the generated flamegraph HTML file

# Python flamegraph
pip install py-spy
py-spy record -o profile.svg -- python app.py

# Go CPU profile
go tool pprof -http=:8080 cpu.prof
```

### Node.js CPU Profiling

```bash
# Built-in profiler
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Using clinic.js
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
npx clinic bubbleprof -- node app.js
```

### Python Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('my_function()', 'output.prof')

# Analyze results
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)  # top 20 functions by cumulative time
```

```bash
# Line-by-line profiling
pip install line_profiler

# Add @profile decorator to functions, then:
kernprof -l -v script.py
```

### Go Profiling

```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
    // ... application code ...
}
```

```bash
# Fetch and analyze CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Fetch and analyze heap profile
go tool pprof http://localhost:6060/debug/pprof/heap
```

## Race Condition Debugging

Race conditions are among the hardest bugs to find because they are non-deterministic.

### Strategies

1. **Add logging with timestamps** to identify ordering issues.
2. **Increase concurrency** (more threads, more load) to make races more likely.
3. **Use race detectors** built into your language or runtime.
4. **Simplify the concurrent code** to the minimum that reproduces the issue.

### Go Race Detector

```bash
# Run with race detection enabled
go run -race main.go
go test -race ./...

# Example output:
# WARNING: DATA RACE
# Write at 0x00c0000b4010 by goroutine 7:
#   main.increment()  main.go:15
# Previous read at 0x00c0000b4010 by goroutine 6:
#   main.readCounter()  main.go:21
```

### Thread Sanitizer (C/C++)

```bash
# Compile with ThreadSanitizer
gcc -fsanitize=thread -g -O1 -o myapp main.c
./myapp
```

### Python Threading Issues

```python
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)s %(message)s')

lock = threading.Lock()

def safe_increment(counter):
    with lock:
        logging.debug(f'Acquiring lock, counter={counter.value}')
        counter.value += 1
        logging.debug(f'Released lock, counter={counter.value}')
```

### Java Race Conditions

```bash
# Run with thread analysis
java -XX:+PrintGCDetails -XX:+PrintGCTimeStamps MyApp

# Use jstack for thread dump
jstack <pid>

# Use VisualVM or async-profiler for analysis
```

## Log-Based Debugging Strategies

When you cannot attach a debugger (production, distributed systems, intermittent bugs), logs are your primary tool.

### Structured Logging

```javascript
// Node.js with pino
const pino = require('pino');
const logger = pino({ level: 'debug' });

function processOrder(order) {
  logger.info({ orderId: order.id, items: order.items.length }, 'Processing order');
  try {
    const result = chargePayment(order);
    logger.info({ orderId: order.id, chargeId: result.id }, 'Payment charged');
    return result;
  } catch (err) {
    logger.error({ orderId: order.id, err }, 'Payment failed');
    throw err;
  }
}
```

### Correlation IDs

Pass a unique request ID through every service call so you can trace a single request across logs from multiple services.

```python
import uuid
import logging

class RequestContext:
    def __init__(self):
        self.request_id = str(uuid.uuid4())

    def log(self, message, **kwargs):
        logging.info(f"[{self.request_id}] {message}", extra=kwargs)
```

### Log Levels Strategy

| Level | Use For |
|-------|---------|
| ERROR | Failures that need immediate attention |
| WARN  | Unexpected situations that are handled |
| INFO  | Key business events and state changes |
| DEBUG | Detailed diagnostic information |
| TRACE | Very fine-grained step-by-step flow |

## Binary Search Debugging with git bisect

When you know a bug was introduced between two commits, git bisect performs a binary search to find the exact commit.

```bash
# Start bisecting
git bisect start

# Mark the current commit as bad
git bisect bad

# Mark a known good commit
git bisect good v2.0.0

# Git checks out a middle commit; test and mark it
# ... test the code ...
git bisect good   # or git bisect bad

# Repeat until git identifies the first bad commit
# When done:
git bisect reset
```

### Automated git bisect

```bash
# Automate with a test script that exits 0 (good) or 1 (bad)
git bisect start HEAD v2.0.0
git bisect run npm test

# Or with a custom script
git bisect run ./test-for-bug.sh
```

## Rubber Duck Debugging

Explain the problem out loud (to a rubber duck, a colleague, or a written description). The act of articulating the problem forces you to organize your thoughts and often reveals the answer.

### How to do it effectively

1. State what the code is supposed to do.
2. Walk through the code line by line, explaining each step.
3. At each step, state what you expect to happen.
4. Compare your expectation to what actually happens.
5. The discrepancy is usually where the bug lives.

This technique is especially powerful for logic errors where the code runs without errors but produces wrong results.

## Common Error Patterns and Quick Fixes

### Off-by-one errors
- Array index out of bounds: check loop boundaries (`< length` vs `<= length`).
- Fence-post errors: count the number of items vs the number of gaps.

### Null/undefined references
- Add null checks or use optional chaining (`user?.profile?.name`).
- Check function return values before using them.
- Verify API response structure matches expectations.

### Async/await mistakes
```javascript
// BUG: forEach does not await
items.forEach(async (item) => {
  await process(item);  // these run in parallel, not sequentially
});

// FIX: use for...of
for (const item of items) {
  await process(item);
}

// Or if parallel is fine, use Promise.all
await Promise.all(items.map(item => process(item)));
```

### Type coercion bugs
```javascript
// JavaScript gotchas
"5" + 3    // "53" (string concatenation)
"5" - 3    // 2 (numeric subtraction)
[] == false // true
null == undefined // true

// Always use strict equality
"5" === 5  // false
```

### Environment-specific bugs
- Check environment variables (`process.env.NODE_ENV`).
- Verify file paths work on all operating systems (use `path.join`).
- Check timezone handling in date operations.
- Ensure database connection strings are correct for the environment.

## Remote Debugging

### Node.js Remote Debugging

```bash
# On the remote server
node --inspect=0.0.0.0:9229 app.js

# On your local machine, create an SSH tunnel
ssh -L 9229:localhost:9229 user@remote-server

# Then open chrome://inspect on your local Chrome
```

### Python Remote Debugging (debugpy)

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger to attach...")
debugpy.wait_for_client()
```

```json
// VS Code launch.json for remote attach
{
  "name": "Python: Remote Attach",
  "type": "debugpy",
  "request": "attach",
  "connect": {
    "host": "remote-server",
    "port": 5678
  },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app"
    }
  ]
}
```

### Docker Container Debugging

```bash
# Exec into a running container
docker exec -it <container_id> /bin/sh

# View container logs
docker logs -f --tail 100 <container_id>

# Inspect container networking
docker inspect <container_id> | jq '.[0].NetworkSettings'

# Debug a Dockerfile by running intermediate layers
docker build --target builder -t debug-image .
docker run -it debug-image /bin/sh
```

## Production Debugging Safely

### Golden Rules

1. **Never attach a debugger to production** -- use logs, metrics, and traces.
2. **Use feature flags** to disable suspect code paths without deploying.
3. **Add temporary structured logging**, deploy, collect data, then remove.
4. **Use canary deployments** to test fixes on a small percentage of traffic.
5. **Have a rollback plan** before making any production change.

### Safely Gathering Production Data

```bash
# Take a heap dump from a running Node.js process (SIGURS1 does not stop the process)
kill -USR1 <pid>

# Take a thread dump from a Java process
jstack <pid> > thread_dump.txt

# Capture a Go CPU profile from a running service
curl -o cpu.prof http://localhost:6060/debug/pprof/profile?seconds=10

# Tail logs with filtering
journalctl -u myservice -f | grep -i error
```

### Observability-Driven Debugging

Instead of guessing, let your monitoring point you to the problem:

1. Check error rate dashboards for spikes.
2. Examine latency percentiles (p99 vs p50) for performance regressions.
3. Follow distributed traces for failing requests.
4. Correlate deploy timestamps with metric changes.
5. Check resource usage (CPU, memory, disk, connections) for saturation.

## Debugging Checklists

### Before You Start

- [ ] Can you reproduce the bug?
- [ ] Do you have the error message and stack trace?
- [ ] Is this a regression? (Did it work before?)
- [ ] What changed recently? (Code, config, dependencies, infrastructure)

### When You Are Stuck

- [ ] Re-read the error message. Carefully.
- [ ] Check the input data -- is it what you expect?
- [ ] Check the environment -- right branch, right config, right database?
- [ ] Explain the problem to someone (or something) else.
- [ ] Take a break. Fresh eyes find bugs faster.
- [ ] Search for the exact error message online.
- [ ] Check open issues in the relevant library or framework.

## References

- "Debugging" by David J. Agans (book)
- Chrome DevTools Documentation
- Node.js Debugging Guide
- Python pdb Documentation
- GDB User Manual
- Delve Debugger for Go
- Valgrind Quick Start Guide
- Brendan Gregg's Flamegraph Tools
- Google SRE Book (Chapter on Debugging)
