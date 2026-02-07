#!/usr/bin/env bash
# Bundle Size Analyzer
# Reports JavaScript bundle sizes and splits

analyze_bundle() {
    local bundle_dir="$1"
    
    echo "=== Bundle Analysis ==="
    echo ""
    echo "Overall Size:"
    du -sh "$bundle_dir" | awk '{print "  Total: " $1}'
    
    echo ""
    echo "By File:"
    ls -lh "$bundle_dir"/*.js | awk '{print "  " $9 ": " $5}'
    
    echo ""
    echo "Recommendations:"
    echo "  - Target: < 200KB for JavaScript"
    echo "  - Use code splitting for routes"
    echo "  - Enable tree shaking in build"
    echo "  - Compress with gzip/brotli"
}

# Usage
analyze_bundle "./dist"
