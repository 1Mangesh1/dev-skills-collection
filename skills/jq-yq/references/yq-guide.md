# YAML Processing with yq

## Installation

```bash
# macOS
brew install yq

# Ubuntu
sudo apt install yq

# Using Python
pip install yq
```

## Basic Syntax

```bash
# Pretty print
yq '.' config.yaml

# Extract field
yq '.database.host' config.yaml

# List all keys
yq 'keys' config.yaml

# Get value or default
yq '.field // "default"' config.yaml
```

## Kubernetes-specific

```bash
# Get all container names
yq '.spec.template.spec.containers[].name' deployment.yaml

# Get environment vars
yq '.spec.template.spec.containers[].env[] | {name, value}' deployment.yaml

# Filter resources by type
yq 'select(.kind == "Service")' resources.yaml
```

## Transformations

```bash
# Update value
yq '.metadata.name = "new-name"' config.yaml

# Add field
yq '.metadata.labels.app = "myapp"' config.yaml

# Delete field
yq 'del(.metadata.managedFields)' config.yaml

# Merge files
yq eval-all '. as $item |-pick($item; ["a", "b"]) | . + $item' file1.yaml file2.yaml
```

## Output Formats

```bash
# JSON output
yq '.' --output-format json config.yaml

# Properties format
yq '.' --output-format props config.yaml

# XML format
yq '.' --output-format xml config.yaml
```

## Multi-file Operations

```bash
# Process multiple files
yq eval '.metadata.name' *.yaml

# Merge and split
yq eval -s '.' config1.yaml config2.yaml | yq eval -s '.[0] + .[1]'

# Filter across files
yq eval 'select(.kind == "Deployment")' *.yaml
```
