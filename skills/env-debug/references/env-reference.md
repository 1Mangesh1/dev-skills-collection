# System Environment Info

## Key Environment Variables

```bash
HOME        # User home directory
USER        # Current user
PATH        # Executable search path
SHELL       # Current shell
PWD         # Current directory
TMPDIR      # Temporary directory
EDITOR      # Default editor
PAGER       # Default pager (less, more)
```

## Language-Specific

```bash
NODE_PATH       # Node.js module search
PYTHONPATH      # Python module search
GOPATH          # Go workspace
RUBYLIB         # Ruby load path
```

## Application-Specific

```bash
NODE_ENV        # Development, production, test
DEBUG           # Debug output level
LOG_LEVEL       # Logging level
DATABASE_URL    # Database connection
API_KEY         # API authentication
```

## How to Check

```bash
# Show specific variable
echo $PATH
echo $HOME

# Show all variables
env

# Show just exported ones
printenv

# Search for pattern
env | grep NODE
```

## Security Caution

```bash
# ❌ Don't do this in shell
export API_KEY=secret123

# ✓ Better options
# 1. .env file (not committed)
# 2. System keychain (macOS: security, Linux: pass)
# 3. Environment secrets in CI/CD
# 4. Docker secrets or Kubernetes secrets
```
