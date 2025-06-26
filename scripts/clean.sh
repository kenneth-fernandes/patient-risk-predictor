#!/bin/bash
# Cleanup script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}                 CLEANUP UTILITIES                          ${NC}${CYAN}║${NC}"
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
    print_section "CLEANUP COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}basic${NC}             Clean temporary files ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${GREEN}all${NC}               Clean everything including data"
    echo -e "  ${GREEN}python${NC}            Clean Python cache files"
    echo -e "  ${GREEN}test${NC}              Clean test artifacts"
    echo -e "  ${GREEN}docker${NC}            Clean Docker resources"
    echo -e "  ${GREEN}mlflow${NC}            Clean MLflow data"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0${NC}                ${WHITE}# Basic cleanup${NC}"
    echo -e "  ${CYAN}$0 all${NC}            ${WHITE}# Complete cleanup${NC}"
    echo -e "  ${CYAN}$0 docker${NC}         ${WHITE}# Clean Docker only${NC}"
    echo ""
}

# Clean Python cache files
clean_python() {
    print_section "🐍 CLEANING PYTHON CACHE"
    print_info "Removing Python cache files..."
    
    # Remove .pyc files
    find . -type f -name "*.pyc" -delete 2>/dev/null
    print_success "Removed .pyc files"
    
    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    print_success "Removed __pycache__ directories"
    
    # Remove .egg-info directories
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
    print_success "Removed .egg-info directories"
}

# Clean test artifacts
clean_test() {
    print_section "🧪 CLEANING TEST ARTIFACTS"
    print_info "Removing test artifacts..."
    
    # Remove pytest cache
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache/
        print_success "Removed .pytest_cache"
    fi
    
    # Remove coverage files
    if [ -f ".coverage" ]; then
        rm -f .coverage
        print_success "Removed .coverage file"
    fi
    
    # Remove coverage reports
    if [ -d "htmlcov" ]; then
        rm -rf htmlcov/
        print_success "Removed htmlcov directory"
    fi
    
    # Remove test result files
    rm -f test-results*.xml coverage.xml 2>/dev/null
    print_success "Removed test result files"
    
    # Remove bandit reports
    rm -f bandit-report.json 2>/dev/null
    print_success "Removed security report files"
}

# Clean basic temporary files
clean_basic() {
    print_section "🧹 BASIC CLEANUP"
    print_info "Cleaning temporary files..."
    
    clean_python
    clean_test
    
    print_success "Basic cleanup completed!"
}

# Clean MLflow data
clean_mlflow() {
    print_section "📊 CLEANING MLFLOW DATA"
    print_warning "This will remove all MLflow experiments and models!"
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "mlruns" ]; then
            rm -rf mlruns/
            print_success "Removed mlruns directory"
        fi
        
        if [ -f "mlflow.db" ]; then
            rm -f mlflow.db
            print_success "Removed mlflow.db"
        fi
        
        print_success "MLflow data cleaned!"
    else
        print_info "MLflow cleanup cancelled"
    fi
}

# Clean Docker resources
clean_docker() {
    print_section "🐳 CLEANING DOCKER RESOURCES"
    print_info "Cleaning Docker resources..."
    
    # Stop and remove containers
    if command -v docker-compose &> /dev/null; then
        print_info "Stopping Docker Compose services..."
        docker-compose down -v 2>/dev/null
        print_success "Docker Compose services stopped"
    fi
    
    # Prune Docker system
    if command -v docker &> /dev/null; then
        print_info "Pruning Docker system..."
        docker system prune -f 2>/dev/null
        print_success "Docker system pruned"
    else
        print_warning "Docker not found, skipping Docker cleanup"
    fi
}

# Clean logs
clean_logs() {
    print_section "📝 CLEANING LOGS"
    print_info "Cleaning log files..."
    
    if [ -d "logs" ]; then
        rm -rf logs/*.log 2>/dev/null
        print_success "Removed log files"
    fi
}

# Clean everything
clean_all() {
    print_section "🗑️  COMPLETE CLEANUP"
    print_warning "This will remove ALL temporary files, data, and Docker resources!"
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        clean_basic
        clean_mlflow
        clean_docker
        clean_logs
        
        print_success "Complete cleanup finished! 🎉"
    else
        print_info "Complete cleanup cancelled"
    fi
}

# Main script logic
COMMAND=${1:-basic}

case $COMMAND in
    basic|clean)
        clean_basic
        ;;
    all)
        clean_all
        ;;
    python)
        clean_python
        ;;
    test)
        clean_test
        ;;
    docker)
        clean_docker
        ;;
    mlflow)
        clean_mlflow
        ;;
    logs)
        clean_logs
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