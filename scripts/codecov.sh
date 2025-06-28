#!/bin/bash
# Codecov coverage testing script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}                   CODECOV TESTING                          ${NC}${CYAN}║${NC}"
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
    print_section "CODECOV TESTING COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}test${NC}              Run tests and generate Codecov-compatible coverage ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${GREEN}upload${NC}            Upload coverage to Codecov (requires CODECOV_TOKEN)"
    echo -e "  ${GREEN}local${NC}             Generate local coverage report for Codecov validation"
    echo -e "  ${GREEN}validate${NC}          Validate coverage data for Codecov compatibility"
    echo -e "  ${GREEN}ci${NC}                Run full CI pipeline with Codecov upload"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Environment Variables:${NC}"
    echo -e "  ${PURPLE}CODECOV_TOKEN${NC}     Your Codecov upload token (for upload command)"
    echo -e "  ${PURPLE}CI${NC}                Set to 'true' in CI environments"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0${NC}                ${WHITE}# Run tests and generate coverage${NC}"
    echo -e "  ${CYAN}$0 test${NC}           ${WHITE}# Same as above${NC}"
    echo -e "  ${CYAN}$0 local${NC}          ${WHITE}# Generate local coverage report${NC}"
    echo -e "  ${CYAN}$0 validate${NC}       ${WHITE}# Validate coverage data${NC}"
    echo -e "  ${CYAN}CODECOV_TOKEN=xxx $0 upload${NC}  ${WHITE}# Upload to Codecov${NC}"
    echo ""
}

# Check if coverage tools are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check pytest-cov
    if ! python -c "import pytest_cov" 2>/dev/null; then
        missing_deps+=("pytest-cov")
    fi
    
    # Check coverage
    if ! python -c "import coverage" 2>/dev/null; then
        missing_deps+=("coverage")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Install with: pip install ${missing_deps[*]}"
        exit 1
    fi
    
    print_success "All dependencies available"
}

# Run tests and generate Codecov-compatible coverage
test_codecov() {
    print_section "🧪 CODECOV COVERAGE TESTING"
    check_dependencies
    
    print_info "Running tests with Codecov-compatible coverage..."
    
    # Create reports directory
    mkdir -p reports/coverage
    
    # Run tests with coverage
    python -m pytest \
        --cov=src \
        --cov-report=xml:coverage.xml \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-config=.coveragerc \
        tests/
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Tests completed successfully!"
        print_info "Coverage XML (Codecov format): coverage.xml"
        print_info "Coverage HTML: htmlcov/index.html"
        
        # Show coverage summary
        if [ -f "coverage.xml" ]; then
            print_section "📊 COVERAGE SUMMARY"
            python -m coverage report --show-missing
        fi
    else
        print_error "Tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Generate local coverage report
test_local() {
    print_section "🏠 LOCAL COVERAGE TESTING"
    check_dependencies
    
    print_info "Generating local coverage report..."
    
    # Run tests with detailed coverage
    python -m pytest \
        --cov=src \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml:coverage.xml \
        tests/
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Local coverage report generated!"
        echo ""
        print_info "View detailed coverage report:"
        echo -e "  ${CYAN}open htmlcov/index.html${NC}"
        echo ""
        print_info "Coverage XML for Codecov: coverage.xml"
        
        # Show basic coverage stats
        if command -v coverage &> /dev/null; then
            echo ""
            print_section "📈 COVERAGE STATISTICS"
            coverage report --show-missing
        fi
    else
        print_error "Coverage generation failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Validate coverage data
validate_coverage() {
    print_section "✅ COVERAGE VALIDATION"
    
    if [ ! -f "coverage.xml" ]; then
        print_warning "No coverage.xml found, generating..."
        test_codecov
    fi
    
    print_info "Validating coverage data for Codecov compatibility..."
    
    # Check if coverage.xml exists and is valid
    if [ -f "coverage.xml" ]; then
        # Basic XML validation
        if python -c "import xml.etree.ElementTree as ET; ET.parse('coverage.xml')" 2>/dev/null; then
            print_success "Coverage XML is valid"
            
            # Show file size
            local file_size=$(wc -c < coverage.xml)
            print_info "Coverage file size: ${file_size} bytes"
            
            # Show number of covered files
            local covered_files=$(grep -c '<class' coverage.xml 2>/dev/null || echo "0")
            print_info "Number of covered files: ${covered_files}"
            
        else
            print_error "Coverage XML is malformed"
            exit 1
        fi
    else
        print_error "Coverage XML not found"
        exit 1
    fi
    
    print_success "Coverage data is valid for Codecov"
}

# Upload coverage to Codecov
upload_codecov() {
    print_section "☁️  CODECOV UPLOAD"
    
    # Check if coverage file exists
    if [ ! -f "coverage.xml" ]; then
        print_warning "No coverage.xml found, generating..."
        test_codecov
    fi
    
    # Validate first
    validate_coverage
    
    # Check for Codecov token
    if [ -z "$CODECOV_TOKEN" ]; then
        print_warning "CODECOV_TOKEN not set"
        print_info "Upload may work without token for public repositories"
        print_info "For private repos, set: export CODECOV_TOKEN=your_token"
    else
        print_success "CODECOV_TOKEN is set"
    fi
    
    # Check if codecov CLI is available
    if command -v codecov &> /dev/null; then
        print_info "Using codecov CLI..."
        codecov -f coverage.xml
    elif command -v curl &> /dev/null; then
        print_info "Using curl to upload to Codecov..."
        
        # Get commit info
        local commit_sha=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        
        print_info "Commit: ${commit_sha:0:8}"
        print_info "Branch: ${branch}"
        
        # Upload using bash uploader
        curl -s https://codecov.io/bash | bash -s -- -f coverage.xml
    else
        print_error "Neither codecov CLI nor curl available"
        print_info "Install codecov CLI with: pip install codecov"
        exit 1
    fi
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Coverage uploaded to Codecov!"
    else
        print_error "Codecov upload failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Run CI pipeline with Codecov
test_ci() {
    print_section "🤖 CI CODECOV PIPELINE"
    
    print_info "Running complete CI pipeline with Codecov integration..."
    
    # Set CI environment
    export CI=true
    
    # Run tests with coverage
    test_codecov
    
    # Validate coverage
    validate_coverage
    
    # Upload if token is available or if running in CI
    if [ ! -z "$CODECOV_TOKEN" ] || [ "$CI" = "true" ]; then
        upload_codecov
    else
        print_warning "Skipping upload (no CODECOV_TOKEN and not in CI)"
        print_info "Coverage data is ready at: coverage.xml"
    fi
    
    print_success "CI Codecov pipeline completed!"
}

# Main script logic
print_header

COMMAND=${1:-test}

case $COMMAND in
    test|coverage)
        test_codecov
        ;;
    local)
        test_local
        ;;
    validate)
        validate_coverage
        ;;
    upload)
        upload_codecov
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