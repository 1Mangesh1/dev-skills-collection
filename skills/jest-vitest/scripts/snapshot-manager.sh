#!/usr/bin/env bash
# Test Snapshot Manager
# Manage and update Jest snapshots

update_snapshots() {
    echo "=== Updating Snapshots ==="
    npx jest --updateSnapshot
    echo "✓ Snapshots updated"
}

view_snapshots() {
    echo "=== Snapshot Files ==="
    find . -name "*.snap" -type f | head -20
}

# Usage
update_snapshots
