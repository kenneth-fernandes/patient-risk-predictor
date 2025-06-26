#!/bin/bash
# Code quality script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}                 CODE QUALITY TOOLS                         ${NC}${CYAN}║${NC}"
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
    print_section "CODE QUALITY COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}all${NC}               Run all quality checks ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${GREEN}lint${NC}              Run linting (flake8)"
    echo -e "  ${GREEN}format${NC}            Format code (black)"
    echo -e "  ${GREEN}format-check${NC}      Check code formatting"
    echo -e "  ${GREEN}type-check${NC}        Run type checking (mypy)"
    echo -e "  ${GREEN}security${NC}          Run security checks"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0${NC}                ${WHITE}# Run all quality checks${NC}"
    echo -e "  ${CYAN}$0 lint${NC}           ${WHITE}# Run linting only${NC}"
    echo -e "  ${CYAN}$0 format${NC}         ${WHITE}# Format code${NC}"
    echo -e "  ${CYAN}$0 security${NC}       ${WHITE}# Security checks${NC}"
    echo ""
}

# Check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_warning "$1 is not installed. Run: pip install -r requirements.txt"
        return 1
    fi
    return 0
}

# Run linting
run_lint() {
    print_section "🔍 LINTING CODE"
    print_info "Running flake8 linting..."
    
    if ! check_command flake8; then
        return 1
    fi
    
    flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Linting passed!"
    else
        print_error "Linting failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Format code
run_format() {
    print_section "✨ FORMATTING CODE"
    print_info "Formatting code with black and isort..."
    
    if ! check_command black; then
        return 1
    fi
    
    if ! check_command isort; then
        print_warning "isort not installed, skipping import sorting"
        black src/ tests/ --line-length=100
    else
        black src/ tests/ --line-length=100
        isort src/ tests/ --profile black
    fi
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Code formatting completed!"
    else
        print_error "Code formatting failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Check code formatting
check_format() {
    print_section "🔍 CHECKING CODE FORMAT"
    print_info "Checking code formatting..."
    
    if ! check_command black; then
        return 1
    fi
    
    black --check --line-length=100 src/ tests/
    local black_exit=$?
    
    if command -v isort &> /dev/null; then
        isort --check-only --profile black src/ tests/
        local isort_exit=$?
    else
        print_warning "isort not installed, skipping import sort check"
        local isort_exit=0
    fi
    
    if [ $black_exit -eq 0 ] && [ $isort_exit -eq 0 ]; then
        print_success "Code formatting is correct!"
    else
        print_error "Code formatting issues found"
        print_info "Run: $0 format to fix formatting issues"
        return 1
    fi
}

# Run type checking
run_type_check() {
    print_section "📝 TYPE CHECKING"
    print_info "Running mypy type checking..."
    
    if ! check_command mypy; then
        return 1
    fi
    
    mypy src/ --ignore-missing-imports
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Type checking passed!"
    else
        print_error "Type checking failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Run security checks
run_security() {
    print_section "🔒 SECURITY CHECKS"
    print_info "Running security checks..."
    
    local overall_success=0
    
    # Safety check
    if check_command safety; then
        print_info "Running safety scan for known vulnerabilities..."
        safety check --continue-on-error
        if [ $? -ne 0 ]; then
            print_warning "Safety scan found issues"
            overall_success=1
        else
            print_success "Safety scan passed!"
        fi
    else
        print_warning "Safety not installed, skipping vulnerability check"
    fi
    
    # Bandit check
    if check_command bandit; then
        print_info "Running bandit security linter..."
        mkdir -p reports/security
        bandit -r src/ -f json > reports/security/bandit-report.json 2>/dev/null
        if [ $? -ne 0 ]; then
            print_warning "Bandit found security issues (see reports/security/bandit-report.json)"
            overall_success=1
        else
            print_success "Bandit security check passed!"
            rm -f reports/security/bandit-report.json
        fi
    else
        print_warning "Bandit not installed, skipping security linting"
    fi
    
    if [ $overall_success -eq 0 ]; then
        print_success "All security checks passed!"
    fi
    
    return $overall_success
}

# Run all quality checks
run_all() {
    print_section "🏆 RUNNING ALL QUALITY CHECKS"
    print_info "Running complete quality check suite..."
    
    local overall_success=0
    
    # Run linting
    run_lint
    if [ $? -ne 0 ]; then
        overall_success=1
    fi
    
    # Check formatting
    check_format
    if [ $? -ne 0 ]; then
        overall_success=1
    fi
    
    # Run type checking
    run_type_check
    if [ $? -ne 0 ]; then
        overall_success=1
    fi
    
    # Run security checks
    run_security
    if [ $? -ne 0 ]; then
        overall_success=1
    fi
    
    echo ""
    if [ $overall_success -eq 0 ]; then
        print_success "All quality checks passed! 🎉"
    else
        print_error "Some quality checks failed"
        print_info "Fix the issues above and run again"
        exit 1
    fi
}

# Main script logic
COMMAND=${1:-all}

case $COMMAND in
    all|quality)
        run_all
        ;;
    lint)
        run_lint
        ;;
    format)
        run_format
        ;;
    format-check)
        check_format
        ;;
    type-check)
        run_type_check
        ;;
    security)
        run_security
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