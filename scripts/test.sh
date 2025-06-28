#!/bin/bash
# Testing script for Patient Risk Predictor

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored headers
print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}${BOLD}                   TEST UTILITIES                            ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}${BOLD} $1 ${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print info messages
print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to show usage
show_usage() {
    print_header
    print_section "TESTING COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}all${NC}               Run all tests with coverage ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${GREEN}unit${NC}              Run unit tests only"
    echo -e "  ${GREEN}integration${NC}       Run integration tests only"
    echo -e "  ${GREEN}quick${NC}             Run tests without coverage (faster)"
    echo -e "  ${GREEN}parallel${NC}          Run tests in parallel"
    echo -e "  ${GREEN}coverage${NC}          Generate detailed coverage report"
    echo -e "  ${GREEN}codecov${NC}           Generate Codecov-compatible coverage report"
    echo -e "  ${GREEN}ci${NC}                Run CI test suite"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0${NC}                ${WHITE}# Run all tests${NC}"
    echo -e "  ${CYAN}$0 quick${NC}          ${WHITE}# Quick test run${NC}"
    echo -e "  ${CYAN}$0 unit${NC}           ${WHITE}# Unit tests only${NC}"
    echo -e "  ${CYAN}$0 coverage${NC}       ${WHITE}# Generate coverage report${NC}"
    echo -e "  ${CYAN}$0 codecov${NC}        ${WHITE}# Generate Codecov coverage${NC}"
    echo ""
}

# Run all tests with coverage
test_all() {
    print_section "🧪 RUNNING ALL TESTS"
    print_info "Running complete test suite with coverage..."
    
    python -m pytest -c config/testing/pytest.ini
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed!"
        print_info "Coverage report: reports/coverage/coverage.xml"
        print_info "HTML coverage: reports/coverage/htmlcov/index.html"
        print_info "Test results: reports/tests/test-results.xml"
    else
        print_error "Some tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Run unit tests only
test_unit() {
    print_section "🔬 RUNNING UNIT TESTS"
    print_info "Running unit tests with coverage..."
    
    python -m pytest tests/unit/ -c config/testing/pytest.ini \
        --junitxml=reports/tests/test-results-unit.xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Run integration tests only
test_integration() {
    print_section "🔗 RUNNING INTEGRATION TESTS"
    print_info "Running integration tests..."
    
    python -m pytest tests/integration/ -c config/testing/pytest.ini \
        --junitxml=reports/tests/test-results-integration.xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Integration tests passed!"
    else
        print_error "Integration tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Run quick tests (no coverage)
test_quick() {
    print_section "⚡ RUNNING QUICK TESTS"
    print_info "Running tests without coverage (faster)..."
    
    python -m pytest tests/ -x --tb=no --quiet
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Quick tests passed!"
    else
        print_error "Quick tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Run tests in parallel
test_parallel() {
    print_section "⚡ RUNNING PARALLEL TESTS"
    print_info "Running tests in parallel..."
    
    # Check if pytest-xdist is available
    if ! python -c "import xdist" 2>/dev/null; then
        print_warning "pytest-xdist not installed, running normally..."
        test_all
        return
    fi
    
    python -m pytest tests/ -n auto \
        --cov=src \
        --cov-report=xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Parallel tests passed!"
    else
        print_error "Parallel tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Generate detailed coverage report
test_coverage() {
    print_section "📊 GENERATING COVERAGE REPORT"
    print_info "Running tests and generating detailed coverage report..."
    
    python -m pytest \
        --cov=src \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Coverage report generated!"
        print_info "HTML report: htmlcov/index.html"
        print_info "XML report: coverage.xml"
        echo ""
        print_info "Open htmlcov/index.html in your browser to view detailed coverage"
    else
        print_error "Coverage generation failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Generate Codecov-compatible coverage report
test_codecov() {
    print_section "☁️  GENERATING CODECOV COVERAGE"
    print_info "Running tests and generating Codecov-compatible coverage..."
    
    # Delegate to dedicated codecov script
    if [ -f "scripts/codecov.sh" ]; then
        ./scripts/codecov.sh test
    else
        print_warning "codecov.sh script not found, using fallback..."
        python -m pytest \
            --cov=src \
            --cov-report=xml:coverage.xml \
            --cov-report=term-missing \
            tests/
        
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            print_success "Codecov coverage generated!"
            print_info "XML report: coverage.xml"
        else
            print_error "Codecov coverage generation failed (exit code: $exit_code)"
            exit $exit_code
        fi
    fi
}

# Run CI test suite
test_ci() {
    print_section "🤖 RUNNING CI TEST SUITE"
    print_info "Running complete CI test pipeline..."
    
    # Setup CI environment if needed
    print_info "Setting up CI environment..."
    mkdir -p /tmp/test_mlruns
    mkdir -p logs
    mkdir -p htmlcov
    
    # Run unit tests
    print_info "Running unit tests..."
    test_unit
    
    # Run integration tests
    print_info "Running integration tests..."
    test_integration
    
    print_success "CI test suite completed successfully!"
}

# Main script logic
COMMAND=${1:-all}

case $COMMAND in
    all|test)
        test_all
        ;;
    unit)
        test_unit
        ;;
    integration)
        test_integration
        ;;
    quick)
        test_quick
        ;;
    parallel)
        test_parallel
        ;;
    coverage)
        test_coverage
        ;;
    codecov)
        test_codecov
        ;;
    ci)
        test_ci
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac