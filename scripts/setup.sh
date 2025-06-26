#!/bin/bash
# Setup script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}                   SETUP UTILITIES                           ${NC}${CYAN}║${NC}"
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

# Function to show usage
show_usage() {
    print_header
    print_section "SETUP COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}install${NC}           Install production dependencies"
    echo -e "  ${GREEN}install-dev${NC}       Install development dependencies"
    echo -e "  ${GREEN}install-test${NC}      Install testing dependencies only"
    echo -e "  ${GREEN}ci-setup${NC}          Setup CI environment"
    echo -e "  ${GREEN}dev-setup${NC}         Complete development setup"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0 install${NC}        ${WHITE}# Install basic dependencies${NC}"
    echo -e "  ${CYAN}$0 install-dev${NC}    ${WHITE}# Install everything for development${NC}"
    echo -e "  ${CYAN}$0 dev-setup${NC}      ${WHITE}# Complete development environment${NC}"
    echo ""
}

# Install production dependencies
install_basic() {
    print_section "📦 INSTALLING PRODUCTION DEPENDENCIES"
    print_info "Installing basic application dependencies..."
    
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Production dependencies installed successfully!"
    else
        print_error "Failed to install production dependencies"
        exit 1
    fi
}

# Install development dependencies
install_dev() {
    print_section "🛠️  INSTALLING DEVELOPMENT DEPENDENCIES"
    print_info "Installing all dependencies (production + development)..."
    
    # Install all dependencies from single file
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Development dependencies installed successfully!"
    else
        print_error "Failed to install development dependencies"
        exit 1
    fi
}

# Install testing dependencies only
install_test() {
    print_section "🧪 INSTALLING TESTING DEPENDENCIES"
    print_info "Installing all dependencies (includes testing tools)..."
    
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Testing dependencies installed successfully!"
    else
        print_error "Failed to install testing dependencies"
        exit 1
    fi
}

# Setup CI environment
ci_setup() {
    print_section "🤖 CI ENVIRONMENT SETUP"
    print_info "Setting up CI environment..."
    
    # Install all dependencies
    install_dev
    
    # Create necessary directories
    print_info "Creating required directories..."
    mkdir -p /tmp/test_mlruns
    mkdir -p logs
    mkdir -p htmlcov
    
    print_success "CI environment setup completed!"
}

# Complete development setup
dev_setup() {
    print_section "🚀 DEVELOPMENT ENVIRONMENT SETUP"
    print_info "Setting up complete development environment..."
    
    # Install development dependencies
    install_dev
    
    # Create necessary directories
    print_info "Creating project directories..."
    mkdir -p logs
    mkdir -p htmlcov
    
    print_success "Development environment setup complete!"
    echo ""
    print_info "Next steps:"
    echo -e "  ${CYAN}./scripts/test.sh${NC}        ${WHITE}# Run tests to verify setup${NC}"
    echo -e "  ${CYAN}./scripts/run_local.sh${NC}   ${WHITE}# Start the application${NC}"
    echo ""
}

# Main script logic
COMMAND=${1:-help}

case $COMMAND in
    install)
        install_basic
        ;;
    install-dev)
        install_dev
        ;;
    install-test)
        install_test
        ;;
    ci-setup)
        ci_setup
        ;;
    dev-setup)
        dev_setup
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