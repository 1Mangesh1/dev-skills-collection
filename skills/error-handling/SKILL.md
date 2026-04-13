---
name: error-handling
description: This skill should be used when the user asks to "handle errors", "add error handling", "create custom errors", "handle exceptions", "implement retry logic", "add error boundaries", "design error responses", "handle async errors", "create error types", "implement graceful degradation", or mentions error handling patterns, exception handling, error boundaries, retry strategies, circuit breakers, or error recovery.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - error-handling
    - exceptions
    - retry
    - circuit-breaker
    - resilience
    - fault-tolerance
---

# Error Handling Patterns & Best Practices

Comprehensive error handling strategies across languages and frameworks for building resilient, fault-tolerant software systems.

## Error Handling Philosophy

### Fail Fast
Detect problems as early as possible and report them immediately. Do not let invalid state propagate through the system.

- Validate inputs at system boundaries
- Use assertions for invariants during development
- Throw on impossible states rather than returning defaults
- Prefer compile-time checks over runtime checks

### Fail Gracefully
When failure is unavoidable, degrade functionality rather than crashing the entire system.

- Provide fallback values or cached responses
- Shed load intelligently under pressure
- Communicate errors clearly to the caller
- Preserve as much functionality as possible

### Operational vs Programmer Errors

| Aspect              | Operational Errors                  | Programmer Errors                  |
|---------------------|-------------------------------------|------------------------------------|
| Cause               | Runtime conditions (network, disk)  | Bugs in code (null ref, bad logic) |
| Predictable?        | Yes                                 | No                                 |
| Handling             | Retry, fallback, alert             | Fix the code                       |
| Examples            | Timeout, DNS failure, disk full     | TypeError, off-by-one, null deref  |
| Recovery            | Automated or manual intervention    | Deploy a fix                       |

---

## JavaScript / TypeScript Error Handling

### Basic try/catch

```typescript
try {
  const data = JSON.parse(rawInput);
  processData(data);
} catch (error: unknown) {
  if (error instanceof SyntaxError) {
    console.error("Invalid JSON:", error.message);
  } else if (error instanceof TypeError) {
    console.error("Type error during processing:", error.message);
  } else {
    throw error; // Re-throw unknown errors
  }
}
```

### Async/Await Error Handling

```typescript
async function fetchUserData(userId: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new HttpError(response.status, `Failed to fetch user: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof HttpError) {
      throw error;
    }
    throw new NetworkError("Unable to reach the server", { cause: error });
  }
}
```

### Promise.allSettled for Concurrent Operations

```typescript
async function fetchMultipleResources(ids: string[]) {
  const results = await Promise.allSettled(
    ids.map(id => fetchResource(id))
  );

  const successes: Resource[] = [];
  const failures: { id: string; reason: unknown }[] = [];

  results.forEach((result, index) => {
    if (result.status === "fulfilled") {
      successes.push(result.value);
    } else {
      failures.push({ id: ids[index], reason: result.reason });
    }
  });

  if (failures.length > 0) {
    console.warn(`Failed to fetch ${failures.length}/${ids.length} resources`);
  }

  return { successes, failures };
}
```

### Custom Error Classes (TypeScript)

```typescript
class AppError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly context?: Record<string, unknown>;

  constructor(options: {
    message: string;
    code: string;
    statusCode?: number;
    isOperational?: boolean;
    cause?: Error;
    context?: Record<string, unknown>;
  }) {
    super(options.message, { cause: options.cause });
    this.name = this.constructor.name;
    this.code = options.code;
    this.statusCode = options.statusCode ?? 500;
    this.isOperational = options.isOperational ?? true;
    this.context = options.context;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super({
      message: `${resource} with id '${id}' not found`,
      code: "RESOURCE_NOT_FOUND",
      statusCode: 404,
      context: { resource, id },
    });
  }
}

class ValidationError extends AppError {
  public readonly fields: Record<string, string[]>;

  constructor(fields: Record<string, string[]>) {
    const fieldNames = Object.keys(fields).join(", ");
    super({
      message: `Validation failed for fields: ${fieldNames}`,
      code: "VALIDATION_ERROR",
      statusCode: 422,
      context: { fields },
    });
    this.fields = fields;
  }
}

class ConflictError extends AppError {
  constructor(message: string) {
    super({
      message,
      code: "CONFLICT",
      statusCode: 409,
    });
  }
}
```

### Global Error Handlers (Node.js)

```typescript
// Catch unhandled promise rejections
process.on("unhandledRejection", (reason: unknown, promise: Promise<unknown>) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
  // Log to monitoring service
  monitor.captureException(reason);
  // Optionally exit for critical failures
  // process.exit(1);
});

// Catch uncaught exceptions
process.on("uncaughtException", (error: Error) => {
  console.error("Uncaught Exception:", error);
  monitor.captureException(error);
  // Always exit on uncaught exceptions - state may be corrupted
  process.exit(1);
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("SIGTERM received. Starting graceful shutdown...");
  await server.close();
  await database.disconnect();
  process.exit(0);
});
```

---

## Python Exception Handling

### try/except/else/finally

```python
def read_config(path: str) -> dict:
    """Read and parse a JSON configuration file."""
    try:
        with open(path, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except PermissionError:
        raise ConfigError(f"Permission denied reading: {path}")
    else:
        # Runs only if no exception occurred
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {path}: {e}")
    finally:
        # Always runs - cleanup goes here
        logger.debug(f"Finished config read attempt for {path}")
```

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, code: str, status_code: int = 500,
                 context: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.context = context or {}
        self.is_operational = True

    def to_dict(self) -> dict:
        return {
            "error": {
                "type": self.code,
                "title": self.__class__.__name__,
                "detail": self.message,
                "status": self.status_code,
                **({k: v for k, v in self.context.items()} if self.context else {}),
            }
        }


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            context={"resource": resource, "identifier": identifier},
        )


class ValidationError(AppError):
    def __init__(self, errors: dict[str, list[str]]):
        super().__init__(
            message="Validation failed",
            code="VALIDATION_ERROR",
            status_code=422,
            context={"fields": errors},
        )
        self.field_errors = errors


class RateLimitError(AppError):
    def __init__(self, retry_after: int):
        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            context={"retry_after": retry_after},
        )
```

### Context Managers for Error Handling

```python
from contextlib import contextmanager

@contextmanager
def error_boundary(operation: str, reraise: bool = True):
    """Context manager that logs errors and optionally suppresses them."""
    try:
        yield
    except AppError:
        raise  # Let operational errors propagate
    except Exception as exc:
        logger.exception(f"Unexpected error during {operation}")
        monitor.capture_exception(exc)
        if reraise:
            raise AppError(
                message=f"Internal error during {operation}",
                code="INTERNAL_ERROR",
            ) from exc

# Usage
with error_boundary("user_creation"):
    user = create_user(data)
```

---

## Go Error Handling

### Error Interface and Wrapping

```go
package apperr

import (
    "errors"
    "fmt"
)

// AppError represents a structured application error.
type AppError struct {
    Code       string
    Message    string
    StatusCode int
    Err        error // wrapped error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// Sentinel errors
var (
    ErrNotFound     = &AppError{Code: "NOT_FOUND", StatusCode: 404}
    ErrUnauthorized = &AppError{Code: "UNAUTHORIZED", StatusCode: 401}
    ErrConflict     = &AppError{Code: "CONFLICT", StatusCode: 409}
)

// NewNotFound creates a not-found error for a specific resource.
func NewNotFound(resource, id string) error {
    return &AppError{
        Code:       "NOT_FOUND",
        Message:    fmt.Sprintf("%s '%s' not found", resource, id),
        StatusCode: 404,
    }
}

// Wrap adds context to an error.
func Wrap(err error, message string) error {
    return fmt.Errorf("%s: %w", message, err)
}
```

### errors.Is and errors.As

```go
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        // Check for specific sentinel errors
        if errors.Is(err, sql.ErrNoRows) {
            return nil, NewNotFound("user", id)
        }
        return nil, Wrap(err, "failed to query user")
    }
    return user, nil
}

func handleError(err error) {
    var appErr *AppError
    if errors.As(err, &appErr) {
        // We have a structured error - use its code and status
        respondWithError(appErr.StatusCode, appErr.Code, appErr.Message)
    } else {
        // Unknown error - log and return generic 500
        log.Printf("unexpected error: %v", err)
        respondWithError(500, "INTERNAL_ERROR", "An internal error occurred")
    }
}
```

---

## Java Exception Handling

### Checked vs Unchecked Exceptions

```java
// Checked exception - caller must handle
public class ResourceNotFoundException extends Exception {
    private final String resource;
    private final String identifier;

    public ResourceNotFoundException(String resource, String identifier) {
        super(String.format("%s '%s' not found", resource, identifier));
        this.resource = resource;
        this.identifier = identifier;
    }

    public String getResource() { return resource; }
    public String getIdentifier() { return identifier; }
}

// Unchecked exception - for programmer errors
public class InvalidStateException extends RuntimeException {
    public InvalidStateException(String message) {
        super(message);
    }
}
```

### try-with-resources

```java
public List<User> readUsersFromCsv(Path path) throws UserImportException {
    List<User> users = new ArrayList<>();
    try (
        var reader = Files.newBufferedReader(path);
        var csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withHeader())
    ) {
        for (CSVRecord record : csvParser) {
            users.add(parseUser(record));
        }
    } catch (IOException e) {
        throw new UserImportException("Failed to read CSV file: " + path, e);
    } catch (IllegalArgumentException e) {
        throw new UserImportException("Malformed CSV record in: " + path, e);
    }
    return users;
}
```

---

## Rust Error Handling

### Result, Option, and the ? Operator

```rust
use std::fs;
use std::io;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Resource '{resource}' with id '{id}' not found")]
    NotFound { resource: String, id: String },

    #[error("Validation failed: {0}")]
    Validation(String),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("IO error: {0}")]
    Io(#[from] io::Error),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl AppError {
    pub fn status_code(&self) -> u16 {
        match self {
            AppError::NotFound { .. } => 404,
            AppError::Validation(_) => 422,
            AppError::Database(_) => 500,
            AppError::Io(_) => 500,
            AppError::Serialization(_) => 400,
            AppError::Internal(_) => 500,
        }
    }
}

fn read_config(path: &str) -> Result<Config, AppError> {
    let contents = fs::read_to_string(path)?;   // ? converts io::Error via From
    let config: Config = serde_json::from_str(&contents)?; // ? converts serde error
    Ok(config)
}
```

### Using anyhow for Application Code

```rust
use anyhow::{Context, Result};

fn process_file(path: &str) -> Result<()> {
    let contents = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {path}"))?;

    let data: serde_json::Value = serde_json::from_str(&contents)
        .with_context(|| format!("Invalid JSON in file: {path}"))?;

    process_data(&data)
        .context("Failed to process data")?;

    Ok(())
}
```

---

## React Error Boundaries

```tsx
import React, { Component, ErrorInfo, ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("Error Boundary caught:", error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div role="alert">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary
      fallback={<p>Dashboard failed to load.</p>}
      onError={(error) => monitor.captureException(error)}
    >
      <Dashboard />
    </ErrorBoundary>
  );
}
```

---

## Express / Koa Error Middleware

### Express Error Middleware

```typescript
import { Request, Response, NextFunction } from "express";

// Async handler wrapper - eliminates try/catch in every route
function asyncHandler(fn: (req: Request, res: Response, next: NextFunction) => Promise<void>) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// Route using asyncHandler
app.get("/api/users/:id", asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id);
  if (!user) {
    throw new NotFoundError("User", req.params.id);
  }
  res.json(user);
}));

// Centralized error handler (must have 4 parameters)
app.use((err: Error, req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof AppError && err.isOperational) {
    res.status(err.statusCode).json({
      type: `https://api.example.com/errors/${err.code}`,
      title: err.name,
      status: err.statusCode,
      detail: err.message,
      instance: req.originalUrl,
      ...(err.context ?? {}),
    });
  } else {
    // Programmer error - log full details, return generic message
    console.error("Unhandled error:", err);
    monitor.captureException(err);
    res.status(500).json({
      type: "https://api.example.com/errors/INTERNAL_ERROR",
      title: "Internal Server Error",
      status: 500,
      detail: "An unexpected error occurred",
      instance: req.originalUrl,
    });
  }
});
```

### Koa Error Middleware

```typescript
import Koa from "koa";

const app = new Koa();

// Error handling middleware (place first in chain)
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err: any) {
    if (err instanceof AppError && err.isOperational) {
      ctx.status = err.statusCode;
      ctx.body = {
        type: `https://api.example.com/errors/${err.code}`,
        title: err.name,
        status: err.statusCode,
        detail: err.message,
      };
    } else {
      console.error("Unhandled error:", err);
      ctx.status = 500;
      ctx.body = {
        type: "https://api.example.com/errors/INTERNAL_ERROR",
        title: "Internal Server Error",
        status: 500,
        detail: "An unexpected error occurred",
      };
    }
  }
});
```

---

## Error Serialization for APIs (RFC 7807)

### Problem Details (RFC 7807 / RFC 9457)

Standardized format for HTTP API error responses.

```typescript
interface ProblemDetail {
  type: string;      // URI reference identifying the error type
  title: string;     // Short human-readable summary
  status: number;    // HTTP status code
  detail?: string;   // Human-readable explanation specific to this occurrence
  instance?: string; // URI reference for the specific occurrence
  [key: string]: unknown; // Extension fields
}

// Example response: 422 Unprocessable Entity
// Content-Type: application/problem+json
{
  "type": "https://api.example.com/errors/VALIDATION_ERROR",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields",
  "instance": "/api/users",
  "errors": [
    { "field": "email", "message": "Must be a valid email address" },
    { "field": "age", "message": "Must be a positive integer" }
  ]
}

// Example response: 429 Too Many Requests
{
  "type": "https://api.example.com/errors/RATE_LIMIT_EXCEEDED",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per minute",
  "instance": "/api/search",
  "retryAfter": 32
}
```

---

## Error Codes and Error Catalogs

Define a centralized catalog of error codes so clients can programmatically handle errors.

```typescript
// error-catalog.ts
export const ErrorCatalog = {
  AUTH_001: {
    code: "AUTH_001",
    title: "Invalid Credentials",
    statusCode: 401,
    description: "The provided username or password is incorrect.",
  },
  AUTH_002: {
    code: "AUTH_002",
    title: "Token Expired",
    statusCode: 401,
    description: "The authentication token has expired. Please re-authenticate.",
  },
  AUTH_003: {
    code: "AUTH_003",
    title: "Insufficient Permissions",
    statusCode: 403,
    description: "You do not have permission to perform this action.",
  },
  RES_001: {
    code: "RES_001",
    title: "Resource Not Found",
    statusCode: 404,
    description: "The requested resource does not exist.",
  },
  VAL_001: {
    code: "VAL_001",
    title: "Validation Error",
    statusCode: 422,
    description: "One or more fields in the request are invalid.",
  },
  RATE_001: {
    code: "RATE_001",
    title: "Rate Limit Exceeded",
    statusCode: 429,
    description: "Too many requests. Please retry after the specified interval.",
  },
  SYS_001: {
    code: "SYS_001",
    title: "Service Unavailable",
    statusCode: 503,
    description: "The service is temporarily unavailable. Please try again later.",
  },
} as const;

type ErrorCode = keyof typeof ErrorCatalog;

function createError(code: ErrorCode, detail?: string): AppError {
  const entry = ErrorCatalog[code];
  return new AppError({
    message: detail ?? entry.description,
    code: entry.code,
    statusCode: entry.statusCode,
  });
}
```

---

## Retry Patterns

### Exponential Backoff with Jitter

```typescript
interface RetryOptions {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  jitter: boolean;
  retryableErrors?: (error: unknown) => boolean;
  onRetry?: (error: unknown, attempt: number, delayMs: number) => void;
}

const DEFAULT_OPTIONS: RetryOptions = {
  maxRetries: 3,
  baseDelayMs: 1000,
  maxDelayMs: 30_000,
  jitter: true,
};

async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: unknown;

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if error is retryable
      if (opts.retryableErrors && !opts.retryableErrors(error)) {
        throw error;
      }

      if (attempt === opts.maxRetries) {
        break; // No more retries
      }

      // Calculate delay: exponential backoff
      let delay = Math.min(
        opts.baseDelayMs * Math.pow(2, attempt),
        opts.maxDelayMs
      );

      // Add jitter to prevent thundering herd
      if (opts.jitter) {
        delay = delay * (0.5 + Math.random() * 0.5);
      }

      opts.onRetry?.(error, attempt + 1, delay);
      await sleep(delay);
    }
  }

  throw lastError;
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage
const data = await withRetry(
  () => fetchFromApi("/data"),
  {
    maxRetries: 5,
    baseDelayMs: 500,
    retryableErrors: (err) => err instanceof NetworkError || (err instanceof HttpError && err.status >= 500),
    onRetry: (err, attempt, delay) => {
      console.warn(`Retry attempt ${attempt} after ${delay}ms due to: ${err}`);
    },
  }
);
```

---

## Circuit Breaker Pattern

Prevent cascading failures by stopping calls to a failing service.

```typescript
enum CircuitState {
  CLOSED = "CLOSED",       // Normal operation
  OPEN = "OPEN",           // Failing - reject calls immediately
  HALF_OPEN = "HALF_OPEN", // Testing if service recovered
}

interface CircuitBreakerOptions {
  failureThreshold: number;   // Failures before opening
  resetTimeoutMs: number;     // Time before trying half-open
  successThreshold: number;   // Successes in half-open before closing
  monitorInterval?: number;   // Interval for metric reporting
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime = 0;

  constructor(
    private readonly name: string,
    private readonly options: CircuitBreakerOptions
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailureTime >= this.options.resetTimeoutMs) {
        this.state = CircuitState.HALF_OPEN;
        this.successCount = 0;
      } else {
        throw new CircuitBreakerOpenError(
          `Circuit breaker '${this.name}' is open. Service unavailable.`
        );
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.options.successThreshold) {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        console.log(`Circuit breaker '${this.name}' closed. Service recovered.`);
      }
    } else {
      this.failureCount = 0;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (this.failureCount >= this.options.failureThreshold) {
      this.state = CircuitState.OPEN;
      console.warn(`Circuit breaker '${this.name}' opened after ${this.failureCount} failures.`);
    }
  }

  getState(): CircuitState {
    return this.state;
  }
}

class CircuitBreakerOpenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CircuitBreakerOpenError";
  }
}

// Usage
const paymentCircuit = new CircuitBreaker("payment-service", {
  failureThreshold: 5,
  resetTimeoutMs: 30_000,
  successThreshold: 3,
});

async function processPayment(order: Order) {
  return paymentCircuit.execute(() => paymentApi.charge(order));
}
```

---

## Graceful Degradation and Fallbacks

```typescript
interface FallbackOptions<T> {
  primary: () => Promise<T>;
  fallback: () => Promise<T>;
  shouldFallback?: (error: unknown) => boolean;
  onFallback?: (error: unknown) => void;
}

async function withFallback<T>(options: FallbackOptions<T>): Promise<T> {
  try {
    return await options.primary();
  } catch (error) {
    if (options.shouldFallback && !options.shouldFallback(error)) {
      throw error;
    }
    options.onFallback?.(error);
    return options.fallback();
  }
}

// Usage: Feature recommendations with cache fallback
const recommendations = await withFallback({
  primary: () => mlService.getRecommendations(userId),
  fallback: () => cache.get(`recommendations:${userId}`) ?? getPopularItems(),
  shouldFallback: (err) => err instanceof NetworkError || err instanceof TimeoutError,
  onFallback: (err) => console.warn("ML service unavailable, using cached recommendations:", err),
});

// Usage: Multi-tier degradation
async function getProductPrice(productId: string): Promise<number> {
  try {
    // Tier 1: Real-time pricing service
    return await pricingService.getPrice(productId);
  } catch {
    try {
      // Tier 2: Cached price
      const cached = await cache.get(`price:${productId}`);
      if (cached) return cached;
    } catch {
      // Tier 3: Database fallback
    }
    const product = await db.products.findById(productId);
    if (!product) throw new NotFoundError("Product", productId);
    return product.basePrice;
  }
}
```

---

## Error Logging and Monitoring Integration

```typescript
import { Logger } from "./logger";
import { Monitor } from "./monitor";

interface ErrorReporter {
  report(error: unknown, context?: Record<string, unknown>): void;
}

class ErrorHandler implements ErrorReporter {
  constructor(
    private readonly logger: Logger,
    private readonly monitor: Monitor,
  ) {}

  report(error: unknown, context?: Record<string, unknown>): void {
    if (error instanceof AppError && error.isOperational) {
      // Operational errors: log as warnings, track metrics
      this.logger.warn("Operational error", {
        code: error.code,
        message: error.message,
        statusCode: error.statusCode,
        ...context,
      });
      this.monitor.incrementCounter("operational_errors", {
        code: error.code,
      });
    } else {
      // Programmer errors: log as errors, send to exception tracker
      this.logger.error("Unexpected error", {
        error: error instanceof Error ? error.stack : String(error),
        ...context,
      });
      this.monitor.captureException(error, context);
      this.monitor.incrementCounter("unexpected_errors");
    }
  }

  // Middleware factory for Express
  middleware() {
    return (err: Error, req: Request, res: Response, next: NextFunction) => {
      this.report(err, {
        method: req.method,
        path: req.path,
        query: req.query,
        userId: (req as any).userId,
        requestId: req.headers["x-request-id"],
      });

      if (err instanceof AppError) {
        res.status(err.statusCode).json(err.toJSON());
      } else {
        res.status(500).json({
          type: "https://api.example.com/errors/INTERNAL_ERROR",
          title: "Internal Server Error",
          status: 500,
          detail: "An unexpected error occurred",
        });
      }
    };
  }
}
```

---

## Summary of Best Practices

1. **Use typed, structured errors** - Create error hierarchies with codes, status codes, and context.
2. **Separate operational errors from programmer errors** - Handle them differently in monitoring and recovery.
3. **Always wrap lower-level errors** - Add context at each layer (what operation failed) while preserving the root cause.
4. **Use RFC 7807 Problem Details** for API error responses - Consistent, machine-readable format.
5. **Implement retries with exponential backoff and jitter** - Protect against transient failures and thundering herds.
6. **Use circuit breakers** for external service calls - Prevent cascading failures.
7. **Design fallback paths** - Graceful degradation is better than total failure.
8. **Centralize error handling** - Use middleware, global handlers, and a unified error reporter.
9. **Log structured data** - Include request IDs, user context, and error codes for debugging.
10. **Define an error catalog** - Enumerate all known error codes so clients can handle them programmatically.
11. **Fail fast at boundaries** - Validate early, throw early, catch at the appropriate level.
12. **Never swallow errors silently** - If you catch an exception, log it or re-throw it.
13. **Use language-idiomatic patterns** - Result types in Rust, error interface in Go, custom exceptions in Python/Java.
14. **Test error paths** - Write tests for failure scenarios, not just the happy path.
15. **Monitor error rates and set alerts** - Track operational error frequency and latency impact.
