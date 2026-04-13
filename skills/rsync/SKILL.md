---
name: rsync
description: File synchronization, backup, and deployment with rsync. Use when user mentions "rsync", "sync files", "mirror directory", "incremental backup", "copy files to server", "deploy files", "remote sync", "backup to external drive", "exclude patterns", "dry run sync", "bandwidth limit transfer", or transferring files between local and remote systems efficiently.
---

# rsync Reference

## Core Syntax

```bash
rsync [options] source destination

# Local to local
rsync -av /src/dir/ /dest/dir/

# Local to remote (push)
rsync -avz /local/dir/ user@host:/remote/dir/

# Remote to local (pull)
rsync -avz user@host:/remote/dir/ /local/dir/
```

**Trailing slash matters:** `/src/dir/` copies the *contents* of dir. `/src/dir` copies the directory itself into the destination.

## Common Flags

```bash
-a, --archive        # recursive + preserve permissions, times, symlinks, group, owner, devices
-v, --verbose        # increase verbosity
-z, --compress       # compress during transfer
-n, --dry-run        # show what would be transferred without doing it
-P                   # same as --partial --progress
--progress           # show per-file transfer progress
-h, --human-readable # human-readable sizes in output
-r, --recursive      # recurse into directories (included in -a)
-u, --update         # skip files that are newer on the destination
-c, --checksum       # use checksum instead of mod-time/size to detect changes
--stats              # show file transfer statistics at end
-q, --quiet          # suppress non-error messages
```

## Local Sync Patterns

```bash
# Mirror a directory (exact copy, delete extras on dest)
rsync -av --delete /src/ /dest/

# Incremental copy (only new/changed files)
rsync -av /src/ /dest/

# Copy only specific file types
rsync -av --include='*.jpg' --include='*/' --exclude='*' /src/ /dest/

# Sync and show progress
rsync -avh --progress /src/ /dest/

# Flatten: skip directory structure
rsync -av --no-relative /src/deep/path/file.txt /dest/
```

## Remote Sync over SSH

```bash
# Push to remote
rsync -avz /local/project/ user@server:/var/www/project/

# Pull from remote
rsync -avz user@server:/var/log/app/ /local/logs/

# Specify SSH port
rsync -avz -e "ssh -p 2222" /local/ user@server:/remote/

# Use specific SSH key
rsync -avz -e "ssh -i ~/.ssh/deploy_key" /local/ user@server:/remote/

# Limit SSH cipher for speed on trusted networks
rsync -avz -e "ssh -c aes128-ctr" /local/ user@server:/remote/

# Compress only during transfer (useful for already-compressed files)
rsync -av --compress-level=0 /local/media/ user@server:/remote/media/
```

## Exclude and Include Patterns

```bash
# Exclude single or multiple patterns
rsync -av --exclude='*.log' /src/ /dest/
rsync -av --exclude='*.log' --exclude='.git' --exclude='node_modules' /src/ /dest/

# Exclude from file
rsync -av --exclude-from='exclude-list.txt' /src/ /dest/

# Include only certain files, exclude everything else
rsync -av --include='*.py' --include='*/' --exclude='*' /src/ /dest/

# Filter rules (+ include, - exclude, H hide, P protect)
rsync -av --filter='- *.log' --filter='- .git/' /src/ /dest/

# .rsync-filter file (place in any directory, rules apply to that subtree)
# Contents: - *.pyc / - __pycache__/ / - .env
rsync -av --filter='dir-merge .rsync-filter' /src/ /dest/
```

## Delete Modes

```bash
# Delete files on dest that don't exist on source (mirror)
rsync -av --delete /src/ /dest/

# Delete after transfer (safer - transfer completes first)
rsync -av --delete-after /src/ /dest/

# Delete before transfer (frees space first)
rsync -av --delete-before /src/ /dest/

# Delete excluded files from destination
rsync -av --delete-excluded --exclude='*.tmp' /src/ /dest/

# Delete during transfer (default with --delete on newer rsync)
rsync -av --delete-during /src/ /dest/

# Protect certain files on dest from deletion
rsync -av --delete --filter='P *.local' /src/ /dest/
```

## Bandwidth Limiting

```bash
# Limit to 1 MB/s
rsync -avz --bwlimit=1000 /src/ user@server:/dest/

# Limit to 500 KB/s
rsync -avz --bwlimit=500 /src/ user@server:/dest/

# Limit to 5 MB/s (rsync 3.2.3+ supports suffixes)
rsync -avz --bwlimit=5m /src/ user@server:/dest/
```

## Partial Transfers and Resume

```bash
# Keep partially transferred files (resume on restart)
rsync -av --partial /src/ /dest/

# Store partial files in a hidden directory (keeps dest clean)
rsync -av --partial-dir=.rsync-partial /src/ /dest/

# -P combines --partial and --progress
rsync -avP /src/ user@server:/dest/

# Append to partially transferred files (no checksum verification)
rsync -av --append /src/ /dest/

# Append with checksum verification
rsync -av --append-verify /src/ /dest/
```

## Backup Patterns

```bash
# Create backups of overwritten files
rsync -av --backup --backup-dir=/backups/$(date +%Y%m%d) /src/ /dest/

# Backup with suffix instead of directory
rsync -av --backup --suffix=".bak" /src/ /dest/

# Rotating daily backups using hard links (space-efficient)
rsync -av --delete --link-dest=/backups/latest /src/ /backups/$(date +%Y%m%d)/
ln -nsf /backups/$(date +%Y%m%d) /backups/latest

# Full backup script with rotation
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LATEST="$BACKUP_DIR/latest"
NEW="$BACKUP_DIR/$DATE"

rsync -av --delete \
  ${LATEST:+--link-dest="$LATEST"} \
  /data/ "$NEW/"

rm -f "$LATEST"
ln -s "$NEW" "$LATEST"

# Keep only last 7 backups
ls -dt "$BACKUP_DIR"/2* | tail -n +8 | xargs rm -rf

# Backup to external drive
rsync -av --delete --exclude='.Trash' /home/user/ /media/external/backup/
```

## Deployment Workflows

```bash
# Deploy website (mirror with delete, exclude deploy artifacts)
rsync -avz --delete \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='node_modules' \
  --exclude='.DS_Store' \
  /local/site/build/ user@web:/var/www/html/

# Deploy with dry run first
rsync -avzn --delete /local/site/build/ user@web:/var/www/html/
# Review output, then run without -n

# Deploy to multiple servers
for server in web1 web2 web3; do
  rsync -avz --delete /local/build/ deploy@$server:/var/www/html/ &
done
wait

# Deploy with pre/post hooks
rsync -avz --delete /local/build/ user@web:/var/www/html/ \
  --rsync-path="sudo rsync" \
  && ssh user@web "sudo systemctl reload nginx"

# Atomic deployment with symlink swap
rsync -avz /local/build/ user@web:/releases/$(date +%s)/
ssh user@web "ln -nsf /releases/$(date +%s) /var/www/current && sudo systemctl reload nginx"
```

## Preserving File Attributes

```bash
# Preserve everything (archive mode)
rsync -a /src/ /dest/

# Preserve specific attributes
rsync -rlptgoD /src/ /dest/
# -r recursive  -l symlinks  -p permissions  -t timestamps
# -g group  -o owner  -D devices+specials

# Preserve hard links (slower, more memory)
rsync -avH /src/ /dest/

# Preserve ACLs and extended attributes
rsync -avAX /src/ /dest/

# Don't preserve owner/group (when running as non-root)
rsync -av --no-owner --no-group /src/ /dest/

# Preserve only timestamps and permissions (skip owner/group)
rsync -rltpv /src/ /dest/
```

## Dry Run and Verbose Output

```bash
# Dry run (preview changes)
rsync -avn /src/ /dest/

# Dry run with itemized changes
rsync -avn --itemize-changes /src/ /dest/
# Output format: YXcstpoguax
# Y: < sent, > received, c local change, h hard link
# X: f file, d directory, L symlink
# c checksum differs, s size differs, t time differs
# p permissions, o owner, g group, u (reserved)
# a ACL, x xattr

# Example output interpretation:
# >f.st...... file.txt     # file will be sent, size+time differ
# >f+++++++++ newfile.txt  # new file will be created
# *deleting   old.txt      # file will be deleted
# .d..t...... subdir/      # directory timestamp will be updated

# Verbose with stats
rsync -av --stats /src/ /dest/
```

## Common Recipes

```bash
# Website deploy from CI/CD
rsync -avz --delete \
  -e "ssh -i /ci/deploy_key -o StrictHostKeyChecking=no" \
  --exclude='.git' --exclude='.env' \
  ./dist/ deploy@prod:/var/www/app/

# Database dump sync
mysqldump -u root mydb | gzip > /tmp/mydb.sql.gz
rsync -avz /tmp/mydb.sql.gz user@backup:/backups/db/mydb_$(date +%Y%m%d).sql.gz

# Dotfiles sync across machines
rsync -av --delete \
  --include='.bashrc' --include='.vimrc' --include='.gitconfig' \
  --include='.config/***' --include='.ssh/config' \
  --exclude='*' \
  ~/ user@other:~/

# Photo library mirror to NAS
rsync -avz --delete --progress \
  --exclude='.DS_Store' --exclude='Thumbs.db' \
  ~/Photos/ nas:/volume1/photos/

# Sync project without build artifacts
rsync -av --delete \
  --exclude='node_modules' --exclude='dist' --exclude='.next' \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
  /project/ /backup/project/

# Two-way sync approximation (use unison for true two-way)
# Sync newer files in both directions without deleting
rsync -avu /dir_a/ /dir_b/
rsync -avu /dir_b/ /dir_a/

# Large file transfer with resume
rsync -avP --bwlimit=2000 /local/large.iso user@server:/remote/
```

## rsync Daemon Mode

```bash
# /etc/rsyncd.conf
# [share]
#   path = /data/shared
#   read only = no
#   auth users = syncuser
#   secrets file = /etc/rsyncd.secrets
#   hosts allow = 192.168.1.0/24

# Start daemon
rsync --daemon --config=/etc/rsyncd.conf

# Connect to daemon (double colon, no SSH)
rsync -av rsync://syncuser@server/share/ /local/copy/
rsync -av server::share/ /local/copy/

# List available modules
rsync rsync://server/
```

## Comparison with Other Tools

| Feature              | rsync          | scp            | sftp           | rclone         |
|----------------------|----------------|----------------|----------------|----------------|
| Incremental transfer | Yes            | No             | No             | Yes            |
| Resume partial       | Yes            | No             | Yes            | Yes            |
| Compression          | Yes            | Yes            | No             | Yes            |
| Delete remote extras | Yes            | No             | Manual         | Yes            |
| Cloud storage        | No             | No             | No             | Yes            |
| Bandwidth limit      | Yes            | Yes (OpenSSH 9)| No             | Yes            |
| Preserve permissions | Yes            | Yes            | Yes            | Limited        |
| Filter/exclude       | Yes            | No             | No             | Yes            |

Use `rclone` for cloud storage (S3, GCS, Dropbox). Use `rsync` for server-to-server and local sync.

## Cron + rsync for Automated Backups

```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * rsync -a --delete /data/ /backups/daily/ >> /var/log/rsync-backup.log 2>&1

# Hourly incremental with link-dest
0 * * * * /usr/local/bin/rsync-hourly.sh

# rsync-hourly.sh
#!/bin/bash
set -euo pipefail
SRC="/data/"
BASE="/backups"
STAMP=$(date +\%Y\%m\%d_\%H\%M)
LATEST="$BASE/latest"
NEW="$BASE/$STAMP"

rsync -a --delete --link-dest="$LATEST" "$SRC" "$NEW/" 2>> /var/log/rsync.log
rm -f "$LATEST"
ln -s "$NEW" "$LATEST"

# With email notification on failure
0 3 * * * rsync -a --delete /data/ /backups/nightly/ 2>&1 || echo "Backup failed" | mail -s "rsync failure" admin@example.com

# Lock file to prevent overlapping runs
#!/bin/bash
LOCKFILE="/tmp/rsync-backup.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Already running"; exit 1; }

rsync -a --delete /data/ /backups/daily/
```

## Troubleshooting

```bash
# Permission denied
# - Check SSH key permissions: chmod 600 ~/.ssh/id_rsa
# - Check dest directory ownership/permissions
# - Use --no-owner --no-group when syncing to non-root dest
# - Use --rsync-path="sudo rsync" for root-owned destinations
rsync -av --rsync-path="sudo rsync" /src/ user@server:/root-owned/

# Slow transfers
# - Disable compression for already-compressed files (images, video, archives)
rsync -av --compress-level=0 /media/ user@server:/media/
# - Use faster SSH cipher
rsync -av -e "ssh -c aes128-ctr -o Compression=no" /src/ user@server:/dest/
# - Increase I/O buffer
rsync -av --sockopts=SO_SNDBUF=65536,SO_RCVBUF=65536 /src/ /dest/

# Checksum verification (when timestamps are unreliable)
rsync -avc /src/ /dest/

# Debug connection issues
rsync -avvv -e "ssh -v" /src/ user@server:/dest/

# "max delete" safety net (abort if too many deletions)
rsync -av --delete --max-delete=100 /src/ /dest/

# Handle spaces in filenames
rsync -av -e ssh "/path/with spaces/" "user@server:/path/with spaces/"

# Timeout for stalled transfers
rsync -av --timeout=300 --contimeout=30 /src/ user@server:/dest/

# Exclude .git but include everything else, verify with dry run
rsync -avn --exclude='.git' /project/ user@server:/deploy/
```
