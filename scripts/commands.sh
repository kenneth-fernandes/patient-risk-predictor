#!/bin/bash
# Main command script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}               PATIENT RISK PREDICTOR                       ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${YELLOW}                   COMMAND CENTER                             ${NC}${CYAN}║${NC}"
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

# Function to print info messages
print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Show all available commands
show_all_commands() {
    print_header
    
    print_section "🛠️  SETUP & INSTALLATION"
    echo -e "${WHITE}${BOLD}./scripts/setup.sh${NC}"
    echo -e "  ${GREEN}install${NC}           Install production dependencies"
    echo -e "  ${GREEN}install-dev${NC}       Install development dependencies"
    echo -e "  ${GREEN}dev-setup${NC}         Complete development environment setup"
    echo ""
    
    print_section "🧪 TESTING"
    echo -e "${WHITE}${BOLD}./scripts/test.sh${NC}"
    echo -e "  ${GREEN}all${NC}               Run all tests with coverage"
    echo -e "  ${GREEN}unit${NC}              Run unit tests only"
    echo -e "  ${GREEN}integration${NC}       Run integration tests only"
    echo -e "  ${GREEN}quick${NC}             Run tests without coverage (faster)"
    echo -e "  ${GREEN}coverage${NC}          Generate detailed coverage report"
    echo ""
    
    print_section "🔍 CODE QUALITY"
    echo -e "${WHITE}${BOLD}./scripts/quality.sh${NC}"
    echo -e "  ${GREEN}all${NC}               Run all quality checks"
    echo -e "  ${GREEN}lint${NC}              Run linting (flake8)"
    echo -e "  ${GREEN}format${NC}            Format code (black)"
    echo -e "  ${GREEN}security${NC}          Run security checks"
    echo ""
    
    print_section "🐳 DOCKER"
    echo -e "${WHITE}${BOLD}./scripts/docker.sh${NC}"
    echo -e "  ${GREEN}up${NC}                Start all services"
    echo -e "  ${GREEN}down${NC}              Stop all services"
    echo -e "  ${GREEN}build${NC}             Build Docker images"
    echo -e "  ${GREEN}logs${NC}              Show service logs"
    echo -e "  ${GREEN}train${NC}             Run model training in Docker"
    echo ""
    
    print_section "🧹 CLEANUP"
    echo -e "${WHITE}${BOLD}./scripts/clean.sh${NC}"
    echo -e "  ${GREEN}basic${NC}             Clean temporary files"
    echo -e "  ${GREEN}all${NC}               Clean everything including data"
    echo -e "  ${GREEN}docker${NC}            Clean Docker resources"
    echo ""
    
    print_section "🚀 APPLICATION"
    echo -e "${WHITE}${BOLD}./scripts/run_local.sh${NC}"
    echo -e "  ${GREEN}full${NC}              Train model and run API"
    echo -e "  ${GREEN}api${NC}               Run API only"
    echo -e "  ${GREEN}train${NC}             Train model only"
    echo ""
    
    print_section "📝 COMMON WORKFLOWS"
    echo -e "${YELLOW}${BOLD}Development Workflow:${NC}"
    echo -e "  ${CYAN}./scripts/setup.sh dev-setup${NC}     ${WHITE}# Setup environment${NC}"
    echo -e "  ${CYAN}./scripts/test.sh quick${NC}          ${WHITE}# Quick test${NC}"
    echo -e "  ${CYAN}./scripts/quality.sh format${NC}      ${WHITE}# Format code${NC}"
    echo -e "  ${CYAN}./scripts/run_local.sh${NC}           ${WHITE}# Run application${NC}"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Before Committing:${NC}"
    echo -e "  ${CYAN}./scripts/test.sh${NC}                ${WHITE}# Run all tests${NC}"
    echo -e "  ${CYAN}./scripts/quality.sh${NC}             ${WHITE}# Check code quality${NC}"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Production Deployment:${NC}"
    echo -e "  ${CYAN}./scripts/docker.sh up${NC}           ${WHITE}# Start with Docker${NC}"
    echo -e "  ${CYAN}./scripts/docker.sh train${NC}        ${WHITE}# Train model${NC}"
    echo ""
    
    print_info "Run any script with '--help' to see detailed options"
    print_info "Example: ./scripts/test.sh --help"
    echo ""
}

# Quick development check
quick_check() {
    print_section "⚡ QUICK DEVELOPMENT CHECK"
    
    print_info "Running quick tests..."
    ./scripts/test.sh quick
    
    if [ $? -eq 0 ]; then
        print_info "Running code quality checks..."
        ./scripts/quality.sh lint
        
        if [ $? -eq 0 ]; then
            print_success "Everything looks good! 🎉"
        else
            print_info "Code quality issues found - run: ./scripts/quality.sh format"
        fi
    else
        print_info "Tests failed - check the output above"
    fi
}

# Complete development check
full_check() {
    print_section "🔍 COMPLETE DEVELOPMENT CHECK"
    
    print_info "Running all tests..."
    ./scripts/test.sh
    
    if [ $? -eq 0 ]; then
        print_info "Running all quality checks..."
        ./scripts/quality.sh
        
        if [ $? -eq 0 ]; then
            print_success "All checks passed! Ready to commit 🚀"
        else
            print_info "Quality issues found - fix them before committing"
        fi
    else
        print_info "Tests failed - fix them before proceeding"
    fi
}

# Main script logic
COMMAND=${1:-help}

case $COMMAND in
    help|--help|-h|"")
        show_all_commands
        ;;
    quick)
        quick_check
        ;;
    full)
        full_check
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_all_commands
        exit 1
        ;;
esac