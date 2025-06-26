#!/bin/bash
# Docker utilities script for Patient Risk Predictor

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
    echo -e "${CYAN}║${WHITE}${BOLD}                 DOCKER UTILITIES                           ${NC}${CYAN}║${NC}"
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
    print_section "DOCKER COMMANDS"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Available Commands:${NC}"
    echo -e "  ${GREEN}up${NC}                Start all services ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${GREEN}down${NC}              Stop all services"
    echo -e "  ${GREEN}build${NC}             Build Docker images"
    echo -e "  ${GREEN}rebuild${NC}           Rebuild images from scratch"
    echo -e "  ${GREEN}logs${NC}              Show service logs"
    echo -e "  ${GREEN}status${NC}            Show service status"
    echo -e "  ${GREEN}train${NC}             Run model training in Docker"
    echo -e "  ${GREEN}clean${NC}             Clean Docker resources"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0 up${NC}             ${WHITE}# Start all services${NC}"
    echo -e "  ${CYAN}$0 logs api${NC}       ${WHITE}# Show API logs${NC}"
    echo -e "  ${CYAN}$0 rebuild${NC}        ${WHITE}# Rebuild from scratch${NC}"
    echo ""
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Start Docker services
docker_up() {
    print_section "🚀 STARTING DOCKER SERVICES"
    check_docker
    
    print_info "Starting services with Docker Compose..."
    docker-compose up --build -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully!"
        echo ""
        print_info "Service URLs:"
        echo -e "  ${CYAN}API:${NC} http://localhost:8000"
        echo -e "  ${CYAN}MLflow UI:${NC} http://localhost:5001"
        echo ""
        print_info "Use '$0 logs' to view logs"
        print_info "Use '$0 status' to check service health"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Stop Docker services
docker_down() {
    print_section "🛑 STOPPING DOCKER SERVICES"
    check_docker
    
    print_info "Stopping services..."
    docker-compose down -v
    
    if [ $? -eq 0 ]; then
        print_success "Services stopped successfully!"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Build Docker images
docker_build() {
    print_section "🔨 BUILDING DOCKER IMAGES"
    check_docker
    
    print_info "Building Docker images..."
    docker-compose build
    
    if [ $? -eq 0 ]; then
        print_success "Images built successfully!"
    else
        print_error "Failed to build images"
        exit 1
    fi
}

# Rebuild Docker images from scratch
docker_rebuild() {
    print_section "🔄 REBUILDING DOCKER IMAGES"
    check_docker
    
    print_info "Stopping services..."
    docker-compose down -v
    
    print_info "Removing existing images..."
    docker-compose build --no-cache
    
    print_info "Starting services with new images..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services rebuilt and started successfully!"
    else
        print_error "Failed to rebuild services"
        exit 1
    fi
}

# Show Docker logs
docker_logs() {
    print_section "📋 SERVICE LOGS"
    check_docker
    
    local service=${1:-""}
    
    if [ -z "$service" ]; then
        print_info "Showing logs for all services..."
        docker-compose logs -f
    else
        print_info "Showing logs for service: $service"
        docker-compose logs -f "$service"
    fi
}

# Show service status
docker_status() {
    print_section "📊 SERVICE STATUS"
    check_docker
    
    print_info "Service status:"
    docker-compose ps
    
    echo ""
    print_info "Health checks:"
    
    # Check API health
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        print_success "API is responding"
    else
        print_warning "API is not responding"
    fi
    
    # Check MLflow health
    if curl -s http://localhost:5001/ >/dev/null 2>&1; then
        print_success "MLflow UI is responding"
    else
        print_warning "MLflow UI is not responding"
    fi
}

# Run model training in Docker
docker_train() {
    print_section "🤖 TRAINING MODEL IN DOCKER"
    check_docker
    
    print_info "Running model training..."
    docker-compose --profile training up trainer
    
    if [ $? -eq 0 ]; then
        print_success "Model training completed!"
    else
        print_error "Model training failed"
        exit 1
    fi
}

# Clean Docker resources
docker_clean() {
    print_section "🧹 CLEANING DOCKER RESOURCES"
    check_docker
    
    print_warning "This will remove all containers, volumes, and unused images!"
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping services..."
        docker-compose down -v
        
        print_info "Pruning Docker system..."
        docker system prune -a -f
        
        print_success "Docker resources cleaned!"
    else
        print_info "Docker cleanup cancelled"
    fi
}

# Main script logic
COMMAND=${1:-up}

case $COMMAND in
    up|start)
        docker_up
        ;;
    down|stop)
        docker_down
        ;;
    build)
        docker_build
        ;;
    rebuild)
        docker_rebuild
        ;;
    logs)
        docker_logs $2
        ;;
    status)
        docker_status
        ;;
    train)
        docker_train
        ;;
    clean)
        docker_clean
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