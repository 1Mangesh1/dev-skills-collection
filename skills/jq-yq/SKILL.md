---
name: jq-yq
description: JSON and YAML processing with jq and yq command-line tools. Use when user asks to "parse JSON", "transform YAML", "extract from JSON", "filter JSON array", "convert YAML to JSON", "query JSON", "jq filter", "yq select", "process API response", "parse logs as JSON", "merge YAML files", "convert JSON to CSV", "stream large JSON", "jq reduce", "group_by", "unique_by", or manipulate structured data from the command line.
---

# jq & yq

Command-line JSON and YAML processing.

## jq Fundamentals

### Extract Values

```bash
# Get field / nested field
echo '{"name":"John","age":30}' | jq '.name'
echo '{"user":{"name":"John"}}' | jq '.user.name'

# Array element
echo '[1,2,3]' | jq '.[0]'

# Multiple fields
echo '{"a":1,"b":2,"c":3}' | jq '{a,b}'

# Optional field access (no error if missing)
echo '{"a":1}' | jq '.b?'
```

### Array Operations

```bash
# Iterate, filter, map
echo '[1,2,3]' | jq '.[]'
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 2)]'
echo '[1,2,3]' | jq 'map(. * 2)'

# Length, first, last
echo '[1,2,3]' | jq 'length'
echo '[1,2,3]' | jq 'first'

# Flatten nested arrays
echo '[[1,2],[3,[4,5]]]' | jq 'flatten'

# Slice
echo '[10,20,30,40,50]' | jq '.[2:4]'
```

### Object Arrays

```bash
# Extract, filter, sort
echo '[{"name":"a"},{"name":"b"}]' | jq '.[].name'
echo '[{"age":20},{"age":30}]' | jq '[.[] | select(.age > 25)]'
echo '[{"a":2},{"a":1}]' | jq 'sort_by(.a)'

# Group by field
echo '[{"type":"a","v":1},{"type":"b","v":2},{"type":"a","v":3}]' | jq 'group_by(.type)'

# Unique by field
echo '[{"id":1,"n":"a"},{"id":2,"n":"b"},{"id":1,"n":"c"}]' | jq 'unique_by(.id)'

# Min/max by field
echo '[{"score":80},{"score":95},{"score":72}]' | jq 'min_by(.score)'
```

### Object Construction and Deconstruction

```bash
# Build new object with string interpolation
echo '{"first":"John","last":"Doe"}' | jq '{fullName: "\(.first) \(.last)"}'

# Add/delete/rename fields
echo '{"a":1}' | jq '. + {b:2}'
echo '{"a":1,"b":2}' | jq 'del(.b)'
echo '{"old":1}' | jq '{new: .old}'

# Flatten nested structure
echo '{"user":{"name":"Jo","addr":{"city":"NYC"}}}' | jq '{name: .user.name, city: .user.addr.city}'

# to_entries / from_entries (object <-> key-value pairs)
echo '{"a":1,"b":2}' | jq '[to_entries[] | {(.key): (.value * 10)}] | add'

# with_entries shorthand
echo '{"a":1,"b":2}' | jq 'with_entries(.value += 100)'
```

### String Interpolation and Formatting

```bash
# Interpolation
echo '{"name":"Jo","age":30}' | jq -r '"Name: \(.name), Age: \(.age)"'

# Join / split
echo '["a","b","c"]' | jq 'join(", ")'
echo '"a,b,c"' | jq 'split(",")'

# Regex test and capture
echo '"hello"' | jq 'test("^hel")'
echo '"2024-01-15"' | jq 'capture("(?<y>[0-9]{4})-(?<m>[0-9]{2})-(?<d>[0-9]{2})")'
# {"y":"2024","m":"01","d":"15"}
```

### Conditionals and Null Handling

```bash
# If-then-else
echo '{"age":20}' | jq 'if .age >= 18 then "adult" else "minor" end'

# Alternative operator (null coalescing)
echo '{"a":null}' | jq '.a // "default"'

# try-catch
echo '{"a":1}' | jq 'try .b.c.d catch "missing"'

# any/all
echo '[1,2,3]' | jq 'all(. > 0)'
```

### Reduce and Aggregation

```bash
# Sum values
echo '[1,2,3,4,5]' | jq 'add'

# Reduce: accumulate a result
echo '[1,2,3,4,5]' | jq 'reduce .[] as $x (0; . + $x)'

# Build object from array
echo '[{"k":"a","v":1},{"k":"b","v":2}]' | jq 'reduce .[] as $item ({}; . + {($item.k): $item.v})'

# Group and aggregate
echo '[{"dept":"eng","sal":100},{"dept":"eng","sal":120},{"dept":"sales","sal":90}]' | \
  jq 'group_by(.dept) | map({dept: .[0].dept, total: map(.sal) | add, count: length})'
```

### Recursive Descent

```bash
# Find all values for a key at any depth
echo '{"a":{"name":"x","b":{"name":"y"}}}' | jq '.. | .name? // empty'

# Find all strings / numbers in a structure
echo '{"a":1,"b":"hello","c":{"d":"world"}}' | jq '[.. | strings]'
echo '{"a":1,"b":{"c":2},"d":[3,4]}' | jq '[.. | numbers]'
```

### Output Flags and Format Encoders

```bash
# Raw output (no quotes) / compact output
echo '{"name":"John"}' | jq -r '.name'
echo '{"a":1}' | jq -c '.'

# Slurp multiple values into array
cat lines.json | jq -s '.'

# Raw input: treat each line as a string
echo -e "line1\nline2" | jq -R '.'

# Null input: generate JSON without input
jq -n '{created: now | todate}'

# TSV / CSV / URI encoding
echo '[{"n":"a","v":1},{"n":"b","v":2}]' | jq -r '.[] | [.n, .v] | @tsv'
echo '[{"n":"a","v":1},{"n":"b","v":2}]' | jq -r '.[] | [.n, .v] | @csv'
echo '{"q":"hello world"}' | jq -r '.q | @uri'
```

## CSV/TSV Conversion

```bash
# JSON array of objects to CSV with header
echo '[{"name":"a","age":1},{"name":"b","age":2}]' | \
  jq -r '(.[0] | keys_unsorted) as $k | $k, (.[] | [.[$k[]]])| @csv'

# CSV to JSON (line-by-line)
cat data.csv | jq -R 'split(",") | {id: .[0], name: .[1], value: .[2]}'
```

## Environment Variable Integration

```bash
# Pass string variable into jq
NAME="John"
echo '{}' | jq --arg name "$NAME" '. + {name: $name}'

# Pass numeric / JSON value
echo '{}' | jq --argjson count 42 '. + {count: $count}'
TAGS='["a","b"]'
echo '{}' | jq --argjson tags "$TAGS" '. + {tags: $tags}'

# Access env directly
export MY_VAR="hello"
echo '{}' | jq -n 'env.MY_VAR'
```

## yq YAML Processing

### Read, Update, Delete

```bash
yq '.name' file.yaml
yq '.database.host' config.yaml
yq -i '.version = "2.0"' file.yaml
yq -i '.new_field = "value"' file.yaml
yq -i 'del(.unwanted)' file.yaml
yq 'keys' config.yaml
```

### Select and Filter

```bash
yq '.items[] | select(.enabled == true)' config.yaml
yq '.services[] | select(has("port"))' config.yaml
yq 'select(.kind == "Service")' resources.yaml
yq '.spec.template.spec.containers[].image' deployment.yaml
```

### Merge YAML Files

```bash
# Deep merge (second overrides first)
yq ea 'select(fileIndex == 0) * select(fileIndex == 1)' base.yaml override.yaml

# Merge all documents into one
yq ea '. as $item ireduce ({}; . * $item)' *.yaml
```

### Convert Between Formats

```bash
yq -o=json file.yaml          # YAML to JSON
yq -P file.json               # JSON to YAML
yq -o=xml file.yaml           # YAML to XML
yq -o=props file.yaml         # YAML to properties
curl -s https://api.example.com/data | yq -P  # pipe JSON to YAML
```

### Multiple Documents

```bash
yq 'select(documentIndex == 0)' multi.yaml
yq 'select(documentIndex >= 0) | .metadata.namespace = "prod"' multi.yaml
yq ea '[.] | length' multi.yaml
```

## Real-World Pipelines

### API Response Processing with curl

```bash
# Get specific fields from API
curl -s 'https://api.github.com/repos/jqlang/jq/issues?per_page=5' | \
  jq '[.[] | {number, title, state, user: .user.login}]'

# Paginate and collect
for page in $(seq 1 5); do
  curl -s "https://api.example.com/items?page=$page"
done | jq -s 'map(.data[]) | flatten'

# Format as table
curl -s https://api.example.com/users | \
  jq -r '.data[] | [.id, .name, .email] | @tsv' | column -t
```

### Log Parsing

```bash
# Parse JSON log lines and filter errors
cat app.log | jq -R 'fromjson? | select(.level == "error")' 2>/dev/null

# Aggregate log levels
cat app.log | jq -R 'fromjson? | .level' 2>/dev/null | \
  jq -s 'group_by(.) | map({level: .[0], count: length})'
```

### Config File Manipulation

```bash
# Update version in package.json
jq '.version = "1.2.3"' package.json > tmp.$$ && mv tmp.$$ package.json

# Merge base and override configs
jq -s '.[0] * .[1]' base.json override.json > merged.json

# Bulk update scoped dependencies
jq '.dependencies |= with_entries(if .key | test("^@myorg/") then .value = "latest" else . end)' package.json

# Generate config from env vars
jq -n --arg host "$DB_HOST" --argjson port "${DB_PORT:-5432}" \
  '{database: {host: $host, port: $port, ssl: true}}'
```

### Kubernetes and Infrastructure

```bash
kubectl get pods -o json | jq -r '.items[].metadata.name'
kubectl get pods -o json | jq '.items[] | select(.status.phase != "Running") | .metadata.name'
yq -i '.spec.replicas = 3' deployment.yaml
```

## Error Handling in Pipelines

```bash
# Try operator: skip errors silently
echo '[1,"two",3]' | jq '[.[] | try (. + 1)]'

# Validate JSON before processing
if echo "$data" | jq empty 2>/dev/null; then
  echo "$data" | jq '.result'
else
  echo "Invalid JSON"
fi

# Handle missing fields gracefully
echo '{"users":[{"name":"a"},{"email":"b@b.com"}]}' | \
  jq '.users[] | {name: (.name // "unknown"), email: (.email // "none")}'

# -e flag: exit non-zero if result is false/null
curl -sf https://api.example.com/data | jq -e '.results | length > 0' > /dev/null
```

## Performance: Streaming Large Files

```bash
# Stream parse: process without loading entire file into memory
jq --stream 'select(.[0][-1] == "name") | .[1]' huge.json

# Truncated stream: get first N matches efficiently
jq -c '.[]' huge_array.json | head -100 | jq -s '.'

# NDJSON: each line parsed independently, constant memory
cat large.ndjson | jq -c 'select(.status == "error")'

# Compare two large JSON files (sorted keys)
diff <(jq -S '.' a.json) <(jq -S '.' b.json)
```

## Quick Reference

| Task | jq | yq |
|---|---|---|
| Pretty print | `jq '.'` | `yq '.'` |
| Get field | `jq '.key'` | `yq '.key'` |
| Filter | `jq 'select(.x > 1)'` | `yq 'select(.x > 1)'` |
| Delete | `jq 'del(.key)'` | `yq 'del(.key)'` |
| Merge | `jq -s '.[0] * .[1]'` | `yq ea '. as $i ireduce({}; . * $i)'` |
| To JSON/YAML | -- | `yq -o=json` / `yq -P` |
| Raw output | `jq -r` | `yq -r` |
| In-place | temp file or `sponge` | `yq -i` |
