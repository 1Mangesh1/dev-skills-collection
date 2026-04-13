---
name: shell-scripting
description: This skill should be used when the user asks to "write a bash script", "create a shell script", "parse command line args", "write a deploy script", "automate with bash", "process files with bash", "create an install script", "write a backup script", "handle signals in bash", "parse CSV in bash", or mentions shell scripting, bash scripting, POSIX shell, script automation, bash best practices, or shell utilities.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - bash
    - shell
    - scripting
    - automation
    - posix
    - cli
---

# Shell Scripting & Bash Best Practices

Comprehensive guide to writing robust, portable, and maintainable shell scripts. Covers Bash idioms, POSIX compliance, error handling, security, and real-world patterns.

## Bash Script Template

Every script should start with a solid foundation.

```bash
#!/usr/bin/env bash
#
# script-name.sh - Brief description of what the script does
#
# Usage: script-name.sh [OPTIONS] <arguments>
#
# Author: Your Name
# Date:   2024-01-01

set -euo pipefail
IFS=$'\n\t'

# --- Constants ----------------------------------------------------------------
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly VERSION="1.0.0"

# --- Cleanup Trap -------------------------------------------------------------
cleanup() {
    local exit_code=$?
    # Remove temp files, release locks, etc.
    if [[ -n "${TMPDIR_CUSTOM:-}" && -d "$TMPDIR_CUSTOM" ]]; then
        rm -rf "$TMPDIR_CUSTOM"
    fi
    exit "$exit_code"
}
trap cleanup EXIT
trap 'echo "Interrupted."; exit 130' INT
trap 'echo "Terminated."; exit 143' TERM

# --- Main Logic ---------------------------------------------------------------
main() {
    parse_args "$@"
    validate_dependencies
    # ... your logic here ...
}

main "$@"
```

### What the options mean

- `set -e` -- Exit immediately on any command failure.
- `set -u` -- Treat unset variables as an error.
- `set -o pipefail` -- A pipeline fails if any command in it fails, not just the last.
- `IFS=$'\n\t'` -- Safer word splitting; avoids problems with spaces in filenames.

## Variable Handling

### Quoting Rules

Always double-quote variables unless you explicitly need word splitting or globbing.

```bash
# CORRECT -- variables are quoted
name="world"
echo "Hello, $name"
cp "$source" "$destination"

# WRONG -- unquoted variables break on spaces
cp $source $destination        # Breaks if paths have spaces

# When you DO want globbing (intentionally)
for f in *.txt; do
    echo "Processing: $f"
done
```

### Variable Expansion and Defaults

```bash
# Default value if unset or empty
db_host="${DB_HOST:-localhost}"
db_port="${DB_PORT:-5432}"

# Assign default if unset or empty
: "${LOG_LEVEL:=info}"

# Error if variable is unset
: "${API_KEY:?ERROR: API_KEY must be set}"

# Substring extraction
filename="report-2024-01-15.csv"
echo "${filename:0:6}"          # "report"
echo "${filename: -3}"          # "csv" (note the space before -)

# String length
echo "${#filename}"             # 22

# Variable indirection
var_name="HOME"
echo "${!var_name}"             # prints value of $HOME
```

### Removal and Replacement

```bash
filepath="/home/user/documents/report.tar.gz"

# Remove shortest match from front
echo "${filepath#*/}"           # "home/user/documents/report.tar.gz"

# Remove longest match from front
echo "${filepath##*/}"          # "report.tar.gz" (basename)

# Remove shortest match from end
echo "${filepath%.*}"           # "/home/user/documents/report.tar"

# Remove longest match from end
echo "${filepath%%.*}"          # "/home/user/documents/report"

# Pattern substitution
echo "${filepath/user/admin}"   # "/home/admin/documents/report.tar.gz"

# Replace all occurrences
msg="foo-bar-baz"
echo "${msg//-/_}"              # "foo_bar_baz"

# Case conversion (Bash 4+)
text="Hello World"
echo "${text,,}"                # "hello world" (lowercase)
echo "${text^^}"                # "HELLO WORLD" (uppercase)
echo "${text~}"                 # "hELLO WORLD" (toggle first char)
```

## Conditionals and Test Operators

### if/elif/else

```bash
if [[ -f "$config_file" ]]; then
    source "$config_file"
elif [[ -f /etc/default/myapp ]]; then
    source /etc/default/myapp
else
    echo "No configuration found, using defaults."
fi
```

### Test Operators

```bash
# File tests
[[ -e "$path" ]]     # Exists (file, directory, symlink, etc.)
[[ -f "$path" ]]     # Regular file
[[ -d "$path" ]]     # Directory
[[ -L "$path" ]]     # Symlink
[[ -r "$path" ]]     # Readable
[[ -w "$path" ]]     # Writable
[[ -x "$path" ]]     # Executable
[[ -s "$path" ]]     # Non-empty file
[[ "$a" -nt "$b" ]]  # a is newer than b
[[ "$a" -ot "$b" ]]  # a is older than b

# String tests
[[ -z "$str" ]]      # Empty string
[[ -n "$str" ]]      # Non-empty string
[[ "$a" == "$b" ]]   # String equality
[[ "$a" != "$b" ]]   # String inequality
[[ "$a" == *.txt ]]  # Glob pattern match
[[ "$a" =~ ^[0-9]+$ ]]  # Regex match

# Numeric comparisons
[[ "$x" -eq "$y" ]]  # Equal
[[ "$x" -ne "$y" ]]  # Not equal
[[ "$x" -lt "$y" ]]  # Less than
[[ "$x" -gt "$y" ]]  # Greater than
[[ "$x" -le "$y" ]]  # Less than or equal
[[ "$x" -ge "$y" ]]  # Greater than or equal

# Logical operators inside [[ ]]
[[ -f "$f" && -r "$f" ]]    # AND
[[ -f "$f" || -d "$f" ]]    # OR
[[ ! -e "$path" ]]          # NOT
```

### Arithmetic

```bash
# Arithmetic evaluation
(( count++ ))
(( total = price * quantity ))

if (( age >= 18 )); then
    echo "Adult"
fi

# Ternary-style
(( result = (a > b) ? a : b ))
```

## Loops

### for loops

```bash
# Iterate over a list
for fruit in apple banana cherry; do
    echo "Fruit: $fruit"
done

# C-style for loop
for (( i = 0; i < 10; i++ )); do
    echo "Iteration $i"
done

# Iterate over files safely
for file in /var/log/*.log; do
    [[ -f "$file" ]] || continue   # Guard against no matches
    echo "Log: $file"
done

# Iterate over command output (line by line)
while IFS= read -r line; do
    echo "Line: $line"
done < <(find /tmp -maxdepth 1 -name "*.tmp" -type f)

# Iterate over array
declare -a servers=("web01" "web02" "db01")
for server in "${servers[@]}"; do
    echo "Pinging $server..."
done
```

### while and until

```bash
# while loop
counter=0
while (( counter < 5 )); do
    echo "Count: $counter"
    (( counter++ ))
done

# Read file line by line
while IFS= read -r line; do
    echo ">> $line"
done < "$input_file"

# Read with a custom delimiter (e.g., colon-separated)
while IFS=: read -r user _ uid gid _ home shell; do
    echo "User: $user, Home: $home, Shell: $shell"
done < /etc/passwd

# until loop (runs until condition becomes true)
until ping -c1 -W1 "$host" &>/dev/null; do
    echo "Waiting for $host to come online..."
    sleep 5
done
echo "$host is reachable."
```

### Loop Control

```bash
for i in {1..100}; do
    (( i % 2 == 0 )) && continue   # Skip even numbers
    (( i > 20 )) && break           # Stop after 20
    echo "$i"
done
```

## Functions and Return Values

```bash
# Function definition
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    printf '[%s] [%-5s] %s\n' "$timestamp" "$level" "$message"
}

# Using local variables (always use local in functions)
calculate_sum() {
    local -i a="$1"
    local -i b="$2"
    local -i result
    result=$(( a + b ))
    echo "$result"      # Return value via stdout
}

sum=$(calculate_sum 10 20)
echo "Sum: $sum"       # "Sum: 30"

# Return codes for success/failure signaling
is_valid_ip() {
    local ip="$1"
    local regex='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
    if [[ "$ip" =~ $regex ]]; then
        return 0    # success
    else
        return 1    # failure
    fi
}

if is_valid_ip "192.168.1.1"; then
    echo "Valid IP"
fi

# Function with nameref (Bash 4.3+)
get_result() {
    local -n ref="$1"
    ref="computed value"
}
get_result my_var
echo "$my_var"   # "computed value"
```

## Command-Line Argument Parsing

### Manual Parsing (Flexible, handles long options)

```bash
usage() {
    cat <<USAGE
Usage: ${SCRIPT_NAME} [OPTIONS] <input-file>

Options:
    -o, --output FILE     Output file (default: stdout)
    -v, --verbose         Enable verbose output
    -n, --dry-run         Show what would be done
    -h, --help            Show this help message
    --version             Show version

Examples:
    ${SCRIPT_NAME} -v --output result.txt data.csv
    ${SCRIPT_NAME} --dry-run input.log
USAGE
    exit "${1:-0}"
}

# Defaults
output=""
verbose=false
dry_run=false
input_file=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            [[ -n "${2:-}" ]] || { echo "Error: --output requires a value"; usage 1; }
            output="$2"
            shift 2
            ;;
        -v|--verbose)
            verbose=true
            shift
            ;;
        -n|--dry-run)
            dry_run=true
            shift
            ;;
        -h|--help)
            usage 0
            ;;
        --version)
            echo "${SCRIPT_NAME} v${VERSION}"
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            usage 1
            ;;
        *)
            input_file="$1"
            shift
            ;;
    esac
done

# Remaining positional arguments after --
[[ -n "$input_file" ]] || { echo "Error: input file required" >&2; usage 1; }
```

### getopts (POSIX compatible, short options only)

```bash
verbose=0
output=""

while getopts ":vo:h" opt; do
    case "$opt" in
        v) verbose=1 ;;
        o) output="$OPTARG" ;;
        h) usage 0 ;;
        :) echo "Error: -${OPTARG} requires an argument" >&2; exit 1 ;;
        *) echo "Error: Unknown option -${OPTARG}" >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))
```

## Input/Output Redirection and Pipes

```bash
# Standard redirections
command > file.txt          # Redirect stdout (overwrite)
command >> file.txt         # Redirect stdout (append)
command 2> errors.log       # Redirect stderr
command &> all.log          # Redirect both stdout and stderr
command > out.log 2>&1      # Same as above (POSIX compatible)
command 2>/dev/null         # Discard stderr

# Redirect both independently
command > stdout.log 2> stderr.log

# Here document
cat <<EOF > /etc/myapp.conf
# Configuration generated on $(date)
server_name=${SERVER_NAME}
port=${PORT:-8080}
EOF

# Here document without variable expansion (note the quotes)
cat <<'EOF' > script_template.sh
#!/bin/bash
echo "This $variable is literal, not expanded"
EOF

# Here string
grep "error" <<< "$log_contents"

# Process substitution
diff <(sort file1.txt) <(sort file2.txt)

# Pipeline with error checking
set -o pipefail
cat access.log | grep "500" | awk '{print $1}' | sort -u > failed_ips.txt

# tee -- write to file and stdout
command | tee output.log            # Display and save
command | tee -a output.log         # Display and append
command 2>&1 | tee debug.log        # Capture everything

# File descriptor manipulation
exec 3> custom_output.log     # Open fd 3 for writing
echo "Custom log entry" >&3
exec 3>&-                     # Close fd 3
```

## Process Management

```bash
# Run in background
long_running_task &
pid=$!
echo "Started background task with PID: $pid"

# Wait for specific process
wait "$pid"
echo "Task exited with status: $?"

# Wait for all background jobs
job1 &
job2 &
job3 &
wait    # Wait for all

# Parallel execution with controlled concurrency
max_jobs=4
for file in /data/*.csv; do
    while (( $(jobs -r | wc -l) >= max_jobs )); do
        sleep 0.5
    done
    process_file "$file" &
done
wait

# Trap signals
shutdown() {
    echo "Shutting down gracefully..."
    # Kill child processes
    kill -- -$$  2>/dev/null || true
    exit 0
}
trap shutdown SIGINT SIGTERM

# PID file for singleton enforcement
acquire_lock() {
    local pidfile="$1"
    if [[ -f "$pidfile" ]]; then
        local old_pid
        old_pid="$(cat "$pidfile")"
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "Error: Already running (PID $old_pid)" >&2
            return 1
        fi
        echo "Removing stale PID file" >&2
    fi
    echo $$ > "$pidfile"
}

release_lock() {
    local pidfile="$1"
    rm -f "$pidfile"
}

# Timeout a command
timeout 30 long_running_command || {
    echo "Command timed out after 30 seconds"
    exit 1
}
```

## String Manipulation with Parameter Expansion

No need for `sed` or `awk` for simple string operations.

```bash
str="  Hello, World!  "

# Trim leading/trailing whitespace (Bash trick)
trimmed="${str#"${str%%[![:space:]]*}"}"
trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"

# Check if string contains substring
if [[ "$str" == *"World"* ]]; then
    echo "Contains 'World'"
fi

# Split string into array
IFS=',' read -ra parts <<< "one,two,three,four"
for part in "${parts[@]}"; do
    echo "Part: $part"
done

# Join array into string
join_by() {
    local IFS="$1"
    shift
    echo "$*"
}
result=$(join_by ',' "${parts[@]}")
echo "$result"    # "one,two,three,four"

# Repeat a character
printf '=%.0s' {1..60}
echo

# Uppercase / lowercase first character
name="john"
echo "${name^}"     # "John"
name="JOHN"
echo "${name,}"     # "jOHN"
```

## Array Handling

```bash
# Indexed arrays
declare -a fruits=("apple" "banana" "cherry")
fruits+=("date")                     # Append
echo "${fruits[0]}"                  # First element
echo "${fruits[@]}"                  # All elements
echo "${#fruits[@]}"                 # Length
echo "${!fruits[@]}"                 # All indices

# Slice
echo "${fruits[@]:1:2}"             # "banana cherry"

# Remove element (leaves gap)
unset 'fruits[1]'

# Iterate
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

# Associative arrays (Bash 4+)
declare -A config
config[host]="localhost"
config[port]="8080"
config[debug]="true"

# Check if key exists
if [[ -v config[host] ]]; then
    echo "Host: ${config[host]}"
fi

# Iterate keys and values
for key in "${!config[@]}"; do
    echo "$key = ${config[$key]}"
done

# Array from command output
mapfile -t lines < <(ls -1 /tmp)
echo "Found ${#lines[@]} items in /tmp"

# Array filtering
declare -a evens=()
for n in {1..20}; do
    (( n % 2 == 0 )) && evens+=("$n")
done
echo "Evens: ${evens[*]}"
```

## Error Handling Patterns

```bash
# Custom error handler
err_handler() {
    local line_no="$1"
    local command="$2"
    local exit_code="$3"
    echo "ERROR: Command '${command}' failed at line ${line_no} with exit code ${exit_code}" >&2
}
trap 'err_handler ${LINENO} "${BASH_COMMAND}" $?' ERR

# die function for fatal errors
die() {
    echo "FATAL: $*" >&2
    exit 1
}

# Retry with exponential backoff
retry() {
    local max_attempts="${1:-3}"
    local delay="${2:-1}"
    shift 2
    local attempt=1

    until "$@"; do
        if (( attempt >= max_attempts )); then
            echo "Command failed after $max_attempts attempts: $*" >&2
            return 1
        fi
        echo "Attempt $attempt failed. Retrying in ${delay}s..." >&2
        sleep "$delay"
        (( attempt++ ))
        (( delay *= 2 ))
    done
}

# Usage: retry 5 2 curl -sf https://example.com/health

# Require commands to exist
require_cmd() {
    for cmd in "$@"; do
        command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
    done
}

require_cmd git curl jq

# Assert function
assert() {
    local description="$1"
    shift
    if ! "$@"; then
        die "Assertion failed: $description"
    fi
}

assert "Config file exists" test -f /etc/myapp.conf
```

## File Operations

```bash
# Safe temporary files
tmpfile="$(mktemp)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpfile" "$tmpdir"' EXIT

# Find files with various criteria
find /var/log -name "*.log" -mtime +30 -type f -delete    # Delete logs older than 30 days
find . -name "*.sh" -exec chmod +x {} +                   # Make all .sh files executable
find . -type f -size +100M                                  # Find files over 100MB

# Portable file reading
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "$line"
done < "$file"
# Note: || [[ -n "$line" ]] handles files without trailing newline

# Atomic file write (write to temp, then move)
atomic_write() {
    local target="$1"
    local tmp
    tmp="$(mktemp "${target}.XXXXXX")"
    if cat > "$tmp" && mv -f "$tmp" "$target"; then
        return 0
    else
        rm -f "$tmp"
        return 1
    fi
}

echo "new content" | atomic_write /etc/myapp.conf

# Check and create directory
ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || die "Cannot create directory: $dir"
    fi
}

# Compare files
if cmp -s file1.txt file2.txt; then
    echo "Files are identical"
else
    echo "Files differ"
fi

# Basename and dirname without external commands
path="/home/user/docs/report.pdf"
echo "${path##*/}"    # "report.pdf"  (basename)
echo "${path%/*}"     # "/home/user/docs" (dirname)
```

## Portable Scripting (POSIX Compliance)

```bash
# Use #!/bin/sh for POSIX scripts, #!/usr/bin/env bash for Bash scripts
# POSIX-compatible alternatives:

# Instead of [[ ]], use [ ] with proper quoting
if [ -f "$file" ] && [ -r "$file" ]; then
    echo "File exists and is readable"
fi

# Instead of (( )), use [ ] with -eq, -lt, etc.
if [ "$count" -gt 10 ]; then
    echo "Count exceeds 10"
fi

# Instead of $() for arithmetic, use expr or $(( ))
total=$((a + b))

# Instead of arrays (not POSIX), use positional parameters or IFS splitting
# Instead of local (not strictly POSIX), most shells support it anyway

# Instead of Bash-specific string manipulation, use cut, sed, or tr
# Bash:   echo "${var,,}"
# POSIX:  echo "$var" | tr '[:upper:]' '[:lower:]'

# Use printf instead of echo -e (echo behavior varies across shells)
printf 'Line 1\nLine 2\n'

# Check your scripts with shellcheck
# shellcheck disable=SC2034   -- Inline suppression
# Run: shellcheck -s bash script.sh
```

## Common Patterns

### Lockfile Pattern

```bash
LOCKFILE="/var/run/${SCRIPT_NAME}.lock"

acquire_lock() {
    if ( set -o noclobber; echo $$ > "$LOCKFILE" ) 2>/dev/null; then
        trap 'rm -f "$LOCKFILE"' EXIT
        return 0
    fi
    local lock_pid
    lock_pid="$(cat "$LOCKFILE" 2>/dev/null)"
    if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
        echo "Script is already running (PID $lock_pid)" >&2
        return 1
    fi
    echo "Removing stale lock file" >&2
    rm -f "$LOCKFILE"
    acquire_lock
}
```

### Configuration File Parsing

```bash
# Parse a simple key=value config file
declare -A CONFIG
parse_config() {
    local config_file="$1"
    [[ -f "$config_file" ]] || die "Config file not found: $config_file"

    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip blank lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Extract key and value
        local key="${line%%=*}"
        local value="${line#*=}"
        # Trim whitespace
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"
        # Remove surrounding quotes from value
        value="${value#\"}"
        value="${value%\"}"
        CONFIG["$key"]="$value"
    done < "$config_file"
}

parse_config /etc/myapp.conf
echo "DB host: ${CONFIG[db_host]:-localhost}"
```

### Logging Framework

```bash
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="${LOG_FILE:-/var/log/myapp.log}"

declare -A LOG_LEVELS=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3 [FATAL]=4)

log() {
    local level="$1"
    shift
    local message="$*"
    local current_level="${LOG_LEVELS[${LOG_LEVEL}]:-1}"
    local msg_level="${LOG_LEVELS[${level}]:-1}"

    (( msg_level < current_level )) && return

    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local entry
    entry="$(printf '[%s] [%-5s] [%s:%s] %s' "$timestamp" "$level" "${FUNCNAME[1]:-main}" "${BASH_LINENO[0]}" "$message")"

    echo "$entry" >> "$LOG_FILE"
    if [[ "$level" == "ERROR" || "$level" == "FATAL" ]]; then
        echo "$entry" >&2
    fi
}

log INFO "Application started"
log DEBUG "Verbose debugging info"
log ERROR "Something went wrong"
```

## Here Documents and Here Strings

```bash
# Here document with variable expansion
generate_html() {
    local title="$1"
    local body="$2"
    cat <<-EOF
	<!DOCTYPE html>
	<html>
	<head><title>${title}</title></head>
	<body>${body}</body>
	</html>
	EOF
}

# Here document passed to a command's stdin
mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS myapp;
GRANT ALL ON myapp.* TO 'appuser'@'localhost';
SQL

# Here string (Bash extension)
while IFS=, read -r name age city; do
    echo "Name: $name, Age: $age, City: $city"
done <<< "Alice,30,NYC
Bob,25,LA
Charlie,35,Chicago"

# Indent-stripped here doc (use <<- with tabs)
if true; then
	cat <<-'USAGE'
	Usage: command [options]
	  -h    Show help
	  -v    Verbose mode
	USAGE
fi
```

## Security Best Practices

```bash
# NEVER use eval with user input
# BAD:  eval "$user_input"
# BAD:  eval "echo $untrusted"
# GOOD: Use arrays and direct execution

# Quote EVERYTHING
rm "$file"          # GOOD
rm $file            # BAD -- breaks on spaces, globs could expand

# Validate inputs
validate_filename() {
    local name="$1"
    if [[ "$name" =~ [^a-zA-Z0-9._-] ]]; then
        die "Invalid filename: $name (contains special characters)"
    fi
    if [[ "$name" == ..* || "$name" == */* ]]; then
        die "Invalid filename: $name (path traversal attempt)"
    fi
}

# Use -- to end option parsing (prevents option injection)
rm -- "$file"
grep -- "$pattern" "$file"

# Restrict PATH
export PATH="/usr/local/bin:/usr/bin:/bin"

# Use secure temp files
tmpfile="$(mktemp)" || die "Failed to create temp file"
chmod 600 "$tmpfile"

# Avoid writing secrets to the command line (visible in ps)
# BAD:  mysql -p"$password" ...
# GOOD: Use environment variables or config files
export MYSQL_PWD="$password"
mysql -u root mydb

# Do not store secrets in shell variables that get exported
# If you must, unset them after use
unset MYSQL_PWD

# Prevent glob expansion when not needed
set -f    # Disable globbing
# ... process user input ...
set +f    # Re-enable globbing

# Drop privileges when running as root
if [[ "$(id -u)" -eq 0 ]]; then
    exec su -s /bin/bash nobody -- "$0" "$@"
fi
```

## Useful One-Liners and Idioms

```bash
# Check if running as root
(( EUID == 0 )) || die "Must run as root"

# Check if a command exists
command -v docker >/dev/null 2>&1 || die "Docker is not installed"

# Portable way to get the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Default variable using :- vs -
# ${var:-default}  uses default if var is unset OR empty
# ${var-default}   uses default only if var is unset

# Read password without echoing
read -rsp "Enter password: " password
echo

# Confirm before proceeding
confirm() {
    read -rp "${1:-Are you sure?} [y/N] " response
    [[ "$response" =~ ^[Yy]$ ]]
}
confirm "Delete all files?" || exit 0

# Progress indicator
spin() {
    local -a frames=('|' '/' '-' '\')
    while true; do
        for frame in "${frames[@]}"; do
            printf '\r%s %s' "$frame" "$1"
            sleep 0.2
        done
    done
}
spin "Working..." &
spinner_pid=$!
# ... do work ...
kill "$spinner_pid" 2>/dev/null
printf '\rDone.          \n'

# Measure execution time
start_time="$(date +%s)"
# ... do work ...
end_time="$(date +%s)"
echo "Elapsed: $(( end_time - start_time )) seconds"

# Generate random string
random_string=$(head -c 32 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 16)

# Check if stdin is a terminal
if [[ -t 0 ]]; then
    echo "Interactive mode"
else
    echo "Reading from pipe or file"
fi

# Coalesce empty values
result="${value1:-${value2:-${value3:-fallback}}}"
```

## Script Debugging

```bash
# Enable debug tracing
set -x               # Print each command before execution
set +x               # Disable tracing

# Custom trace prompt for better readability
export PS4='+${BASH_SOURCE}:${LINENO}:${FUNCNAME[0]:+${FUNCNAME[0]}():} '

# Debug only a section
debug_section() {
    set -x
    # ... commands to debug ...
    set +x
}

# Conditional debugging via environment variable
if [[ "${DEBUG:-}" == "true" ]]; then
    set -x
fi

# Debug function that respects verbosity
debug() {
    [[ "${VERBOSE:-false}" == "true" ]] && echo "DEBUG: $*" >&2
}

# Trace function calls
trace_calls() {
    echo "TRACE: ${FUNCNAME[1]} called from ${FUNCNAME[2]:-main} (line ${BASH_LINENO[1]})" >&2
}

# Dump all variables (useful for debugging)
dump_vars() {
    echo "=== Variable Dump ===" >&2
    declare -p 2>/dev/null | grep -v ' -[aAirx]' >&2
    echo "=== End Dump ===" >&2
}

# Run script in debug mode from the command line:
#   bash -x script.sh
#   bash -xv script.sh     (also shows the script lines being read)
```

## Complete Example: Backup Script

```bash
#!/usr/bin/env bash
#
# backup.sh - Incremental backup script with rotation
#

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_NAME="$(basename "$0")"
readonly VERSION="1.0.0"
readonly DEFAULT_RETENTION=7

# --- Logging ------------------------------------------------------------------
log() { printf '[%s] [%-5s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "${*:2}"; }
info()  { log INFO  "$@"; }
warn()  { log WARN  "$@"; }
error() { log ERROR "$@" >&2; }
die()   { error "$@"; exit 1; }

# --- Cleanup ------------------------------------------------------------------
cleanup() {
    local ec=$?
    [[ -n "${tmpdir:-}" ]] && rm -rf "$tmpdir"
    (( ec != 0 )) && error "Backup failed with exit code $ec"
    exit "$ec"
}
trap cleanup EXIT

# --- Usage --------------------------------------------------------------------
usage() {
    cat <<HELP
Usage: ${SCRIPT_NAME} [OPTIONS] <source-directory>

Creates a compressed, timestamped backup of the given directory.

Options:
    -d, --dest DIR          Destination directory (default: /backups)
    -r, --retention DAYS    Delete backups older than DAYS (default: ${DEFAULT_RETENTION})
    -n, --dry-run           Show what would be done
    -v, --verbose           Verbose output
    -h, --help              Show this help
    --version               Show version

Examples:
    ${SCRIPT_NAME} /etc
    ${SCRIPT_NAME} -d /mnt/nas/backups -r 30 /var/www
HELP
    exit "${1:-0}"
}

# --- Parse Arguments ----------------------------------------------------------
dest="/backups"
retention="$DEFAULT_RETENTION"
dry_run=false
verbose=false
source_dir=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--dest)      dest="${2:?--dest requires a value}"; shift 2 ;;
        -r|--retention) retention="${2:?--retention requires a value}"; shift 2 ;;
        -n|--dry-run)   dry_run=true; shift ;;
        -v|--verbose)   verbose=true; shift ;;
        -h|--help)      usage 0 ;;
        --version)      echo "${SCRIPT_NAME} v${VERSION}"; exit 0 ;;
        --)             shift; break ;;
        -*)             die "Unknown option: $1" ;;
        *)              source_dir="$1"; shift ;;
    esac
done

[[ -n "$source_dir" ]]   || { error "Source directory required"; usage 1; }
[[ -d "$source_dir" ]]   || die "Source is not a directory: $source_dir"
command -v tar >/dev/null || die "tar is required but not found"

# --- Main Logic ---------------------------------------------------------------
main() {
    local timestamp
    timestamp="$(date '+%Y%m%d-%H%M%S')"
    local archive_name
    archive_name="backup-$(basename "$source_dir")-${timestamp}.tar.gz"
    local archive_path="${dest}/${archive_name}"

    info "Backing up: $source_dir -> $archive_path"

    if "$dry_run"; then
        info "[DRY RUN] Would create: $archive_path"
        info "[DRY RUN] Would remove backups older than $retention days"
        return 0
    fi

    mkdir -p "$dest"
    tmpdir="$(mktemp -d)"

    local tmp_archive="${tmpdir}/${archive_name}"
    tar -czf "$tmp_archive" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
    mv "$tmp_archive" "$archive_path"
    chmod 600 "$archive_path"

    local size
    size="$(du -sh "$archive_path" | cut -f1)"
    info "Backup complete: $archive_path ($size)"

    # Rotate old backups
    local deleted=0
    while IFS= read -r old_backup; do
        rm -f "$old_backup"
        (( deleted++ ))
        "$verbose" && info "Deleted old backup: $old_backup"
    done < <(find "$dest" -name "backup-$(basename "$source_dir")-*.tar.gz" -mtime "+${retention}" -type f)

    (( deleted > 0 )) && info "Removed $deleted old backup(s)"
    info "Done."
}

main
```

## References

- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck - Shell Script Analysis Tool](https://www.shellcheck.net/)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/)
- [POSIX Shell Command Language Specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Wooledge Bash FAQ](https://mywiki.wooledge.org/BashFAQ)
- [Wooledge Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls)
