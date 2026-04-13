---
name: ssh-config
description: SSH key management, config file setup, tunnels, port forwarding, and jump hosts. Use when user asks to "setup SSH keys", "configure SSH", "create SSH tunnel", "add SSH host", "jump host", "port forwarding", "bastion host", "SSH agent", "ssh-copy-id", "SSH proxy", "SSH hardening", "SSH multiplexing", "SSH certificates", "multiple GitHub keys", "ProxyJump", "SSH debug", "SSH escape", "SSH SOCKS proxy", "rsync over SSH", or manage SSH connections.
---

# SSH Config

SSH key management, configuration, tunneling, and security hardening.

## Key Generation

```bash
# Ed25519 (recommended — shorter, faster, more secure)
ssh-keygen -t ed25519 -C "your@email.com"
ssh-keygen -t ed25519 -f ~/.ssh/github_key -C "github"       # custom filename
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -C "deploy" -N "" # no passphrase

# RSA 4096 (for legacy systems that don't support Ed25519)
ssh-keygen -t rsa -b 4096 -C "your@email.com"

# Change passphrase on existing key
ssh-keygen -p -f ~/.ssh/id_ed25519

# Show fingerprint / update comment
ssh-keygen -lf ~/.ssh/id_ed25519.pub
ssh-keygen -c -f ~/.ssh/id_ed25519 -C "alice@work-laptop-2024"
```

## Copying Public Keys

```bash
# ssh-copy-id (simplest)
ssh-copy-id user@host
ssh-copy-id -i ~/.ssh/mykey.pub user@host
ssh-copy-id -p 2222 user@host

# Manual method (when ssh-copy-id isn't available)
cat ~/.ssh/id_ed25519.pub | ssh user@host 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

# Copy to clipboard (macOS) for GitHub/GitLab web UI
pbcopy < ~/.ssh/id_ed25519.pub
```

## SSH Agent

```bash
eval "$(ssh-agent -s)"                          # start agent
ssh-add ~/.ssh/id_ed25519                       # add key
ssh-add -t 43200 ~/.ssh/id_ed25519              # add with 12h timeout
ssh-add -l                                       # list loaded keys
ssh-add -d ~/.ssh/id_ed25519                    # remove specific key
ssh-add -D                                       # remove all keys
```

### macOS Keychain Integration

```ssh-config
Host *
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519
```

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519  # persist across reboots
```

### Agent Forwarding

```bash
ssh -A user@server       # forward local agent to remote host
```

```ssh-config
Host myserver
    ForwardAgent yes
```

Only forward agent to trusted hosts. A compromised host can use your agent to authenticate as you.

## SSH Config File (~/.ssh/config)

### Basic Host Entries

```ssh-config
Host myserver
    HostName 192.168.1.100
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host prod
    HostName prod.example.com
    User deploy
    IdentityFile ~/.ssh/deploy_key
    IdentitiesOnly yes
```

`IdentitiesOnly yes` prevents SSH from trying every key in the agent.

### Wildcards and Defaults

```ssh-config
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes

Host *.example.com
    User deploy
    IdentityFile ~/.ssh/deploy_key

Host 192.168.1.*
    User admin
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### Multiple GitHub/GitLab Accounts

```ssh-config
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_personal
    IdentitiesOnly yes

Host github.com-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_work
    IdentitiesOnly yes
```

```bash
git clone git@github.com-personal:myuser/repo.git
git clone git@github.com-work:company/repo.git
git remote set-url origin git@github.com-work:company/repo.git
```

## Jump Hosts / Bastion Hosts

### ProxyJump (OpenSSH 7.3+)

```ssh-config
Host bastion
    HostName bastion.example.com
    User jump

Host internal
    HostName 10.0.0.5
    User admin
    ProxyJump bastion

# Chain: bastion -> middleware -> deep-internal
Host middleware
    HostName 10.0.0.10
    User app
    ProxyJump bastion

Host deep-internal
    HostName 172.16.0.5
    User admin
    ProxyJump middleware
```

```bash
ssh -J jump@bastion.example.com admin@10.0.0.5            # command line
ssh -J jump@bastion1,jump@bastion2 admin@10.0.0.5         # chain multiple
```

### ProxyCommand (Legacy)

```ssh-config
Host internal-legacy
    HostName 10.0.0.5
    User admin
    ProxyCommand ssh -W %h:%p bastion
```

## Port Forwarding

### Local Forward (-L)

```bash
ssh -L 8080:localhost:80 user@server                       # local:8080 -> remote:80
ssh -L 5432:localhost:5432 user@server                     # remote PostgreSQL
ssh -L 8080:internal-db.example.com:5432 user@bastion      # through bastion to third host
ssh -L 0.0.0.0:8080:localhost:80 user@server               # bind all interfaces
```

### Remote Forward (-R)

```bash
ssh -R 8080:localhost:3000 user@server     # expose local:3000 on remote:8080
```

### Dynamic Forward / SOCKS Proxy (-D)

```bash
ssh -D 1080 user@server                   # SOCKS5 proxy on localhost:1080
ssh -D 1080 -f -N user@server             # background SOCKS proxy
```

### Port Forwarding in Config

```ssh-config
Host tunnel-db
    HostName server.example.com
    User admin
    LocalForward 5432 localhost:5432
    LocalForward 6379 localhost:6379

Host tunnel-web
    HostName server.example.com
    User admin
    LocalForward 8080 localhost:80
    DynamicForward 1080
```

## SSH Tunnels

```bash
# Background tunnel (-f: background, -N: no remote command)
ssh -f -N -L 8080:localhost:80 user@server
pkill -f "ssh -f -N -L 8080"              # kill it

# Persistent tunnel with autossh (auto-reconnects on drop)
autossh -M 0 -f -N -L 8080:localhost:80 user@server   # brew/apt install autossh

# Database access through bastion
ssh -f -N -L 5432:db.internal:5432 user@bastion && psql -h localhost -p 5432 -U dbuser mydb
ssh -f -N -L 6379:redis.internal:6379 user@bastion && redis-cli -h localhost
```

## SCP and rsync Over SSH

```bash
# SCP
scp file.txt user@host:/path/                              # upload
scp user@host:/path/file.txt ./                             # download
scp -r folder/ user@host:/path/                             # recursive

# rsync (preferred — delta transfer, resume, compression)
rsync -avz folder/ user@host:/path/
rsync -avz --progress folder/ user@host:/path/              # with progress
rsync -avz --delete folder/ user@host:/path/                # mirror (delete extra)
rsync -avzn folder/ user@host:/path/                        # dry run
rsync -avz -e "ssh -J jump@bastion" folder/ admin@internal:/path/  # via jump host
```

## Multiplexing (Connection Reuse)

```ssh-config
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

```bash
mkdir -p ~/.ssh/sockets     # create socket directory

# First ssh opens master socket; subsequent connections reuse it (instant, no re-auth)
ssh -O check myserver       # check master status
ssh -O exit myserver        # close master connection
```

`ControlPersist 600` keeps the socket alive 600s after the last session closes.

## SSH Escape Sequences

Press Enter then `~` during an SSH session:

```
~.      Disconnect (kill hung session)    ~?      List all escapes
~C      Open command line (add -L/-R/-D mid-session)
~#      List forwarded connections        ~~      Send literal ~
```

## Debugging Connection Issues

```bash
ssh -v user@host                        # basic debug
ssh -vvv user@host                      # maximum verbosity
ssh -T git@github.com                   # test GitHub connection
ssh -G myserver | grep -i hostname      # show resolved config

# Remove stale host key after server reinstall
ssh-keygen -R hostname
ssh-keygen -R "[hostname]:port"
```

Common errors:
- "Permission denied (publickey)" -- wrong key, key not in agent, or not in authorized_keys
- "Host key verification failed" -- host key changed (server reinstall or MITM)
- "Connection refused" -- sshd not running or wrong port
- "Connection timed out" -- firewall, wrong IP, or host down

## SSH Security Hardening

### File Permissions

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519 ~/.ssh/config ~/.ssh/authorized_keys
chmod 644 ~/.ssh/id_ed25519.pub
```

### Server Configuration (/etc/ssh/sshd_config)

```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
Port 2222
AllowUsers deploy admin
PermitEmptyPasswords no
MaxAuthTries 3
X11Forwarding no
AllowAgentForwarding no
```

```bash
sudo sshd -t                            # validate config
sudo systemctl restart sshd
```

### fail2ban (Brute-Force Protection)

```bash
sudo apt install fail2ban
# /etc/fail2ban/jail.local: [sshd] enabled=true, maxretry=3, bantime=3600, findtime=600
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd        # check banned IPs
```

## SSH Certificates vs Keys

```bash
ssh-keygen -t ed25519 -f ca_key -C "SSH CA"                              # create CA
ssh-keygen -s ca_key -I "alice-cert" -n alice -V +52w id_ed25519.pub     # sign user key
ssh-keygen -s ca_key -I "web-server" -h -n web.example.com host_key.pub  # sign host key
ssh-keygen -Lf id_ed25519-cert.pub                                        # view cert details
```

Server trusts CA: add `TrustedUserCAKeys /etc/ssh/ca_key.pub` to sshd_config.
Client trusts host CA: add `@cert-authority *.example.com <ca_key.pub contents>` to known_hosts.

Certificates eliminate distributing `authorized_keys` to every server -- sign once, access everywhere the CA is trusted.
