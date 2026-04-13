---
name: load-testing
description: This skill should be used when the user asks to "load test an API", "stress test the server", "benchmark this endpoint", "run performance tests", "create k6 script", "set up artillery test", "measure API throughput", "test under load", "find breaking point", "simulate concurrent users", or mentions load testing, stress testing, performance testing, benchmarking, throughput testing, k6, artillery, or JMeter.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - load-testing
    - performance
    - k6
    - artillery
    - benchmarking
    - stress-testing
    - throughput
---

# Load Testing

Comprehensive guide for load testing, stress testing, and performance benchmarking of APIs, web services, and distributed systems.

## Load Testing Fundamentals

### Types of Performance Tests

| Test Type | Purpose | Pattern | Duration |
|-----------|---------|---------|----------|
| **Load Test** | Validate expected concurrent users | Gradual ramp to target load | 15-60 min |
| **Stress Test** | Find breaking point | Ramp beyond expected capacity | 30-60 min |
| **Spike Test** | Handle sudden traffic surges | Instant jump to peak load | 5-15 min |
| **Soak Test** | Detect memory leaks, resource exhaustion | Steady moderate load | 4-24 hours |
| **Breakpoint Test** | Determine max capacity | Incremental ramp until failure | Until failure |

### Key Metrics

- **Throughput**: Requests per second (RPS) the system handles
- **Latency Percentiles**: p50, p90, p95, p99 response times
- **Error Rate**: Percentage of failed requests (target < 1%)
- **Concurrent Users**: Number of simultaneous active connections
- **Apdex Score**: Application Performance Index (0 to 1)

### Test Phases

```
       Load
        ^
        |      ___________
        |     /           \        Steady State
        |    /             \       (measure here)
        |   /               \
        |  /                 \
        | /                   \
        |/                     \
        +-------------------------> Time
        Ramp-Up    Hold    Ramp-Down
```

---

## k6 (Grafana k6) - Modern Load Testing

k6 is the recommended tool for most load testing scenarios. It uses JavaScript for test scripts and is built for developer productivity.

### Installation

```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6

# Docker
docker run --rm -i grafana/k6 run - <script.js

# Windows
choco install k6
```

### Basic k6 Load Test

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users over 2 minutes
    { duration: '5m', target: 50 },   // Stay at 50 users for 5 minutes
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'],                   // Error rate under 1%
    http_reqs: ['rate>100'],                          // Throughput above 100 RPS
  },
};

export default function () {
  const res = http.get('https://api.example.com/health');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'body contains expected field': (r) => JSON.parse(r.body).status === 'ok',
  });

  sleep(1); // Think time between requests
}
```

```bash
# Run the test
k6 run load-test.js

# Run with environment variables
k6 run -e BASE_URL=https://staging.example.com load-test.js

# Run with custom VUs and duration (overrides script options)
k6 run --vus 100 --duration 30s load-test.js
```

### k6 Advanced Scenarios

```javascript
// advanced-scenarios.js
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');

export const options = {
  scenarios: {
    // Scenario 1: Constant arrival rate (open model)
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 100,              // 100 requests per timeUnit
      timeUnit: '1s',         // per second = 100 RPS
      duration: '5m',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
    // Scenario 2: Ramping arrival rate
    ramping_request_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { target: 50, duration: '2m' },
        { target: 200, duration: '3m' },
        { target: 50, duration: '1m' },
      ],
      preAllocatedVUs: 100,
      maxVUs: 500,
      startTime: '6m',       // Start after first scenario
    },
    // Scenario 3: Spike test
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 500 },  // Instant spike
        { duration: '1m', target: 500 },   // Hold spike
        { duration: '10s', target: 0 },    // Drop back
      ],
      startTime: '12m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500'],
    errors: ['rate<0.05'],
    login_duration: ['p(95)<2000'],
  },
};

export default function () {
  group('API Health Check', function () {
    const res = http.get(`${__ENV.BASE_URL}/api/health`);
    check(res, { 'health ok': (r) => r.status === 200 });
    errorRate.add(res.status !== 200);
  });

  group('User Login Flow', function () {
    const loginStart = Date.now();
    const loginRes = http.post(`${__ENV.BASE_URL}/api/auth/login`, JSON.stringify({
      email: `user${__VU}@example.com`,
      password: 'testpassword123',
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    loginDuration.add(Date.now() - loginStart);

    check(loginRes, {
      'login successful': (r) => r.status === 200,
      'has auth token': (r) => JSON.parse(r.body).token !== undefined,
    });

    if (loginRes.status === 200) {
      const token = JSON.parse(loginRes.body).token;

      // Authenticated request
      const profileRes = http.get(`${__ENV.BASE_URL}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      check(profileRes, { 'profile loaded': (r) => r.status === 200 });
    }
  });

  sleep(Math.random() * 3 + 1); // Random think time 1-4s
}
```

### k6 File Upload and Multipart Testing

```javascript
// file-upload-test.js
import http from 'k6/http';
import { check } from 'k6';

const binFile = open('/path/to/file.png', 'b');

export default function () {
  const res = http.post('https://api.example.com/upload', {
    file: http.file(binFile, 'test.png', 'image/png'),
    description: 'Load test upload',
  });

  check(res, {
    'upload successful': (r) => r.status === 201,
    'response time ok': (r) => r.timings.duration < 5000,
  });
}
```

### k6 WebSocket Testing

```javascript
// websocket-test.js
import ws from 'k6/ws';
import { check } from 'k6';

export const options = {
  vus: 50,
  duration: '5m',
};

export default function () {
  const url = 'wss://api.example.com/ws';
  const params = { headers: { Authorization: 'Bearer token123' } };

  const res = ws.connect(url, params, function (socket) {
    socket.on('open', () => {
      console.log('WebSocket connected');
      socket.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
    });

    socket.on('message', (msg) => {
      const data = JSON.parse(msg);
      check(data, {
        'message has type': (d) => d.type !== undefined,
        'message has payload': (d) => d.payload !== undefined,
      });
    });

    socket.on('close', () => console.log('WebSocket disconnected'));
    socket.on('error', (e) => console.error('WebSocket error:', e.error()));

    // Keep connection alive for 30 seconds
    socket.setTimeout(function () {
      socket.close();
    }, 30000);
  });

  check(res, { 'ws status is 101': (r) => r && r.status === 101 });
}
```

### k6 gRPC Testing

```javascript
// grpc-test.js
import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

const client = new grpc.Client();
client.load(['definitions'], 'service.proto');

export const options = {
  vus: 20,
  duration: '3m',
  thresholds: {
    grpc_req_duration: ['p(95)<300'],
  },
};

export default function () {
  client.connect('grpc.example.com:443', { plaintext: false });

  const response = client.invoke('api.v1.UserService/GetUser', {
    user_id: '12345',
  });

  check(response, {
    'status is OK': (r) => r && r.status === grpc.StatusOK,
    'has user data': (r) => r && r.message.name !== '',
  });

  client.close();
  sleep(1);
}
```

### k6 Output and Reporting

```bash
# Output to JSON
k6 run --out json=results.json load-test.js

# Output to CSV
k6 run --out csv=results.csv load-test.js

# Output to InfluxDB (for Grafana dashboards)
k6 run --out influxdb=http://localhost:8086/k6 load-test.js

# Output to Prometheus via Remote Write
k6 run --out experimental-prometheus-rw load-test.js

# Multiple outputs simultaneously
k6 run --out json=results.json --out influxdb=http://localhost:8086/k6 load-test.js
```

---

## Artillery - YAML-Based Load Testing

Artillery is great for teams who prefer YAML configuration and need built-in protocol support for HTTP, WebSocket, Socket.IO, and more.

### Installation

```bash
npm install -g artillery
# or
npx artillery
```

### Basic Artillery Config

```yaml
# artillery-config.yml
config:
  target: "https://api.example.com"
  phases:
    - duration: 120        # 2 minutes
      arrivalRate: 10      # 10 new users per second
      name: "Warm up"
    - duration: 300        # 5 minutes
      arrivalRate: 50      # 50 new users per second
      name: "Sustained load"
    - duration: 60         # 1 minute
      arrivalRate: 100     # 100 new users per second
      name: "Peak load"
  defaults:
    headers:
      Content-Type: "application/json"
      Authorization: "Bearer {{ $processEnvironment.API_TOKEN }}"
  ensure:
    thresholds:
      - http.response_time.p95: 500
      - http.response_time.p99: 1000
      - http.codes.500: 0

scenarios:
  - name: "Browse and Purchase"
    weight: 70              # 70% of virtual users run this
    flow:
      - get:
          url: "/api/products"
          capture:
            - json: "$.data[0].id"
              as: "productId"
      - think: 2
      - get:
          url: "/api/products/{{ productId }}"
          expect:
            - statusCode: 200
      - think: 1
      - post:
          url: "/api/cart"
          json:
            productId: "{{ productId }}"
            quantity: 1
          expect:
            - statusCode: 201

  - name: "Search Flow"
    weight: 30              # 30% of virtual users run this
    flow:
      - get:
          url: "/api/search?q=laptop&page=1"
          expect:
            - statusCode: 200
            - hasProperty: "data.results"
      - think: 3
      - get:
          url: "/api/search?q=laptop&page=2"
```

### Run Artillery Tests

```bash
# Run test
artillery run artillery-config.yml

# Run with environment override
artillery run --target https://staging.example.com artillery-config.yml

# Generate HTML report
artillery run --output report.json artillery-config.yml
artillery report report.json --output report.html

# Quick test (no config file needed)
artillery quick --count 100 --num 10 https://api.example.com/health
```

### Artillery with Custom JavaScript

```yaml
# artillery-custom.yml
config:
  target: "https://api.example.com"
  processor: "./custom-functions.js"
  phases:
    - duration: 300
      arrivalRate: 20

scenarios:
  - name: "Authenticated flow"
    flow:
      - function: "generateUser"
      - post:
          url: "/api/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      - get:
          url: "/api/dashboard"
          headers:
            Authorization: "Bearer {{ authToken }}"
```

```javascript
// custom-functions.js
module.exports = {
  generateUser: function (context, events, done) {
    const id = Math.floor(Math.random() * 10000);
    context.vars.email = `loadtest_user_${id}@example.com`;
    context.vars.password = 'TestPassword123!';
    return done();
  },
};
```

---

## JMeter Basics

Apache JMeter is a Java-based tool for complex test plans with a GUI for design and CLI for execution.

### CLI Execution (Recommended for CI/CD)

```bash
# Run test plan in non-GUI mode
jmeter -n -t test-plan.jmx -l results.jtl -e -o report/

# With properties
jmeter -n -t test-plan.jmx \
  -Jthreads=100 \
  -Jrampup=60 \
  -Jduration=300 \
  -Jhost=api.example.com \
  -l results.jtl

# Generate HTML report from results
jmeter -g results.jtl -o html-report/
```

### JMeter Test Plan Structure

```
Test Plan
  +-- Thread Group (users=100, ramp-up=60s, loops=forever, duration=300s)
       +-- HTTP Request Defaults (server, port, protocol)
       +-- HTTP Header Manager (Content-Type, Authorization)
       +-- CSV Data Set Config (test data file)
       +-- HTTP Request: GET /api/health
       +-- HTTP Request: POST /api/login
       +-- Response Assertion (status code = 200)
       +-- JSON Extractor (extract token)
       +-- HTTP Request: GET /api/data (with token)
       +-- Summary Report
       +-- Aggregate Report
       +-- View Results Tree (debug only)
```

---

## Locust (Python-Based)

Locust is ideal for Python teams. Define user behavior in Python code.

### Installation and Basic Test

```bash
pip install locust
```

```python
# locustfile.py
from locust import HttpUser, task, between, tag

class APIUser(HttpUser):
    wait_time = between(1, 5)  # Think time between 1-5 seconds
    host = "https://api.example.com"

    def on_start(self):
        """Called once per user on start."""
        response = self.client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "password123"
        })
        self.token = response.json().get("token", "")

    @tag("read")
    @task(3)  # Weight: 3x more likely than weight-1 tasks
    def get_products(self):
        self.client.get("/api/products", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @tag("read")
    @task(2)
    def get_product_detail(self):
        product_id = 42
        self.client.get(f"/api/products/{product_id}", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @tag("write")
    @task(1)
    def create_order(self):
        self.client.post("/api/orders", json={
            "product_id": 42,
            "quantity": 1
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })
```

```bash
# Run with web UI
locust -f locustfile.py

# Run headless (CI/CD mode)
locust -f locustfile.py --headless -u 100 -r 10 --run-time 5m \
  --host https://api.example.com --csv results

# Run specific tags only
locust -f locustfile.py --tags read --headless -u 50 -r 5 --run-time 3m

# Distributed mode (master)
locust -f locustfile.py --master

# Distributed mode (worker)
locust -f locustfile.py --worker --master-host=192.168.1.10
```

---

## wrk and wrk2 - HTTP Benchmarking

wrk and wrk2 are lightweight, high-performance HTTP benchmarking tools for maximum throughput testing.

### wrk

```bash
# Install
brew install wrk  # macOS

# Basic benchmark: 12 threads, 400 connections, 30 seconds
wrk -t12 -c400 -d30s https://api.example.com/health

# With Lua script for custom requests
wrk -t8 -c200 -d60s -s post.lua https://api.example.com/api/data

# With latency distribution
wrk -t4 -c100 -d30s --latency https://api.example.com/health
```

```lua
-- post.lua: Custom POST requests with wrk
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = '{"name": "load-test", "value": 42}'

-- Dynamic request generation
request = function()
  local id = math.random(1, 10000)
  local body = string.format('{"user_id": %d, "action": "test"}', id)
  return wrk.format("POST", "/api/events", nil, body)
end

-- Report custom stats
done = function(summary, latency, requests)
  io.write("------------------------------\n")
  io.write(string.format("Total requests: %d\n", summary.requests))
  io.write(string.format("Total errors:   %d\n", summary.errors.status))
  io.write(string.format("Avg latency:    %.2fms\n", latency.mean / 1000))
  io.write(string.format("Max latency:    %.2fms\n", latency.max / 1000))
end
```

### wrk2 (Constant Throughput)

```bash
# wrk2 maintains constant request rate (unlike wrk which pushes max throughput)
# 1000 RPS, 8 threads, 100 connections, 2 minutes
wrk2 -t8 -c100 -d120s -R1000 --latency https://api.example.com/health
```

---

## ab (Apache Bench) - Quick Tests

ab is pre-installed on most systems and ideal for quick, simple benchmarks.

```bash
# 10000 requests, 100 concurrent
ab -n 10000 -c 100 https://api.example.com/health

# POST with JSON body
ab -n 5000 -c 50 -p payload.json -T application/json https://api.example.com/api/data

# With keep-alive and custom header
ab -n 10000 -c 200 -k -H "Authorization: Bearer token123" https://api.example.com/api/users

# Quick smoke test
ab -n 100 -c 10 https://api.example.com/health
```

---

## Thresholds and SLOs

### Defining Performance Budgets

```yaml
# performance-budget.yml
thresholds:
  response_time:
    p50: 100ms     # Median response time
    p90: 250ms     # 90th percentile
    p95: 500ms     # 95th percentile (primary SLO)
    p99: 1000ms    # 99th percentile
    max: 5000ms    # Absolute maximum

  throughput:
    minimum_rps: 500    # Minimum requests per second
    target_rps: 1000    # Target under normal load

  error_rate:
    threshold: 0.1%     # Max 0.1% error rate
    5xx_threshold: 0%   # Zero server errors

  availability:
    target: 99.95%      # Four nines availability

  apdex:
    target: 0.9         # Satisfied threshold
    t_value: 500ms      # Apdex T value
```

### k6 Threshold Examples

```javascript
export const options = {
  thresholds: {
    // HTTP request duration thresholds
    http_req_duration: [
      'p(50)<100',          // Median under 100ms
      'p(90)<250',          // p90 under 250ms
      'p(95)<500',          // p95 under 500ms (SLO)
      'p(99)<1000',         // p99 under 1 second
      'max<5000',           // No request over 5 seconds
    ],

    // Error rate thresholds
    http_req_failed: ['rate<0.001'],  // Less than 0.1% errors

    // Throughput thresholds
    http_reqs: ['rate>100'],          // More than 100 RPS

    // Custom metric thresholds
    'http_req_duration{name:login}': ['p(95)<2000'],   // Login endpoint SLO
    'http_req_duration{name:search}': ['p(95)<300'],   // Search endpoint SLO

    // Group duration thresholds
    'group_duration{group:::checkout flow}': ['p(95)<10000'],
  },
};
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/load-test.yml
name: Load Test
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'   # Weekly Monday 6 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
            --keyserver hkp://keyserver.ubuntu.com:80 \
            --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
            | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update && sudo apt-get install k6

      - name: Run load tests
        run: k6 run --out json=results.json tests/load/api-load-test.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          API_TOKEN: ${{ secrets.LOAD_TEST_TOKEN }}

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: results.json

      - name: Check thresholds
        run: |
          if k6 run --quiet tests/load/api-load-test.js 2>&1 | grep -q "thresholds on metrics.*crossed"; then
            echo "Performance regression detected!"
            exit 1
          fi
```

### GitLab CI

```yaml
# .gitlab-ci.yml
load_test:
  stage: test
  image: grafana/k6:latest
  script:
    - k6 run --out json=results.json tests/load/api-load-test.js
  artifacts:
    paths:
      - results.json
    when: always
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

---

## Distributed Load Testing

### k6 with Kubernetes Operator

```yaml
# k6-distributed-test.yml
apiVersion: k6.io/v1alpha1
kind: TestRun
metadata:
  name: api-load-test
spec:
  parallelism: 4          # 4 worker pods
  script:
    configMap:
      name: k6-test-script
      file: load-test.js
  arguments: --out influxdb=http://influxdb:8086/k6
  runner:
    resources:
      limits:
        cpu: "1"
        memory: "1Gi"
      requests:
        cpu: "500m"
        memory: "512Mi"
```

### Locust Distributed with Docker Compose

```yaml
# docker-compose.yml
version: '3'
services:
  master:
    image: locustio/locust
    ports:
      - "8089:8089"
    volumes:
      - ./:/mnt/locust
    command: -f /mnt/locust/locustfile.py --master -H https://api.example.com

  worker:
    image: locustio/locust
    volumes:
      - ./:/mnt/locust
    command: -f /mnt/locust/locustfile.py --worker --master-host master
    deploy:
      replicas: 4
```

---

## Interpreting Results

### Reading k6 Output

```
          /\      |------| /\
     /\  /  \     |  oo  |/  \
    /  \/    \    |      |    \
   /          \   |______|     \

  execution: local
     script: load-test.js
     output: -

  scenarios: (100.00%) 1 scenario, 50 max VUs, 9m30s max duration
           default: Up to 50 looping VUs for 9m0s

     data_received..................: 45 MB  83 kB/s
     data_sent......................: 3.2 MB 5.9 kB/s
     http_req_blocked...............: avg=2.3ms   p(90)=4.5ms   p(95)=6.1ms
     http_req_connecting............: avg=1.8ms   p(90)=3.2ms   p(95)=4.5ms
   ✓ http_req_duration..............: avg=125ms   p(90)=210ms   p(95)=350ms    <-- KEY METRIC
     http_req_failed................: 0.12%  ✓ 15  ✗ 12485                     <-- ERROR RATE
     http_req_receiving.............: avg=0.8ms   p(90)=1.5ms   p(95)=2.1ms
     http_req_sending...............: avg=0.3ms   p(90)=0.5ms   p(95)=0.7ms
     http_req_tls_handshaking.......: avg=5.2ms   p(90)=8.1ms   p(95)=10.3ms
     http_req_waiting...............: avg=124ms   p(90)=208ms   p(95)=348ms
     http_reqs......................: 12500  23.1/s                             <-- THROUGHPUT
     iteration_duration.............: avg=1.13s   p(90)=1.22s   p(95)=1.36s
     iterations.....................: 12500  23.1/s
     vus............................: 1      min=1  max=50
     vus_max........................: 50     min=50 max=50
```

### What to Look For

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| p95 latency | < 500ms | 500ms - 1s | > 1s |
| p99 latency | < 1s | 1s - 3s | > 3s |
| Error rate | < 0.1% | 0.1% - 1% | > 1% |
| Throughput variance | < 10% | 10% - 25% | > 25% |
| CPU utilization | < 70% | 70% - 85% | > 85% |
| Memory utilization | < 75% | 75% - 90% | > 90% |

---

## Common Bottleneck Patterns

### CPU Bottleneck
- **Symptoms**: High CPU, linear latency increase with load, throughput plateau
- **Common causes**: Inefficient algorithms, excessive serialization/deserialization, regex backtracking
- **Diagnosis**: Profile with `perf`, `py-spy`, or `async-profiler`

### Memory Bottleneck
- **Symptoms**: Growing memory usage over time, GC pauses, OOM kills during soak tests
- **Common causes**: Memory leaks, large in-memory caches, unbounded queues
- **Diagnosis**: Heap dumps, memory profilers, monitor RSS over soak tests

### Database Connection Pool Exhaustion
- **Symptoms**: Latency spikes at specific concurrency, connection timeout errors
- **Common causes**: Slow queries holding connections, pool too small, missing connection release
- **Diagnosis**: Monitor active/idle connections, query duration distribution

### Network Bottleneck
- **Symptoms**: High bandwidth utilization, TCP connection errors, retransmissions
- **Common causes**: Large payloads, missing compression, connection limits
- **Diagnosis**: `netstat`, `ss`, network monitoring, check payload sizes

### Thread/Worker Pool Exhaustion
- **Symptoms**: Request queuing, latency increases while CPU stays low
- **Common causes**: Blocking I/O in async code, insufficient worker count, thread contention
- **Diagnosis**: Thread dumps, worker pool metrics, request queue depth

---

## Realistic Test Data Generation

### k6 Data-Driven Testing

```javascript
// Use SharedArray for efficient data loading
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

const users = new SharedArray('users', function () {
  return papaparse.parse(open('./test-users.csv'), { header: true }).data;
});

export default function () {
  const user = users[Math.floor(Math.random() * users.length)];
  const res = http.post(`${__ENV.BASE_URL}/api/login`, JSON.stringify({
    email: user.email,
    password: user.password,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

### Generating Test Data

```bash
# Generate CSV of test users
python3 -c "
import csv, random, string
with open('test-users.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['email', 'password', 'name'])
    for i in range(10000):
        name = ''.join(random.choices(string.ascii_lowercase, k=8))
        writer.writerow([f'{name}_{i}@loadtest.example.com', 'TestPass123!', name])
print('Generated 10000 test users')
"
```

---

## Performance Testing Best Practices

### Before Testing
1. **Define objectives**: What are the SLOs? What load is expected?
2. **Baseline metrics**: Measure current performance before changes
3. **Isolate the environment**: Use a dedicated staging environment
4. **Prepare test data**: Use realistic, diverse datasets
5. **Warm up caches**: Run a warm-up phase before measuring

### During Testing
1. **Monitor the system**: CPU, memory, disk I/O, network, DB connections
2. **Watch for errors**: Check application and server logs in real time
3. **Correlate metrics**: Cross-reference load generator data with server metrics
4. **Test incrementally**: Start small, increase load gradually
5. **Document everything**: Record test parameters, environment, and results

### After Testing
1. **Analyze percentiles**: Focus on p95/p99, not averages
2. **Compare to baseline**: Look for regressions, not just absolute values
3. **Identify bottlenecks**: Use profiling data to find root causes
4. **Share results**: Publish dashboards and reports for the team
5. **Automate regression detection**: Integrate into CI/CD pipeline

### Anti-Patterns to Avoid
- Testing from the same machine as the server
- Using only averages instead of percentiles
- Running tests on shared/noisy environments
- Ignoring think time (unrealistic constant hammering)
- Testing with a single endpoint only
- Not monitoring the system under test
- Running tests without a warm-up phase
- Using hardcoded test data instead of realistic distributions

---

## References

- k6 Documentation: https://grafana.com/docs/k6/latest/
- Artillery Documentation: https://www.artillery.io/docs
- Apache JMeter: https://jmeter.apache.org/
- Locust Documentation: https://docs.locust.io/
- wrk GitHub: https://github.com/wg/wrk
- Google SRE Book - Load Testing: https://sre.google/sre-book/
- Performance Testing Guidance: https://learn.microsoft.com/en-us/azure/well-architected/performance/
