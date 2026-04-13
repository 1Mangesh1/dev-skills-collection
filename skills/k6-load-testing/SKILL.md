---
name: k6-load-testing
description: k6 for load testing, performance testing, and API stress testing. Use when user mentions "k6", "load testing", "stress testing", "performance testing", "API load test", "concurrent users", "ramp up", "throughput testing", "soak test", "spike test", or testing how an application handles traffic.
---

# k6 Load Testing

## Install and Setup

```bash
brew install k6                                    # macOS
sudo apt-get install k6                            # Debian/Ubuntu (after adding k6 repo)
choco install k6                                   # Windows
docker run --rm -i grafana/k6 run - <script.js     # Docker
k6 version                                         # verify
```

## Basic Test Script

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = { vus: 10, duration: '30s' };

export default function () {
  const getRes = http.get('https://test-api.k6.io/public/crocodiles/');
  check(getRes, { 'GET status 200': (r) => r.status === 200 });

  const payload = JSON.stringify({ name: 'test', sex: 'M', date_of_birth: '2020-01-01' });
  const postRes = http.post('https://test-api.k6.io/anything', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(postRes, { 'POST status 2xx': (r) => r.status >= 200 && r.status < 300 });
  sleep(1);
}
```

Run with `k6 run script.js`.

## Virtual Users and Duration

```javascript
export const options = {
  vus: 50,           // 50 concurrent virtual users
  duration: '5m',    // run for 5 minutes
  iterations: 1000,  // or cap at 1000 total iterations across all VUs
};
```

## Stages (Ramp Up, Steady State, Ramp Down)

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 50 },  // ramp up
    { duration: '5m', target: 50 },  // steady state
    { duration: '2m', target: 0 },   // ramp down
  ],
};
```

## Test Types

```javascript
// Load test -- typical expected traffic
stages: [{ duration: '5m', target: 100 }, { duration: '10m', target: 100 }, { duration: '5m', target: 0 }]

// Stress test -- beyond normal capacity, stepped increases
stages: [
  { duration: '2m', target: 100 }, { duration: '5m', target: 100 },
  { duration: '2m', target: 200 }, { duration: '5m', target: 200 },
  { duration: '2m', target: 300 }, { duration: '5m', target: 300 },
  { duration: '5m', target: 0 },
]

// Soak test -- sustained load over hours
stages: [{ duration: '5m', target: 100 }, { duration: '8h', target: 100 }, { duration: '5m', target: 0 }]

// Spike test -- sudden surge
stages: [
  { duration: '1m', target: 10 }, { duration: '10s', target: 500 },
  { duration: '3m', target: 500 }, { duration: '10s', target: 10 }, { duration: '2m', target: 0 },
]

// Breakpoint test -- find system limits
{ executor: 'ramping-arrival-rate', startRate: 1, timeUnit: '1s', preAllocatedVUs: 500,
  stages: [{ duration: '30m', target: 500 }] }
```

## Checks (Assertions)

```javascript
import { check } from 'k6';
check(res, {
  'status is 200': (r) => r.status === 200,
  'body contains expected text': (r) => r.body.includes('crocodile'),
  'response time < 500ms': (r) => r.timings.duration < 500,
  'content-type is JSON': (r) => r.headers['Content-Type'].includes('application/json'),
});
```

## Thresholds (Pass/Fail Criteria)

```javascript
export const options = {
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95th percentile < 500ms
    http_req_failed: ['rate<0.01'],                   // error rate < 1%
    checks: ['rate>0.99'],                            // 99% of checks pass
    http_reqs: ['rate>100'],                          // throughput > 100 req/s
    'http_req_duration{name:login}': ['p(95)<300'],   // threshold on tagged request
  },
};
```

k6 exits non-zero when any threshold fails, suitable for CI gating.

## HTTP Methods

```javascript
import http from 'k6/http';
export default function () {
  http.get('https://api.example.com/items');
  http.post('https://api.example.com/items',
    JSON.stringify({ name: 'widget' }), { headers: { 'Content-Type': 'application/json' } });
  http.put('https://api.example.com/items/1',
    JSON.stringify({ name: 'updated' }), { headers: { 'Content-Type': 'application/json' } });
  http.del('https://api.example.com/items/1');

  // Multipart file upload
  const file = open('/path/to/file.png', 'b');
  http.post('https://api.example.com/upload', {
    file: http.file(file, 'file.png', 'image/png'),
  });
}
```

## Headers and Authentication

```javascript
// Bearer token
http.get('https://api.example.com/protected', {
  headers: { Authorization: 'Bearer eyJhbGciOi...', 'Content-Type': 'application/json' },
});

// Login in setup, pass token to default function
export function setup() {
  const res = http.post('https://api.example.com/login',
    JSON.stringify({ username: 'user', password: 'pass' }),
    { headers: { 'Content-Type': 'application/json' } });
  return { token: res.json('token') };
}
export default function (data) {
  http.get('https://api.example.com/dashboard', {
    headers: { Authorization: `Bearer ${data.token}` },
  });
}

// Cookies
const jar = http.cookieJar();
jar.set('https://api.example.com', 'session_id', 'abc123');
```

## Groups and Tags

```javascript
import { group } from 'k6';
export default function () {
  group('user flow', function () {
    group('login', function () {
      http.post('https://api.example.com/login',
        JSON.stringify({ user: 'test', pass: 'test' }),
        { headers: { 'Content-Type': 'application/json' }, tags: { name: 'login' } });
    });
    group('browse', function () {
      http.get('https://api.example.com/items', { tags: { name: 'list-items' } });
    });
  });
}
```

Tags enable filtering in thresholds and outputs: `http_req_duration{name:login}`.

## Parameterization

```javascript
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

const users = new SharedArray('users', function () {
  return JSON.parse(open('./users.json'));  // [{username: "a", password: "b"}, ...]
});
const csvData = new SharedArray('csv', function () {
  return papaparse.parse(open('./data.csv'), { header: true }).data;
});

export default function () {
  const user = users[Math.floor(Math.random() * users.length)];
  http.post('https://api.example.com/login',
    JSON.stringify({ username: user.username, password: user.password }),
    { headers: { 'Content-Type': 'application/json' } });
}
```

`SharedArray` loads data once and shares across VUs to reduce memory.

## Custom Metrics

```javascript
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

const errorCount = new Counter('custom_errors');    // cumulative count
const cacheHitRate = new Rate('cache_hits');         // percentage of true values
const pageLoadTime = new Trend('page_load_time');    // distribution (min/max/avg/p90/p95)
const activeConns = new Gauge('active_connections'); // last value

export default function () {
  const res = http.get('https://api.example.com/');
  pageLoadTime.add(res.timings.duration);
  cacheHitRate.add(res.headers['X-Cache'] === 'HIT');
  if (res.status !== 200) errorCount.add(1);
}

export const options = {
  thresholds: { page_load_time: ['p(95)<600'], custom_errors: ['count<10'] },
};
```

## Output

```bash
k6 run script.js                                                  # stdout summary
k6 run --out json=results.json script.js                          # JSON file
k6 run --out csv=results.csv script.js                            # CSV file
k6 run --out influxdb=http://localhost:8086/k6 script.js          # InfluxDB
K6_CLOUD_TOKEN=token k6 run --out cloud script.js                 # Grafana Cloud
k6 run --out json=results.json --out influxdb=http://localhost:8086/k6 script.js  # multiple
```

```javascript
// Custom summary handler
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';
export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data),
  };
}
```

## Browser Testing

```javascript
import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    ui: { executor: 'shared-iterations', options: { browser: { type: 'chromium' } } },
  },
};

export default async function () {
  const page = await browser.newPage();
  try {
    await page.goto('https://test.k6.io/my_messages.php');
    await page.locator('input[name="login"]').type('admin');
    await page.locator('input[name="password"]').type('123');
    await page.locator('input[type="submit"]').click();
    const header = await page.locator('h2').textContent();
    check(header, { 'logged in': (h) => h === 'Welcome, admin!' });
  } finally { await page.close(); }
}
```

## CI/CD Integration (GitHub Actions)

```yaml
name: Load Test
on: [push, pull_request]
jobs:
  k6-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/k6-action@v0.3.1
        with:
          filename: tests/load-test.js
        env:
          K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}
```

Thresholds serve as the quality gate -- the step fails when any threshold is breached.

## Common Patterns

### API Endpoint Test

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  stages: [{ duration: '1m', target: 50 }, { duration: '3m', target: 50 }, { duration: '1m', target: 0 }],
  thresholds: { http_req_duration: ['p(95)<500'], http_req_failed: ['rate<0.01'] },
};
export default function () {
  check(http.get('https://api.example.com/health'), { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```

### Login Flow Test

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
export default function () {
  const loginRes = http.post('https://api.example.com/auth/login',
    JSON.stringify({ email: 'user@test.com', password: 'password123' }),
    { headers: { 'Content-Type': 'application/json' }, tags: { name: 'login' } });
  check(loginRes, { 'login succeeded': (r) => r.status === 200 });
  const token = loginRes.json('access_token');
  const profileRes = http.get('https://api.example.com/me', {
    headers: { Authorization: `Bearer ${token}` }, tags: { name: 'profile' } });
  check(profileRes, { 'profile loaded': (r) => r.status === 200 });
  sleep(1);
}
```

### File Upload Test

```javascript
import http from 'k6/http';
import { check } from 'k6';
const testFile = open('/path/to/test-file.pdf', 'b');
export default function () {
  const res = http.post('https://api.example.com/upload', {
    file: http.file(testFile, 'report.pdf', 'application/pdf'),
  });
  check(res, { 'upload ok': (r) => r.status === 200, 'under 5s': (r) => r.timings.duration < 5000 });
}
```
