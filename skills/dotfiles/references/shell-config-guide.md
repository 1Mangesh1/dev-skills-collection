# Shell Configuration Best Practices

## Startup Files Order

### macOS Bash
- `/etc/profile` (system)
- `~/.profile` (user) - Run on login
- `~/.bashrc` - Run on every shell

### Zsh
- `~/.zshenv` - Always sourced
- `~/.zprofile` - Login shell
- `~/.zshrc` - Interactive shell ← Most customizations here
- `~/.zlogout` - Cleanup on exit

### Bash/Zsh Best Practices

```bash
# Don't put slow operations in .bashrc
# Use lazy loading:
alias python=/usr/bin/python3

# Load on first use:
npm() {
  unalias npm
  eval "$(command -v node)"
  npm "$@"
}

# Cache expensive operations:
if [ -f ~/.config/cached_env ]; then
  source ~/.config/cached_env
else
  # Generate once
  python generate_config.py > ~/.config/cached_env
  source ~/.config/cached_env
fi
```

## Fast Shell Startup

Profile startup time:
```bash
zsh -i -c exit  # Shows startup time
```

Optimize:
1. Remove unused plugins
2. Use lazy loading
3. Cache expensive operations
4. Use built-in features instead of commands

## Version Management Tools

```bash
# nvm (Node Version Manager)
source ~/.nvm/nvm.sh

# pyenv (Python Version Manager)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"

# rbenv (Ruby Version Manager)
eval "$(rbenv init - zsh)"
```
