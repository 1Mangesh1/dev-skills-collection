# Advanced One-liners

## Data Processing

```bash
# Convert JSON to CSV with headers
jq -r '(.[0] | keys) as $headers | [$headers], (.[] | [$headers[] as $h | .[$h]]) | @csv' data.json

# SQL to CSV
mysql -h localhost -u user -p database \
  -e "SELECT * FROM table" | sed 's/\t/,/g' > output.csv

# Parse Apache logs
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# Real-time log monitoring
tail -f log.txt | grep "ERROR"
```

## System Administration

```bash
# Find and delete old files
find /tmp -type f -mtime +30 -delete

# Find unused packages
apt list --installed | cut -d/ -f1 | sort > installed.txt && ... compare

# Monitor resource usage
while true; do clear; free -h; top -b -n 1 | head -15; sleep 1; done

# Batch rename files
for f in *.jpg; do mv "$f" "${f%jpg}png"; done

# Create directory tree from list
awk '{print "mkdir -p $(dirname "$0")"}' filelist.txt | bash
```

## Development Workflows

```bash
# Build matrix (test multiple node versions)
for node in 14 16 18 20; do nvm use $node && npm test || exit 1; done

# Find code complexity
find . -name "*.js" -exec wc -l {} + | sort -rn | head -20

# Generate dependency graph
npm ls --all --depth 0 > deps.txt

# Auto-format on file save
while true; do inotifywait -r . && prettier --write .; done

# Run tests on file change
while true; do inotifywait -r src && npm test; done
```
