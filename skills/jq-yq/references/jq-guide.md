# jq JSON Processing

## Installation

```bash
# macOS
brew install jq

# Ubuntu
sudo apt install jq

# Windows
choco install jq
```

## Basic Syntax

```bash
# Pretty print
jq '.' data.json

# Extract field
jq '.name' data.json
jq '.user.email' data.json

# Array access
jq '.[0]' data.json
jq '.items[2]' data.json

# Pipe operations
jq '.users | length' data.json
```

## Filtering

```bash
# Select by condition
jq '.items[] | select(.price > 100)' data.json

# Map values
jq '.items[] | {id, name, price}' data.json

# Modify values
jq '.items[].price *= 1.1' data.json  # Increase by 10%
```

## Complex Queries

```bash
# Group by
jq 'group_by(.category)' data.json

# Sort
jq 'sort_by(.price)' data.json

# Reduce/Aggregate
jq '[.items[].price] | add' data.json  # Sum

# Conditional
jq '.items[] | if .active then .name else empty end' data.json
```

## Output Formats

```bash
# Raw output (no quotes)
jq -r '.name' data.json

# Compact output
jq -c '.' data.json

# Slurp (read whole file as array)
jq -s '.' data.json

# Tab-separated output
jq -r '.users[] | [.name, .email] | @tsv' data.json
```

## Advanced

```bash
# Recursive descent
jq '.. | .name?' data.json  # Find all names (including nested)

# Try-catch
jq '.field? // "default"' data.json

# String interpolation
jq '"\(.name) is \(.age) years old"' data.json

# Join arrays
jq '[.items[] | .name] | join(", ")' data.json
```
