---
name: logging
description: This skill should be used when the user asks to "add logging", "set up structured logging", "configure log levels", "create a logger", "set up log rotation", "send logs to ELK", "configure Winston", "set up Pino", "add request logging", "implement audit logging", or mentions logging best practices, structured logging, log aggregation, log levels, observability, log rotation, or centralized logging.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - logging
    - structured-logging
    - observability
    - winston
    - pino
    - elk
    - log-management
---

# Logging

Comprehensive guide to application logging: structured logging, log levels, library choices, centralized aggregation, security considerations, and production-grade patterns across languages and frameworks.

## Logging Levels

Standard logging levels from least to most severe:

| Level | Value | Purpose | Example |
|-------|-------|---------|---------|
| TRACE | 10 | Ultra-fine-grained diagnostic detail | Entering/exiting functions, variable values |
| DEBUG | 20 | Diagnostic information for developers | SQL queries, cache lookups, parsed configs |
| INFO | 30 | Normal operational events | Server started, user logged in, job completed |
| WARN | 40 | Unexpected but recoverable situations | Deprecated API used, retry attempt, slow query |
| ERROR | 50 | Failure in a specific operation | Database connection failed, API call timeout |
| FATAL | 60 | System-wide unrecoverable failure | Out of memory, missing critical config, corrupted state |

### Level Selection Guidelines

- **Production**: Set to INFO (or WARN for high-throughput services).
- **Staging**: Set to DEBUG to catch issues before production.
- **Development**: Set to TRACE for maximum visibility.
- **Per-module overrides**: Allow specific modules to log at a finer level without flooding the entire log.
- **Dynamic level changes**: Support runtime log level adjustment without restarts (e.g., via admin API or environment variable reload).

## Structured Logging (JSON Format)

Always use structured logging in production. Plain text logs are difficult to parse, filter, and aggregate.

### Structured Log Entry Example

```json
{
  "timestamp": "2025-09-15T14:23:07.412Z",
  "level": "ERROR",
  "logger": "com.myapp.UserService",
  "message": "Failed to fetch user profile",
  "service": "user-service",
  "environment": "production",
  "version": "2.4.1",
  "host": "ip-10-0-3-42",
  "correlationId": "req_a1b2c3d4e5",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "userId": "usr_88291",
  "error": {
    "type": "DatabaseTimeoutError",
    "message": "Connection timed out after 5000ms",
    "stack": "DatabaseTimeoutError: Connection timed out...\n    at Pool.query (/app/db.js:42:11)"
  },
  "duration_ms": 5023,
  "metadata": {
    "db_host": "primary-rds.us-east-1",
    "retry_count": 3
  }
}
```

### Why Structured Logging Matters

1. **Machine-parseable**: Log aggregation tools can index and query fields directly.
2. **Consistent schema**: Every log entry follows the same shape, enabling reliable alerting.
3. **Contextual richness**: Attach arbitrary metadata (user ID, request ID, tenant ID) to each entry.
4. **Filterable**: Query logs by level, service, user, time range, or any field combination.

## Node.js Logging

### Winston

Winston is the most popular Node.js logging library with transport-based architecture.

```javascript
// logger.js - Winston configuration
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DDTHH:mm:ss.SSSZ' }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'my-app',
    environment: process.env.NODE_ENV || 'development',
    version: process.env.APP_VERSION || '0.0.0',
  },
  transports: [
    // Write errors to a dedicated file
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 5,
      tailable: true,
    }),
    // Write all logs to combined file
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 50 * 1024 * 1024, // 50MB
      maxFiles: 10,
      tailable: true,
    }),
  ],
});

// In development, also log to console with colorized output
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
  }));
}

module.exports = logger;
```

### Pino

Pino is the fastest Node.js logger, optimized for low overhead in production.

```javascript
// logger.js - Pino configuration
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level(label) {
      return { level: label };
    },
    bindings(bindings) {
      return {
        pid: bindings.pid,
        host: bindings.hostname,
        service: process.env.SERVICE_NAME || 'my-app',
      };
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  redact: {
    paths: ['req.headers.authorization', 'req.headers.cookie', 'body.password',
            'body.ssn', 'body.creditCard', '*.token', '*.secret'],
    censor: '[REDACTED]',
  },
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
});

module.exports = logger;
```

### Pino with Express Middleware

```javascript
const pinoHttp = require('pino-http');
const logger = require('./logger');

app.use(pinoHttp({
  logger,
  autoLogging: {
    ignore: (req) => req.url === '/health' || req.url === '/ready',
  },
  customLogLevel: (req, res, err) => {
    if (res.statusCode >= 500 || err) return 'error';
    if (res.statusCode >= 400) return 'warn';
    return 'info';
  },
  customSuccessMessage: (req, res) => {
    return `${req.method} ${req.url} completed with ${res.statusCode}`;
  },
  customErrorMessage: (req, res, err) => {
    return `${req.method} ${req.url} failed with ${res.statusCode}: ${err.message}`;
  },
  customProps: (req) => ({
    correlationId: req.headers['x-correlation-id'] || req.id,
  }),
}));
```

### Bunyan

```javascript
const bunyan = require('bunyan');

const logger = bunyan.createLogger({
  name: 'my-app',
  level: process.env.LOG_LEVEL || 'info',
  serializers: bunyan.stdSerializers,
  streams: [
    { level: 'info', stream: process.stdout },
    { level: 'error', path: 'logs/error.log' },
    {
      level: 'debug',
      type: 'rotating-file',
      path: 'logs/debug.log',
      period: '1d',
      count: 7,
    },
  ],
});
```

## Python Logging

### Standard Library logging

```python
# logging_config.py
import logging
import logging.config
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON log entries."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        # Include any extra fields passed via the `extra` parameter
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__ and key not in ("message", "asctime"):
                log_entry[key] = value
        return json.dumps(log_entry)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JSONFormatter,
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "logs/error.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "level": "ERROR",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file", "error_file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

### structlog

```python
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# Usage with bound context
request_log = log.bind(
    correlation_id="req_a1b2c3",
    user_id="usr_88291",
    service="user-service",
)
request_log.info("processing_request", endpoint="/api/users", method="GET")
request_log.error("request_failed", error="timeout", duration_ms=5023)
```

### Loguru

```python
from loguru import logger
import sys

# Remove default handler and configure structured output
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DDTHH:mm:ss.SSS}Z | {level: <8} | {name}:{function}:{line} | {message}",
    level="INFO",
    serialize=True,  # Output as JSON
)
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    compression="gz",
    serialize=True,
    level="DEBUG",
)
logger.add(
    "logs/error.log",
    rotation="50 MB",
    retention="90 days",
    compression="gz",
    level="ERROR",
    backtrace=True,
    diagnose=True,
)

# Usage
logger.info("User logged in", user_id="usr_88291", ip="192.168.1.10")
```

## Java Logging

### SLF4J + Logback

```xml
<!-- logback.xml -->
<configuration>
  <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <includeMdcKeyName>correlationId</includeMdcKeyName>
      <includeMdcKeyName>userId</includeMdcKeyName>
      <customFields>{"service":"user-service","environment":"${ENV:-dev}"}</customFields>
    </encoder>
  </appender>

  <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/application.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
      <fileNamePattern>logs/application.%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
      <maxFileSize>100MB</maxFileSize>
      <maxHistory>30</maxHistory>
      <totalSizeCap>3GB</totalSizeCap>
    </rollingPolicy>
    <encoder class="net.logstash.logback.encoder.LogstashEncoder" />
  </appender>

  <root level="INFO">
    <appender-ref ref="CONSOLE" />
    <appender-ref ref="FILE" />
  </root>

  <!-- Per-package log levels -->
  <logger name="com.myapp.repository" level="DEBUG" />
  <logger name="org.hibernate.SQL" level="DEBUG" />
  <logger name="org.springframework.web" level="WARN" />
</configuration>
```

```java
// Usage with SLF4J
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    public User getUser(String userId) {
        MDC.put("userId", userId);
        MDC.put("correlationId", RequestContext.getCorrelationId());
        try {
            log.info("Fetching user profile");
            User user = userRepository.findById(userId);
            log.debug("User fetched successfully, roles={}", user.getRoles());
            return user;
        } catch (Exception e) {
            log.error("Failed to fetch user profile", e);
            throw e;
        } finally {
            MDC.clear();
        }
    }
}
```

### Log4j2

```xml
<!-- log4j2.xml -->
<Configuration status="WARN">
  <Appenders>
    <Console name="Console" target="SYSTEM_OUT">
      <JsonLayout compact="true" eventEol="true" stacktraceAsString="true">
        <KeyValuePair key="service" value="${env:SERVICE_NAME:-my-app}" />
        <KeyValuePair key="environment" value="${env:ENV:-dev}" />
      </JsonLayout>
    </Console>
    <RollingFile name="File" fileName="logs/app.log"
                 filePattern="logs/app-%d{yyyy-MM-dd}-%i.log.gz">
      <JsonLayout compact="true" eventEol="true" />
      <Policies>
        <SizeBasedTriggeringPolicy size="100MB" />
        <TimeBasedTriggeringPolicy interval="1" modulate="true" />
      </Policies>
      <DefaultRolloverStrategy max="30" />
    </RollingFile>
  </Appenders>
  <Loggers>
    <Root level="info">
      <AppenderRef ref="Console" />
      <AppenderRef ref="File" />
    </Root>
  </Loggers>
</Configuration>
```

## Go Logging

### slog (Standard Library, Go 1.21+)

```go
package main

import (
    "context"
    "log/slog"
    "os"
)

func setupLogger() *slog.Logger {
    opts := &slog.HandlerOptions{
        Level:     slog.LevelInfo,
        AddSource: true,
        ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
            // Redact sensitive fields
            if a.Key == "password" || a.Key == "token" || a.Key == "secret" {
                a.Value = slog.StringValue("[REDACTED]")
            }
            return a
        },
    }
    handler := slog.NewJSONHandler(os.Stdout, opts)
    return slog.New(handler)
}

func main() {
    logger := setupLogger()
    slog.SetDefault(logger)

    // Basic logging
    slog.Info("server starting", "port", 8080, "version", "2.4.1")

    // With context and groups
    ctx := context.Background()
    slog.InfoContext(ctx, "processing request",
        slog.Group("request",
            slog.String("method", "GET"),
            slog.String("path", "/api/users"),
            slog.String("correlationId", "req_a1b2c3"),
        ),
        slog.Group("user",
            slog.String("id", "usr_88291"),
        ),
    )
}
```

### Zap (Uber)

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "time"
)

func NewLogger() (*zap.Logger, error) {
    config := zap.Config{
        Level:            zap.NewAtomicLevelAt(zap.InfoLevel),
        Development:      false,
        Encoding:         "json",
        EncoderConfig: zapcore.EncoderConfig{
            TimeKey:        "timestamp",
            LevelKey:       "level",
            NameKey:        "logger",
            CallerKey:      "caller",
            MessageKey:     "message",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.MillisDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout", "logs/app.log"},
        ErrorOutputPaths:  []string{"stderr"},
        InitialFields: map[string]interface{}{
            "service": "user-service",
        },
    }
    return config.Build()
}

func main() {
    logger, _ := NewLogger()
    defer logger.Sync()

    logger.Info("request processed",
        zap.String("method", "GET"),
        zap.String("path", "/api/users"),
        zap.Duration("latency", 42*time.Millisecond),
        zap.Int("status", 200),
    )
}
```

### Zerolog

```go
package main

import (
    "os"
    "time"

    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
)

func init() {
    zerolog.TimeFieldFormat = time.RFC3339Nano
    zerolog.SetGlobalLevel(zerolog.InfoLevel)

    log.Logger = zerolog.New(os.Stdout).
        With().
        Timestamp().
        Str("service", "user-service").
        Str("version", "2.4.1").
        Caller().
        Logger()
}

func main() {
    log.Info().
        Str("method", "GET").
        Str("path", "/api/users").
        Dur("latency", 42*time.Millisecond).
        Int("status", 200).
        Msg("request processed")
}
```

## Request/Response Logging Middleware

### Express.js Middleware

```javascript
const { v4: uuidv4 } = require('uuid');
const { AsyncLocalStorage } = require('async_hooks');
const logger = require('./logger');

const asyncLocalStorage = new AsyncLocalStorage();

function requestLoggingMiddleware(req, res, next) {
  const correlationId = req.headers['x-correlation-id'] || uuidv4();
  const startTime = process.hrtime.bigint();

  // Store context for the lifetime of this request
  const context = { correlationId, startTime };
  req.correlationId = correlationId;
  res.setHeader('X-Correlation-Id', correlationId);

  // Log the incoming request
  logger.info('request_received', {
    correlationId,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('user-agent'),
  });

  // Capture response finish
  const originalEnd = res.end;
  res.end = function (...args) {
    const duration = Number(process.hrtime.bigint() - startTime) / 1e6;
    logger.info('request_completed', {
      correlationId,
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration_ms: Math.round(duration * 100) / 100,
      contentLength: res.get('content-length'),
    });
    originalEnd.apply(res, args);
  };

  asyncLocalStorage.run(context, () => next());
}

// Helper to retrieve correlation ID anywhere in the call stack
function getCorrelationId() {
  const store = asyncLocalStorage.getStore();
  return store?.correlationId || 'unknown';
}

module.exports = { requestLoggingMiddleware, getCorrelationId };
```

### Python FastAPI Middleware

```python
import time
import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="unknown")
log = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        start_time = time.perf_counter()
        log.info(
            "request_received",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            log.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            response.headers["X-Correlation-Id"] = correlation_id
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_ms=round(duration_ms, 2),
            )
            raise
        finally:
            structlog.contextvars.unbind_contextvars("correlation_id")
```

## Correlation IDs and Distributed Tracing

### Propagation Pattern

```
Client --> API Gateway --> Service A --> Service B --> Database
  |           |               |              |
  |    correlationId     correlationId   correlationId
  |    traceId           traceId         traceId
  |    spanId: span-1    spanId: span-2  spanId: span-3
```

### Implementation Rules

1. **Generate** a correlation ID at the system boundary (API gateway or first service to receive the request).
2. **Propagate** via HTTP headers (`X-Correlation-Id`, `traceparent` for W3C Trace Context).
3. **Attach** to every log entry within that request scope.
4. **Pass downstream** in all outgoing HTTP calls, message queue messages, and async tasks.
5. **Use OpenTelemetry** for standardized trace propagation across languages and frameworks.

### OpenTelemetry Integration

```javascript
// opentelemetry-setup.js
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');

const provider = new NodeTracerProvider();

provider.addSpanProcessor(new SimpleSpanProcessor(
  new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' })
));

provider.register();

registerInstrumentations({
  instrumentations: [getNodeAutoInstrumentations()],
});
```

## Log Rotation and Retention

### Linux logrotate Configuration

```
# /etc/logrotate.d/myapp
/var/log/myapp/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    maxsize 100M
    dateext
    dateformat -%Y%m%d
    postrotate
        /usr/bin/systemctl reload myapp > /dev/null 2>&1 || true
    endscript
}
```

### Retention Policy Guidelines

| Log Type | Retention | Rationale |
|----------|-----------|-----------|
| Application logs | 30 days | Debugging recent issues |
| Access logs | 90 days | Security auditing, compliance |
| Audit logs | 1-7 years | Regulatory compliance (HIPAA, SOX, PCI-DSS) |
| Error logs | 90 days | Root cause analysis |
| Debug logs | 7 days | Short-term diagnostics only |
| Security event logs | 1 year+ | Incident response, forensics |

### Docker Logging Configuration

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5",
    "compress": "true",
    "labels": "service,environment"
  }
}
```

## Centralized Logging

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose.yml - ELK stack
version: "3.8"
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  es-data:
```

### Logstash Pipeline

```ruby
# logstash/pipeline/logstash.conf
input {
  beats { port => 5044 }
  tcp {
    port => 5000
    codec => json_lines
  }
}

filter {
  if [level] == "ERROR" or [level] == "FATAL" {
    mutate { add_tag => ["alert_worthy"] }
  }
  if [duration_ms] and [duration_ms] > 5000 {
    mutate { add_tag => ["slow_request"] }
  }
  # Remove sensitive fields
  mutate {
    remove_field => ["password", "token", "secret", "authorization"]
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "logs-%{[service]}-%{+YYYY.MM.dd}"
  }
}
```

### Grafana Loki (Lightweight Alternative)

```yaml
# promtail-config.yml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: application
    static_configs:
      - targets: ["localhost"]
        labels:
          job: myapp
          __path__: /var/log/myapp/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            service: service
            correlationId: correlationId
      - labels:
          level:
          service:
```

### Datadog Log Collection

```yaml
# datadog-agent.yaml
logs_enabled: true
logs_config:
  container_collect_all: true
  processing_rules:
    - type: mask_sequences
      name: mask_credit_cards
      replace_placeholder: "[MASKED_CC]"
      pattern: '\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    - type: mask_sequences
      name: mask_ssn
      replace_placeholder: "[MASKED_SSN]"
      pattern: '\b\d{3}-\d{2}-\d{4}\b'
```

## What to Log and What NOT to Log

### Always Log

- Request/response metadata (method, URL, status code, duration)
- Authentication events (login, logout, failed attempts, token refresh)
- Authorization failures (access denied)
- Business-critical operations (order placed, payment processed, user created)
- Errors and exceptions with full stack traces
- External service calls (API, database, cache) with latency
- Configuration changes and deployments
- Health check results and dependency status

### Never Log

- **Passwords** or authentication credentials
- **API keys**, tokens, or secrets
- **PII**: Social Security numbers, full credit card numbers, date of birth
- **PHI**: Medical records, health information (HIPAA)
- **Session tokens** or cookies in full
- **Request/response bodies** containing sensitive user data
- **Encryption keys** or certificates
- **Database connection strings** with embedded credentials

### Redaction Patterns

```javascript
// Pino redaction (recommended approach)
const logger = pino({
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      'body.password',
      'body.ssn',
      'body.creditCard',
      'body.dateOfBirth',
      '*.apiKey',
      '*.secret',
      '*.token',
    ],
    censor: '[REDACTED]',
  },
});

// Manual redaction utility
function redactSensitive(obj) {
  const sensitiveKeys = /password|secret|token|apikey|authorization|ssn|credit/i;
  return JSON.parse(JSON.stringify(obj, (key, value) => {
    if (sensitiveKeys.test(key)) return '[REDACTED]';
    return value;
  }));
}
```

## Performance Logging (Timing and Metrics)

### Timer Utility

```javascript
class PerformanceLogger {
  constructor(logger) {
    this.logger = logger;
  }

  async time(label, fn, metadata = {}) {
    const start = process.hrtime.bigint();
    try {
      const result = await fn();
      const duration = Number(process.hrtime.bigint() - start) / 1e6;
      this.logger.info('operation_completed', {
        operation: label,
        duration_ms: Math.round(duration * 100) / 100,
        success: true,
        ...metadata,
      });
      return result;
    } catch (error) {
      const duration = Number(process.hrtime.bigint() - start) / 1e6;
      this.logger.error('operation_failed', {
        operation: label,
        duration_ms: Math.round(duration * 100) / 100,
        success: false,
        error: error.message,
        ...metadata,
      });
      throw error;
    }
  }
}

// Usage
const perfLogger = new PerformanceLogger(logger);
const users = await perfLogger.time('fetch_users', () => db.query('SELECT * FROM users'), {
  table: 'users',
  query_type: 'select',
});
```

### Slow Query Detection

```python
import functools
import time
import structlog

log = structlog.get_logger()

def log_slow(threshold_ms=1000):
    """Decorator that logs a warning if a function exceeds the threshold."""
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await fn(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                if elapsed_ms > threshold_ms:
                    log.warning(
                        "slow_operation",
                        function=fn.__name__,
                        duration_ms=round(elapsed_ms, 2),
                        threshold_ms=threshold_ms,
                    )
        return wrapper
    return decorator

@log_slow(threshold_ms=500)
async def fetch_user_profile(user_id: str):
    return await db.users.find_one({"_id": user_id})
```

## Audit Logging Patterns

### Audit Log Schema

```json
{
  "timestamp": "2025-09-15T14:23:07.412Z",
  "eventType": "USER_ROLE_CHANGED",
  "actor": {
    "id": "usr_admin_001",
    "type": "user",
    "ip": "10.0.1.50",
    "userAgent": "Mozilla/5.0..."
  },
  "target": {
    "type": "user",
    "id": "usr_88291",
    "name": "john.doe@example.com"
  },
  "action": "UPDATE",
  "changes": {
    "before": { "role": "viewer" },
    "after": { "role": "admin" }
  },
  "result": "SUCCESS",
  "correlationId": "req_a1b2c3d4e5",
  "metadata": {
    "reason": "Promotion approved by VP Engineering",
    "approvalTicket": "JIRA-4521"
  }
}
```

### Audit Logger Implementation

```javascript
class AuditLogger {
  constructor(logger, store) {
    this.logger = logger;
    this.store = store; // Persistent, append-only store
  }

  async log({ eventType, actor, target, action, changes, result, metadata }) {
    const entry = {
      timestamp: new Date().toISOString(),
      eventType,
      actor,
      target,
      action,
      changes,
      result,
      correlationId: getCorrelationId(),
      metadata,
    };

    // Write to append-only audit store (database or immutable log)
    await this.store.append(entry);

    // Also send to standard logger for aggregation
    this.logger.info('audit_event', entry);
  }
}

// Usage
await auditLogger.log({
  eventType: 'USER_ROLE_CHANGED',
  actor: { id: req.user.id, type: 'user', ip: req.ip },
  target: { type: 'user', id: targetUserId },
  action: 'UPDATE',
  changes: { before: { role: 'viewer' }, after: { role: 'admin' } },
  result: 'SUCCESS',
  metadata: { reason: 'Promotion', approvalTicket: 'JIRA-4521' },
});
```

## Log Format Standards

### Recommended Fields for Every Log Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | ISO 8601 string | Yes | When the event occurred |
| level | string | Yes | Log severity level |
| message | string | Yes | Human-readable description |
| service | string | Yes | Name of the emitting service |
| environment | string | Yes | dev, staging, production |
| correlationId | string | Recommended | Request trace identifier |
| traceId | string | Recommended | Distributed trace ID (OpenTelemetry) |
| host | string | Recommended | Hostname or pod name |
| version | string | Recommended | Application version |
| error | object | Conditional | Error details (when level >= ERROR) |
| duration_ms | number | Conditional | Operation duration in milliseconds |

## Alert-Worthy Log Patterns

Configure alerts when these patterns appear:

| Pattern | Alert Level | Action |
|---------|-------------|--------|
| FATAL level log | P1 - Critical | Page on-call immediately |
| Error rate > 5% over 5 minutes | P1 - Critical | Page on-call |
| Repeated auth failures from same IP | P2 - High | Notify security team |
| 5xx response rate spike | P2 - High | Page on-call |
| Slow query > 10s | P3 - Medium | Create ticket |
| Disk space for logs > 85% | P3 - Medium | Notify ops team |
| Deprecated API usage increase | P4 - Low | Create ticket for next sprint |
| New unique error message | P4 - Low | Review in daily triage |

## Contextual Logging

### Node.js AsyncLocalStorage (Continuation-Local Storage)

```javascript
const { AsyncLocalStorage } = require('async_hooks');

const asyncLocalStorage = new AsyncLocalStorage();

// Middleware to establish context
function contextMiddleware(req, res, next) {
  const context = {
    correlationId: req.headers['x-correlation-id'] || uuidv4(),
    userId: req.user?.id,
    tenantId: req.headers['x-tenant-id'],
    requestPath: req.path,
  };
  asyncLocalStorage.run(context, next);
}

// Logger wrapper that automatically includes context
function createContextualLogger(baseLogger) {
  return {
    info: (msg, extra = {}) => {
      const ctx = asyncLocalStorage.getStore() || {};
      baseLogger.info({ ...ctx, ...extra, message: msg });
    },
    error: (msg, extra = {}) => {
      const ctx = asyncLocalStorage.getStore() || {};
      baseLogger.error({ ...ctx, ...extra, message: msg });
    },
    warn: (msg, extra = {}) => {
      const ctx = asyncLocalStorage.getStore() || {};
      baseLogger.warn({ ...ctx, ...extra, message: msg });
    },
    debug: (msg, extra = {}) => {
      const ctx = asyncLocalStorage.getStore() || {};
      baseLogger.debug({ ...ctx, ...extra, message: msg });
    },
  };
}
```

### Java MDC (Mapped Diagnostic Context)

```java
import org.slf4j.MDC;
import javax.servlet.*;
import java.io.IOException;
import java.util.UUID;

public class MDCFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        try {
            HttpServletRequest httpReq = (HttpServletRequest) req;
            String correlationId = httpReq.getHeader("X-Correlation-Id");
            if (correlationId == null) {
                correlationId = UUID.randomUUID().toString();
            }
            MDC.put("correlationId", correlationId);
            MDC.put("userId", getCurrentUserId(httpReq));
            MDC.put("requestPath", httpReq.getRequestURI());

            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}
```

### Python contextvars

```python
from contextvars import ContextVar
import structlog

# Define context variables
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="none")
user_id: ContextVar[str] = ContextVar("user_id", default="anonymous")
tenant_id: ContextVar[str] = ContextVar("tenant_id", default="unknown")

# Configure structlog to automatically include contextvars
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

# In middleware
async def logging_middleware(request, call_next):
    structlog.contextvars.bind_contextvars(
        correlation_id=request.headers.get("X-Correlation-Id", str(uuid.uuid4())),
        user_id=getattr(request.state, "user_id", "anonymous"),
        tenant_id=request.headers.get("X-Tenant-Id", "unknown"),
    )
    response = await call_next(request)
    structlog.contextvars.unbind_contextvars("correlation_id", "user_id", "tenant_id")
    return response
```

## Log Sampling for High-Traffic Systems

In high-throughput services (thousands of requests per second), logging every event becomes cost-prohibitive. Sampling reduces volume while preserving visibility.

### Sampling Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Rate-based | Log 1 in N requests | General traffic reduction |
| Probabilistic | Random chance per event (e.g., 10%) | Uniform sampling across all traffic |
| Priority-based | Always log errors; sample info/debug | Ensure errors are never lost |
| Head-based | Decide at request start, propagate | Consistent per-request view |
| Tail-based | Decide after request completes | Sample only interesting requests (errors, slow) |
| Adaptive | Adjust rate based on current volume | Handle traffic spikes gracefully |

### Implementation

```javascript
class SampledLogger {
  constructor(logger, options = {}) {
    this.logger = logger;
    this.sampleRate = options.sampleRate || 0.1; // 10% of info logs
    this.alwaysLogLevels = new Set(options.alwaysLogLevels || ['warn', 'error', 'fatal']);
    this.counter = 0;
    this.rateBasedInterval = options.rateBasedInterval || 100; // Log 1 in 100
  }

  _shouldLog(level) {
    if (this.alwaysLogLevels.has(level)) return true;
    // Probabilistic sampling for non-critical levels
    return Math.random() < this.sampleRate;
  }

  info(msg, meta = {}) {
    if (this._shouldLog('info')) {
      this.logger.info(msg, { ...meta, sampled: true, sampleRate: this.sampleRate });
    }
  }

  debug(msg, meta = {}) {
    if (this._shouldLog('debug')) {
      this.logger.debug(msg, { ...meta, sampled: true, sampleRate: this.sampleRate });
    }
  }

  warn(msg, meta = {}) {
    this.logger.warn(msg, meta); // Always log warnings
  }

  error(msg, meta = {}) {
    this.logger.error(msg, meta); // Always log errors
  }
}

// Usage: only 10% of info/debug logs are emitted
const sampledLogger = new SampledLogger(logger, {
  sampleRate: 0.1,
  alwaysLogLevels: ['warn', 'error', 'fatal'],
});
```

### OpenTelemetry Tail-Based Sampling

```yaml
# otel-collector-config.yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      - name: always-sample-errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: always-sample-slow
        type: latency
        latency:
          threshold_ms: 5000
      - name: probabilistic-sample-rest
        type: probabilistic
        probabilistic:
          sampling_percentage: 10
```

## References

- [The Twelve-Factor App - Logs](https://12factor.net/logs)
- [OpenTelemetry Logging Specification](https://opentelemetry.io/docs/specs/otel/logs/)
- [Winston Documentation](https://github.com/winstonjs/winston)
- [Pino Documentation](https://getpino.io/)
- [structlog Documentation](https://www.structlog.org/)
- [SLF4J Manual](https://www.slf4j.org/manual.html)
- [Go slog Package](https://pkg.go.dev/log/slog)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
