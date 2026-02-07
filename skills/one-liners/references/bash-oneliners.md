# Bash One-liners for Development

## File & Text Processing

```bash
# Count lines of code (excluding comments/blanks)
find . -name "*.js" -exec grep -v '^[[:space:]]*$' {} + | wc -l

# Remove trailing whitespace from all files
find . -name "*.js" -exec sed -i 's/[[:space:]]*$//' {} +

# Find large files
find . -type f -size +100M -exec ls -lh {} +

# Backup directory with timestamp
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz directory/

# Recursive grep with line numbers
grep -rn "search_term" . 

# Replace across multiple files
find . -name "*.js" -exec sed -i 's/old/new/g' {} +
```

## Git One-liners

```bash
# Show git log with graph
git log --all --graph --decorate --oneline

# Clean up merged branches
git branch --merged | grep -v main | xargs git branch -d

# Find when a line was changed
git log -p -S "search_text" -- file.js

# Create patch from last N commits
git format-patch -N

# Squash last N commits
git rebase -i HEAD~N
```

## Network & System

```bash
# Find process using port
lsof -i :8080 | grep LISTEN

# Test connectivity
curl -o /dev/null -w "@curl-format.txt" https://example.com

# Monitor network traffic
watch -n 1 'netstat -i'

# Check DNS
nslookup example.com | grep Address

# Monitor file changes
watch -n 1 'ls -la directory'
```

## Docker One-liners

```bash
# List running containers with size
docker ps -s

# Remove stopped containers
docker container prune -f

# View container logs
docker logs -f container_name --tail 100

# Execute command in container
docker exec -it container_name bash

# Copy file from container
docker cp container_name:/path/to/file .

# Build and tag image
docker build -t myapp:latest .
```

## Performance

```bash
# Time command execution
time npm run build

# Profile with strace
strace -c node app.js

# Monitor disk I/O
iostat -x 1 5

# Check memory usage
free -h

# Watch system load
uptime
```
