#!/bin/bash
# Test Suite Runner - Execute all tests and generate reports
# Runs unit tests, integration tests, and generates coverage reports

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="${1:-.}"
TEST_REPORT_DIR="${PROJECT_ROOT}/test-reports"
COVERAGE_THRESHOLD="${2:-80}"

mkdir -p "$TEST_REPORT_DIR"

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Run Python unit tests
run_python_tests() {
    print_header "Running Python Unit Tests"
    
    if command -v python3 &> /dev/null; then
        cd "$PROJECT_ROOT"
        
        if [[ -f "pytest.ini" ]] || [[ -f "setup.py" ]]; then
            python3 -m pytest \
                --verbose \
                --cov=. \
                --cov-report=term-missing \
                --cov-report=html:"$TEST_REPORT_DIR/coverage_html" \
                --cov-report=json:"$TEST_REPORT_DIR/coverage.json" \
                --junit-xml="$TEST_REPORT_DIR/junit.xml" \
                tests/ 2>&1 | tee "$TEST_REPORT_DIR/python-tests.log"
            
            python_exit_code=$?
        else
            python3 -m unittest discover -s tests -p "*_test.py" -v 2>&1 | \
                tee "$TEST_REPORT_DIR/python-tests.log"
            python_exit_code=$?
        fi
        
        if [[ $python_exit_code -eq 0 ]]; then
            print_success "Python tests passed"
        else
            print_error "Python tests failed"
        fi
        
        return $python_exit_code
    fi
    
    return 0
}

# Run JavaScript/Node tests
run_js_tests() {
    print_header "Running JavaScript Tests"
    
    if [[ -f "package.json" ]]; then
        if grep -q '"test"' package.json; then
            npm test -- --coverage 2>&1 | tee "$TEST_REPORT_DIR/js-tests.log"
            return $?
        fi
    fi
    
    return 0
}

# Check coverage thresholds
check_coverage() {
    print_header "Checking Code Coverage"
    
    if [[ -f "$TEST_REPORT_DIR/coverage.json" ]]; then
        coverage_pct=$(python3 -c "
import json
with open('$TEST_REPORT_DIR/coverage.json') as f:
    data = json.load(f)
    total_coverage = data.get('totals', {}).get('percent_covered', 0)
    print(int(total_coverage))
")
        
        echo "Overall coverage: ${coverage_pct}%"
        
        if [[ $coverage_pct -ge $COVERAGE_THRESHOLD ]]; then
            print_success "Coverage meets threshold (${coverage_pct}% >= ${COVERAGE_THRESHOLD}%)"
            return 0
        else
            print_error "Coverage below threshold (${coverage_pct}% < ${COVERAGE_THRESHOLD}%)"
            return 1
        fi
    fi
    
    return 0
}

# Run linting checks
run_linting() {
    print_header "Running Code Quality Checks"
    
    cd "$PROJECT_ROOT"
    
    # Python linting
    if command -v pylint &> /dev/null; then
        pylint **/*.py --exit-zero > "$TEST_REPORT_DIR/pylint-report.txt" 2>&1 || true
        print_success "Pylint check completed"
    fi
    
    # Python formatting
    if command -v black &> /dev/null; then
        black --check . --quiet 2>&1 || print_error "Code formatting issues found"
    fi
    
    # JavaScript linting
    if [[ -f "package.json" ]]; then
        if grep -q '"lint"' package.json; then
            npm run lint 2>&1 | tee "$TEST_REPORT_DIR/eslint-report.txt" || true
        fi
    fi
}

# Run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    
    if [[ -d "tests/integration" ]]; then
        if command -v python3 &> /dev/null; then
            python3 -m pytest tests/integration/ -v --tb=short 2>&1 | \
                tee "$TEST_REPORT_DIR/integration-tests.log"
            return $?
        fi
    fi
    
    return 0
}

# Generate test report
generate_report() {
    print_header "Test Report Generation"
    
    cat > "$TEST_REPORT_DIR/summary.txt" << EOF
Test Execution Summary
======================
Timestamp: $(date)
Project: $PROJECT_ROOT
Coverage Threshold: ${COVERAGE_THRESHOLD}%

Test Results:
- Unit Tests: $(grep -c 'PASSED\|passed' "$TEST_REPORT_DIR/python-tests.log" 2>/dev/null || echo "N/A")
- Integration Tests: $(grep -c 'PASSED\|passed' "$TEST_REPORT_DIR/integration-tests.log" 2>/dev/null || echo "N/A")

Reports Generated:
- Coverage: $TEST_REPORT_DIR/coverage_html/index.html
- Detailed Logs: $TEST_REPORT_DIR/
EOF
    
    echo ""
    echo "Test reports saved to: $TEST_REPORT_DIR"
    echo "Coverage HTML report: $TEST_REPORT_DIR/coverage_html/index.html"
}

# Main execution
main() {
    print_header "Test Suite Runner"
    
    local failed_checks=0
    
    run_python_tests || ((failed_checks++))
    run_js_tests || ((failed_checks++))
    run_linting || ((failed_checks++))
    run_integration_tests || ((failed_checks++))
    check_coverage || ((failed_checks++))
    
    generate_report
    
    if [[ $failed_checks -eq 0 ]]; then
        print_success "All tests passed"
        return 0
    else
        print_error "$failed_checks check(s) failed"
        return 1
    fi
}

main "$@"
