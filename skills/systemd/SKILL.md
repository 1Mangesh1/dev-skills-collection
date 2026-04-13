---
name: systemd
description: Systemd service management, unit files, timers, and journal logging on Linux. Use when user mentions "systemd", "systemctl", "service file", "unit file", "journalctl", "system service", "daemon", "auto-start on boot", "timer", "systemd timer", "service restart", "enable service", "journald", "system logs", or managing Linux services and daemons.
---

# Systemd

## systemctl Commands

```bash
sudo systemctl start myapp
sudo systemctl stop myapp
sudo systemctl restart myapp
sudo systemctl reload myapp            # Reload config without full restart
sudo systemctl enable myapp            # Auto-start on boot
sudo systemctl enable --now myapp      # Enable and start immediately
sudo systemctl disable myapp

systemctl status myapp
systemctl is-active myapp
systemctl is-enabled myapp
systemctl show myapp -p MainPID,MemoryCurrent

sudo systemctl daemon-reload           # Reload unit files after editing

systemctl list-units --type=service --state=failed
systemctl list-unit-files --type=service
systemctl list-timers
```

## Writing Unit Files

Place system services in `/etc/systemd/system/myapp.service`.

```ini
[Unit]
Description=My Application Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=appuser
Group=appgroup
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/bin/server
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
```

After creating or editing: `sudo systemctl daemon-reload && sudo systemctl enable --now myapp`

## Service Types

| Type      | Behavior                                                   | Use Case                     |
|-----------|------------------------------------------------------------|------------------------------|
| simple    | Default. ExecStart process is the main process             | Most long-running services   |
| forking   | Process forks; parent exits. Set PIDFile                   | Traditional daemons          |
| oneshot   | Runs and exits. Service is "active" after completion       | Setup scripts, migrations    |
| notify    | Like simple, but sends sd_notify when ready                | systemd-aware apps           |
| idle      | Like simple, but waits until other jobs finish             | Low-priority startup tasks   |

```ini
# Forking example
[Service]
Type=forking
PIDFile=/run/myapp/myapp.pid
ExecStart=/opt/myapp/bin/server --daemonize

# Oneshot example
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/setup-iptables.sh
```

## Environment Variables

```ini
[Service]
Environment=NODE_ENV=production
Environment=PORT=3000 HOST=0.0.0.0
EnvironmentFile=/etc/myapp/env
EnvironmentFile=-/etc/myapp/env.local   # Dash prefix: no error if missing
```

Environment file (`/etc/myapp/env`): one `VAR=VALUE` per line.

## Restart Policies

```ini
[Service]
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=300    # Rate-limit window
StartLimitBurst=5            # Max restarts within window
```

| Policy       | Clean exit | Unclean signal | Timeout | Watchdog |
|--------------|------------|----------------|---------|----------|
| no           | -          | -              | -       | -        |
| on-failure   | -          | Yes            | Yes     | Yes      |
| on-abnormal  | -          | Yes            | Yes     | Yes      |
| always       | Yes        | Yes            | Yes     | Yes      |

Reset a failed unit: `sudo systemctl reset-failed myapp`

## Resource Limits

```ini
[Service]
MemoryMax=512M
MemoryHigh=400M              # Throttle before hard limit
CPUQuota=200%                # 2 full cores max
CPUWeight=50                 # Relative weight (default 100)
LimitNOFILE=65536
LimitNPROC=4096
```

## Dependency Management

```ini
[Unit]
# Ordering only (does NOT pull in the dependency)
After=network.target redis.service
Before=nginx.service

# Pull in dependencies
Requires=postgresql.service       # Hard: if postgres fails, this fails too
Wants=redis.service               # Soft: continues even if redis fails
BindsTo=docker.service            # Like Requires + stop when docker stops

# For services needing actual network connectivity
After=network-online.target
Wants=network-online.target
```

## User Services

Place units in `~/.config/systemd/user/`. No root required.

```ini
# ~/.config/systemd/user/myapp.service
[Unit]
Description=My User Application

[Service]
Type=simple
ExecStart=%h/bin/myapp
Restart=on-failure
Environment=PORT=8080

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now myapp
journalctl --user -u myapp -f
sudo loginctl enable-linger $USER    # Run without active login session
```

`%h` expands to the user's home directory.

## Timers (Cron Replacement)

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily backup timer

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true                  # Run missed executions after downtime
RandomizedDelaySec=900

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Backup job

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

Monotonic timers (relative to boot):

```ini
[Timer]
OnBootSec=5min
OnUnitActiveSec=1h              # Repeat every hour after last run
```

OnCalendar examples:

```
hourly | daily | weekly
Mon,Fri *-*-* 09:00:00          # Mon and Fri at 9 AM
*-*-01 00:00:00                 # First of every month
*-*-* *:00/15:00                # Every 15 minutes
```

Validate: `systemd-analyze calendar "Mon,Fri *-*-* 09:00:00"`

## journalctl Log Querying

```bash
journalctl -u myapp -f                                  # Follow
journalctl -u myapp -n 100                              # Last 100 lines
journalctl -u myapp --since "1 hour ago"                # Time filter
journalctl -u myapp --since "2024-01-15" --until "2024-01-16"
journalctl -u myapp -p err                              # Priority filter
journalctl -u myapp -b                                  # Current boot only
journalctl -u myapp -o json-pretty -n 10                # JSON output
journalctl -u myapp -o json --no-pager | jq '.MESSAGE'
journalctl -k                                           # Kernel messages
journalctl --disk-usage
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=7d
```

## Socket Activation

Start services on-demand when a connection arrives.

```ini
# /etc/systemd/system/myapp.socket
[Unit]
Description=My App Socket

[Socket]
ListenStream=8080
Accept=no

[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My App
Requires=myapp.socket

[Service]
Type=simple
ExecStart=/opt/myapp/bin/server
```

The service receives the socket as fd 3 (`SD_LISTEN_FDS_START`). Enable the socket, not the service: `sudo systemctl enable --now myapp.socket`

## Templated Units

Template files use `@` in the name. Instance name is `%i`.

```ini
# /etc/systemd/system/myapp@.service
[Unit]
Description=My App instance %i
After=network.target

[Service]
Type=simple
User=appuser
ExecStart=/opt/myapp/bin/server --port %i
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now myapp@8080
sudo systemctl enable --now myapp@8081
```

## Common Service Patterns

### Node.js

```ini
[Service]
Type=simple
User=nodeapp
WorkingDirectory=/opt/nodeapp
ExecStart=/usr/bin/node server.js
EnvironmentFile=/etc/nodeapp/env
Environment=NODE_ENV=production
LimitNOFILE=65536
Restart=on-failure
RestartSec=5
```

### Python (uvicorn with venv)

```ini
[Service]
Type=simple
User=pyapp
WorkingDirectory=/opt/pyapp
ExecStart=/opt/pyapp/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
EnvironmentFile=/etc/pyapp/env
Restart=on-failure
```

### Go Binary

```ini
[Service]
Type=simple
User=goapp
ExecStart=/usr/local/bin/goservice
EnvironmentFile=/etc/goservice/env
Restart=on-failure
LimitNOFILE=65536
```

### Docker Container

```ini
[Unit]
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStartPre=-/usr/bin/docker stop mycontainer
ExecStartPre=-/usr/bin/docker rm mycontainer
ExecStart=/usr/bin/docker run --rm --name mycontainer -p 8080:80 myimage:latest
ExecStop=/usr/bin/docker stop mycontainer
```

`-` prefix on ExecStartPre: don't fail if the command fails (container may not exist).

All patterns need `[Unit]` with `After=network.target` and `[Install]` with `WantedBy=multi-user.target`.

## Debugging Failed Services

```bash
systemctl status myapp
journalctl -xeu myapp                             # Logs with explanations
journalctl -u myapp -b --no-pager                 # Full boot log
systemd-analyze blame                              # Time per unit at boot
systemd-analyze critical-chain myapp               # Dependency chain timing
systemd-analyze verify myapp.service               # Validate unit file syntax
systemd-analyze security myapp                     # Security audit score
systemctl show myapp -p ExecMainStatus,Result,ActiveState
```

Common exit codes:
- 200: bad unit file syntax (check ExecStart path, missing `=`)
- 203: exec format error (missing shebang, wrong architecture)
- 217: user/group doesn't exist

## Security Hardening

```ini
[Service]
ProtectSystem=strict              # Mount / read-only
ProtectHome=true                  # Hide /home, /root, /run/user
ReadWritePaths=/var/lib/myapp     # Whitelist writable paths
PrivateTmp=true                   # Isolated /tmp
NoNewPrivileges=true              # Block privilege escalation
PrivateDevices=true               # No physical device access
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
SystemCallFilter=@system-service
SystemCallArchitectures=native

# Dynamic user (ephemeral UID, ideal for stateless services)
DynamicUser=true
StateDirectory=myapp              # Auto-creates /var/lib/myapp
CacheDirectory=myapp              # Auto-creates /var/cache/myapp
LogsDirectory=myapp               # Auto-creates /var/log/myapp

# Allow binding ports < 1024 without root
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

Audit: `systemd-analyze security myapp` (0 = most secure, 10 = least).

## Path Units (File Watching)

```ini
# /etc/systemd/system/deploy-watcher.path
[Unit]
Description=Watch for deployment triggers

[Path]
PathChanged=/var/deploy/trigger       # Trigger on write + close
PathExists=/var/deploy/run-now        # Trigger when file appears
PathModified=/var/deploy/config       # Trigger on any write
Unit=deploy.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/deploy.service
[Service]
Type=oneshot
ExecStart=/usr/local/bin/deploy.sh
```

```bash
sudo systemctl enable --now deploy-watcher.path
```

## Quick Reference: Unit File Specifiers

| Specifier | Meaning                        |
|-----------|--------------------------------|
| `%i`      | Instance name (template units) |
| `%I`      | Unescaped instance name        |
| `%n`      | Full unit name                 |
| `%h`      | User home directory            |
| `%t`      | Runtime directory (/run)       |
| `%S`      | State directory (/var/lib)     |
| `%C`      | Cache directory (/var/cache)   |
