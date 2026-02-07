# Environment Variable Troubleshooting

## Common Issues

### "Command not found"

```bash
# Debug where command is
which node          # Shows path
type node           # Shows type (binary, alias, function)
command -v node     # Most portable

# Add to PATH
export PATH="/usr/local/bin:$PATH"

# Persist in ~/.bashrc or ~/.zshrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
```

### Conflicting Versions

```bash
# Find all versions
which -a node       # All matches
ls -la /usr/local/bin/node*

# Check symlink
readlink $(which node)

# Use version manager
nvm use 18
pyenv global 3.11
```

### Missing Environment Variables

```bash
# Check if set
echo $DATABASE_URL

# Set temporarily
export DATABASE_URL="postgres://localhost/mydb"

# Persist
echo 'export DATABASE_URL="postgres://localhost/mydb"' >> ~/.bashrc

# Load from .env file
set -a
source .env
set +a
```

## Debugging Script

```bash
#!/bin/bash

echo "=== Full Environment Debug ==="

echo "Executable locations:"
type node npm python git
echo ""

echo "Version information:"
node --version
npm --version
python --version
git --version
echo ""

echo "Path:"
echo $PATH
echo ""

echo "Environment variables:"
env | sort | head -20
```

## Performance Issues

### Slow Shell Startup

```bash
# Profile startup
time bash -i -c exit
time zsh -i -c exit

# Find slow operations
zsh -xvs 2>&1 | head -50
```

### Slow Commands

```bash
# Time specific command
time npm install

# Find bottleneck
time npm list --depth=0

# Check disk I/O
iotop
```

## Security

Don't expose:
- API keys in shell history
- Passwords in environment
- Credentials in scripts

```bash
# Use secrets manager
# Store in ~/.env (not committed)
# Load with: set -a; source ~/.env; set +a

# Or use direnv
echo 'export API_KEY=secret' > .envrc
direnv allow
```
