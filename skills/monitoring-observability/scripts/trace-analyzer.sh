#!/bin/bash
# Trace Analyzer - Analyze distributed traces and service latency
# Helps identify bottlenecks in microservice architectures

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Analyze trace latency
analyze_trace_latency() {
    local trace_file=$1
    
    print_header "Trace Latency Analysis"
    
    if [[ ! -f "$trace_file" ]]; then
        print_error "Trace file not found: $trace_file"
        return 1
    fi
    
    # Extract spans and calculate latencies
    jq -r '.spans[] | "\(.spanName): \(.duration)ms"' "$trace_file" 2>/dev/null | sort -t: -k2 -rn | head -10
}

# Identify slow services
identify_slow_services() {
    local trace_file=$1
    local threshold=${2:-1000}  # Default 1000ms
    
    print_header "Slow Services (>${threshold}ms)"
    
    jq -r --arg threshold "$threshold" \
        '.spans[] | select(.duration > ($threshold | tonumber)) | "\(.serviceName): \(.spanName) - \(.duration)ms"' \
        "$trace_file" 2>/dev/null || true
}

# Analyze service dependencies
analyze_service_dependencies() {
    local trace_file=$1
    
    print_header "Service Dependency Trace"
    
    jq -r '.spans[] | "\(.serviceName) → \(.parentService // "ROOT")"' "$trace_file" 2>/dev/null | sort | uniq
}

# Count spans by service
count_spans_by_service() {
    local trace_file=$1
    
    print_header "Span Count By Service"
    
    jq -r '.spans[].serviceName' "$trace_file" 2>/dev/null | sort | uniq -c | sort -rn
}

# Detect error spans
detect_error_spans() {
    local trace_file=$1
    
    print_header "Error Spans"
    
    error_count=$(jq '[.spans[] | select(.status == "ERROR")] | length' "$trace_file" 2>/dev/null || echo 0)
    
    if [[ $error_count -gt 0 ]]; then
        print_warning "Found $error_count error spans"
        jq -r '.spans[] | select(.status == "ERROR") | "\(.serviceName): \(.spanName) - \(.error)"' "$trace_file" 2>/dev/null | head -5
    else
        print_success "No error spans detected"
    fi
}

# Generate trace summary
generate_trace_summary() {
    local trace_file=$1
    
    print_header "Trace Summary"
    
    jq '{
        "traceId": .traceId,
        "totalDuration": .duration,
        "spanCount": (.spans | length),
        "serviceCount": [.spans[].serviceName] | unique | length,
        "errorCount": [.spans[] | select(.status == "ERROR")] | length,
        "warningCount": [.spans[] | select(.status == "WARNING")] | length
    }' "$trace_file" 2>/dev/null || print_error "Failed to parse trace file"
}

# Main execution
main() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <trace_file> [threshold_ms]"
        echo ""
        echo "Commands:"
        echo "  analyze_latency <file>           - Analyze trace latency"
        echo "  slow_services <file> [threshold] - Identify slow services"
        echo "  dependencies <file>              - Analyze service dependencies"
        echo "  count_spans <file>               - Count spans by service"
        echo "  errors <file>                    - Detect error spans"
        echo "  summary <file>                   - Generate trace summary"
        exit 1
    fi
    
    local trace_file=$1
    
    # Generate full report
    generate_trace_summary "$trace_file"
    analyze_trace_latency "$trace_file"
    identify_slow_services "$trace_file" "${2:-1000}"
    count_spans_by_service "$trace_file"
    detect_error_spans "$trace_file"
    analyze_service_dependencies "$trace_file"
}

main "$@"
