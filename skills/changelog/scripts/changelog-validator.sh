#!/bin/bash
# Changelog Validator - Validate CHANGELOG.md format and completeness
# Usage: ./changelog-validator.sh [CHANGELOG.md]

set -e

CHANGELOG_FILE="${1:-CHANGELOG.md}"
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
NC='\033[0m'

print_error() {
    echo -e "${COLOR_RED}✗ $1${NC}"
}

print_success() {
    echo -e "${COLOR_GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠ $1${NC}"
}

check_file_exists() {
    if [ ! -f "$CHANGELOG_FILE" ]; then
        print_error "File not found: $CHANGELOG_FILE"
        exit 1
    fi
    print_success "File found: $CHANGELOG_FILE"
}

check_headers() {
    if ! grep -q "^# Changelog" "$CHANGELOG_FILE"; then
        print_error "Missing main header '# Changelog'"
        return 1
    fi
    print_success "Main header found"
    
    if ! grep -qE "^## \[" "$CHANGELOG_FILE"; then
        print_warning "No version headers found (expecting '## [version]')"
    else
        print_success "Version headers found"
    fi
}

check_format() {
    local has_format_issues=0
    
    # Check for consistent formatting
    if ! grep -qE "^-\s" "$CHANGELOG_FILE"; then
        print_warning "No bullet points (- style) found in changelog"
        has_format_issues=1
    else
        print_success "Bullet points found"
    fi
    
    # Check for dates
    if ! grep -qE "\d{4}-\d{2}-\d{2}" "$CHANGELOG_FILE"; then
        print_warning "No dates found in YYYY-MM-DD format"
    else
        print_success "Dates in correct format found"
    fi
    
    return $has_format_issues
}

check_entries() {
    local version_count=$(grep -cE "^## \[" "$CHANGELOG_FILE" || true)
    local entry_count=$(grep -cE "^-\s" "$CHANGELOG_FILE" || true)
    
    echo "Found $version_count version(s) and $entry_count changelog entries"
    
    if [ "$entry_count" -eq 0 ]; then
        print_warning "No changelog entries found"
        return 1
    fi
    
    print_success "Changelog entries present ($entry_count)"
}

check_conventions() {
    # Check for common prefixes (feat, fix, etc.)
    local has_conventional=0
    
    if grep -qiE "\(feat\)|\(fix\)|\(docs\)|\(refactor\)" "$CHANGELOG_FILE"; then
        print_success "Conventional commit prefixes found"
        has_conventional=1
    else
        print_warning "No conventional commit prefixes detected"
    fi
    
    return $((1 - has_conventional))
}

main() {
    echo "Validating $CHANGELOG_FILE..."
    echo ""
    
    check_file_exists
    echo ""
    
    echo "Checking structure:"
    check_headers
    echo ""
    
    echo "Checking format:"
    check_format
    echo ""
    
    echo "Checking content:"
    check_entries
    echo ""
    
    echo "Checking conventions:"
    check_conventions
    echo ""
    
    print_success "Validation complete!"
}

main
