#!/usr/bin/env bash
# Changelog Generator
# Auto-generate changelog from git commits

generate_changelog() {
    local version="$1"
    local previous_tag="$(git describe --tags --abbrev=0 2>/dev/null || echo 'HEAD~100')"
    
    echo "# Changelog"
    echo ""
    echo "## [$version] - $(date +%Y-%m-%d)"
    echo ""
    
    echo "### Features"
    git log "$previous_tag"..HEAD --grep="^feat" --pretty=format:"- %s (%h)" || echo "- No features"
    echo ""
    
    echo "### Bug Fixes"
    git log "$previous_tag"..HEAD --grep="^fix" --pretty=format:"- %s (%h)" || echo "- No fixes"
    echo ""
    
    echo "### Breaking Changes"
    git log "$previous_tag"..HEAD --grep="^BREAKING" --pretty=format:"- %s (%h)" || echo "- No breaking changes"
}

# Usage
generate_changelog "1.2.0"
