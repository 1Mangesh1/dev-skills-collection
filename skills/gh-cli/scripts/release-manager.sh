#!/usr/bin/env bash
# GitHub Release Manager
# Automate release creation and publishing

create_release() {
    local version="$1"
    local notes="$2"
    
    echo "=== Creating Release $version ==="
    
    # Tag first
    git tag -a "v$version" -m "Release $version"
    
    # Create GitHub release
    gh release create "v$version" \
        --title "Version $version" \
        --notes "$notes"
}

list_releases() {
    echo "=== Recent Releases ==="
    gh release list --limit 10
}

upload_asset() {
    local release_tag="$1"
    local asset_file="$2"
    
    gh release upload "$release_tag" "$asset_file"
}

# Usage
create_release "1.2.0" "Added dark mode and fixed login bug"
