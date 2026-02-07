# SSH Configuration Guide

## Key Generation

```bash
# Modern approach (recommended)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "email@example.com"

# Well-supported
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -C "email@example.com"

# List keys
ls -la ~/.ssh/
```

## SSH Config File

```bash
# ~/.ssh/config

# GitHub
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_key
    AddKeysToAgent yes
    UseKeychain yes

# Custom server
Host myserver
    HostName 192.168.1.100
    User deploy
    Port 2222
    IdentityFile ~/.ssh/myserver_key
    StrictHostKeyChecking accept-new

# Jump host
Host internal
    HostName internal.company.com
    User john
    ProxyJump bastion
    IdentityFile ~/.ssh/internal_key
```

## Usage

```bash
# Connect using config
ssh github.com
ssh myserver

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_rsa.pub user@host

# Test connection
ssh -T git@github.com

# List known hosts
cat ~/.ssh/known_hosts
```

## SSH Agent

```bash
# Start agent
eval $(ssh-agent -s)

# Add key
ssh-add ~/.ssh/id_rsa

# List keys
ssh-add -l

# Remove key
ssh-add -d ~/.ssh/id_rsa

# Remove all keys
ssh-add -D
```

## Troubleshooting

```bash
# Clear known_hosts for host
ssh-keygen -R hostname

# Verbose connection test
ssh -vvv user@host

# Check key permissions
ls -la ~/.ssh/
# -rw------- for private keys
# -rw-r--r-- for public keys
# drwx------ for ~/.ssh/
```

## Best Practices

1. **Use EdDSA keys** - Smaller, secure
2. **One key per device** - Easier revocation
3. **Use passphrases** - Protect private keys
4. **ssh-agent** - Avoid typing password
5. **Restrict access** - Limit key permissions
6. **Regular rotation** - Regenerate periodically
7. **Never share private key** - Only share .pub
