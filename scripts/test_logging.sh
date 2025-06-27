#!/bin/bash

# =============================================================================
# Patient Risk Predictor - Logging System Testing
# =============================================================================
# This script provides comprehensive testing for both local and Docker
# execution with different logging levels and configurations.
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
TEST_LOG_DIR="$PROJECT_ROOT/test-logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_section() {
    echo -e "\n${CYAN}--- $1 ---${NC}"
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

print_info() {
    echo -e "${PURPLE}ℹ $1${NC}"
}

check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v curl >/dev/null 2>&1 || missing_deps+=("curl")
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies:"
        echo "  Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}"
        echo "  macOS: brew install ${missing_deps[*]}"
        exit 1
    fi
}

cleanup() {
    print_section "Cleaning up"
    
    # Stop any running processes
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    
    # Clean test logs
    rm -rf "$TEST_LOG_DIR" 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# =============================================================================
# Local Testing Functions
# =============================================================================

test_local_basic() {
    print_section "Testing Local Basic Execution"
    
    mkdir -p "$TEST_LOG_DIR"
    
    # Test with INFO log level
    print_info "Testing with INFO log level..."
    cd "$PROJECT_ROOT"
    
    export LOG_DIR="$TEST_LOG_DIR"
    export LOG_TO_FILE="true"
    
    # Start API server with INFO level in background
    python3 main.py --log-level INFO &
    local api_pid=$!
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    if ! kill -0 $api_pid 2>/dev/null; then
        print_error "API server failed to start"
        return 1
    fi
    
    print_success "API server started with INFO logging (PID: $api_pid)"
    
    # Test health endpoint
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "Health endpoint responding"
    else
        print_error "Health endpoint not responding"
    fi
    
    # Stop server
    kill $api_pid 2>/dev/null || true
    wait $api_pid 2>/dev/null || true
    
    # Check log files
    if [ -f "$TEST_LOG_DIR/patient-risk-predictor.log" ]; then
        local log_entries=$(wc -l < "$TEST_LOG_DIR/patient-risk-predictor.log")
        print_success "Log file created with $log_entries entries"
        
        # Check for INFO level logs
        if grep -q "INFO" "$TEST_LOG_DIR/patient-risk-predictor.log"; then
            print_success "INFO level logs found"
        else
            print_warning "No INFO level logs found"
        fi
    else
        print_error "Log file not created"
        return 1
    fi
    
    rm -rf "$TEST_LOG_DIR"
    print_success "Local basic test completed"
}

test_local_log_levels() {
    print_section "Testing Local Log Levels"
    
    local levels=("ERROR" "WARNING" "INFO" "DEBUG")
    
    for level in "${levels[@]}"; do
        print_info "Testing log level: $level"
        
        mkdir -p "$TEST_LOG_DIR"
        cd "$PROJECT_ROOT"
        
        export LOG_DIR="$TEST_LOG_DIR"
        export LOG_TO_FILE="true"
        
        # Start server with specific log level
        python3 main.py --log-level "$level" &
        local pid=$!
        
        sleep 2
        
        # Make a request to generate logs
        curl -s http://localhost:8000/ > /dev/null || true
        
        # Stop server
        kill $pid 2>/dev/null || true
        wait $pid 2>/dev/null || true
        
        # Check logs
        if [ -f "$TEST_LOG_DIR/patient-risk-predictor.log" ]; then
            local log_count=$(wc -l < "$TEST_LOG_DIR/patient-risk-predictor.log")
            print_success "Log level $level: $log_count log entries"
            
            # Show sample log entry
            if [ $log_count -gt 0 ]; then
                echo "  Sample log: $(head -n 1 "$TEST_LOG_DIR/patient-risk-predictor.log")"
            fi
        else
            print_warning "No log file created for level $level"
        fi
        
        rm -rf "$TEST_LOG_DIR"
        sleep 1
    done
    
    print_success "Log level testing completed"
}

test_local_training() {
    print_section "Testing Local Model Training with Logging"
    
    mkdir -p "$TEST_LOG_DIR"
    cd "$PROJECT_ROOT"
    
    export LOG_DIR="$TEST_LOG_DIR"
    export LOG_TO_FILE="true"
    
    print_info "Starting model training with DEBUG logging..."
    
    if python3 main.py train --log-level DEBUG; then
        print_success "Model training completed"
        
        # Check training logs
        if [ -f "$TEST_LOG_DIR/patient-risk-predictor.log" ]; then
            local training_logs=$(grep -c "training" "$TEST_LOG_DIR/patient-risk-predictor.log" || echo "0")
            print_success "Found $training_logs training-related log entries"
            
            # Show training progress logs
            echo "Training log samples:"
            grep "training" "$TEST_LOG_DIR/patient-risk-predictor.log" | head -3 | sed 's/^/  /'
        else
            print_warning "Training log file not found"
        fi
    else
        print_error "Model training failed"
        return 1
    fi
    
    rm -rf "$TEST_LOG_DIR"
    print_success "Local training test completed"
}

# =============================================================================
# Docker Testing Functions
# =============================================================================

test_docker_basic() {
    print_section "Testing Docker Basic Execution"
    
    cd "$PROJECT_ROOT"
    
    print_info "Building Docker image..."
    if docker build -t patient-risk-predictor-test . > /dev/null 2>&1; then
        print_success "Docker image built successfully"
    else
        print_error "Docker image build failed"
        return 1
    fi
    
    print_info "Starting Docker container with INFO logging..."
    
    # Start container with INFO logging
    docker run -d \
        --name test-container \
        -p 8001:8000 \
        -e LOG_LEVEL=INFO \
        -e ENVIRONMENT=production \
        patient-risk-predictor-test > /dev/null
    
    # Wait for container to start
    sleep 5
    
    # Check if container is running
    if docker ps | grep -q test-container; then
        print_success "Docker container started"
        
        # Test health endpoint
        if curl -s http://localhost:8001/ > /dev/null; then
            print_success "Docker API responding"
        else
            print_warning "Docker API not responding"
        fi
        
        # Check container logs
        local log_output=$(docker logs test-container 2>&1)
        if echo "$log_output" | grep -q "INFO"; then
            print_success "INFO level logs found in container"
        else
            print_warning "No INFO logs found in container"
        fi
        
        # Show sample container logs
        echo "Container log samples:"
        echo "$log_output" | head -5 | sed 's/^/  /'
        
    else
        print_error "Docker container failed to start"
        docker logs test-container || true
        return 1
    fi
    
    # Cleanup
    docker stop test-container > /dev/null 2>&1 || true
    docker rm test-container > /dev/null 2>&1 || true
    docker rmi patient-risk-predictor-test > /dev/null 2>&1 || true
    
    print_success "Docker basic test completed"
}

test_docker_log_levels() {
    print_section "Testing Docker Log Levels"
    
    cd "$PROJECT_ROOT"
    
    # Build image if not exists
    docker build -t patient-risk-predictor-test . > /dev/null 2>&1
    
    local levels=("ERROR" "WARNING" "INFO" "DEBUG")
    local port=8002
    
    for level in "${levels[@]}"; do
        print_info "Testing Docker with log level: $level"
        
        # Start container with specific log level
        docker run -d \
            --name "test-container-$level" \
            -p "$port:8000" \
            -e LOG_LEVEL="$level" \
            -e ENVIRONMENT=production \
            patient-risk-predictor-test > /dev/null
        
        sleep 3
        
        # Make request to generate logs
        curl -s "http://localhost:$port/" > /dev/null || true
        
        # Check logs
        local log_output=$(docker logs "test-container-$level" 2>&1)
        local log_lines=$(echo "$log_output" | wc -l)
        
        print_success "Docker $level: $log_lines log lines"
        
        # Show log sample
        if [ $log_lines -gt 0 ]; then
            echo "  Sample: $(echo "$log_output" | head -n 1)"
        fi
        
        # Cleanup
        docker stop "test-container-$level" > /dev/null 2>&1 || true
        docker rm "test-container-$level" > /dev/null 2>&1 || true
        
        ((port++))
    done
    
    # Final cleanup
    docker rmi patient-risk-predictor-test > /dev/null 2>&1 || true
    
    print_success "Docker log level testing completed"
}

test_docker_compose() {
    print_section "Testing Docker Compose Logging"
    
    cd "$PROJECT_ROOT"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_warning "docker-compose.yml not found, skipping compose test"
        return 0
    fi
    
    print_info "Starting services with docker-compose..."
    
    # Start services
    if docker-compose up -d > /dev/null 2>&1; then
        print_success "Docker Compose services started"
        
        sleep 10
        
        # Check API service logs
        local api_logs=$(docker-compose logs api 2>/dev/null || docker-compose logs patient-risk-predictor 2>/dev/null || echo "No API logs")
        
        if echo "$api_logs" | grep -q "INFO\|ERROR\|WARNING"; then
            print_success "Structured logs found in compose setup"
            echo "Sample compose logs:"
            echo "$api_logs" | head -3 | sed 's/^/  /'
        else
            print_warning "No structured logs found in compose setup"
        fi
        
        # Test API endpoint
        if curl -s http://localhost:8000/ > /dev/null; then
            print_success "Compose API responding"
        else
            print_warning "Compose API not responding"
        fi
        
        # Cleanup
        docker-compose down > /dev/null 2>&1 || true
        
    else
        print_warning "Docker Compose failed to start"
        return 1
    fi
    
    print_success "Docker Compose test completed"
}

# =============================================================================
# Performance Testing
# =============================================================================

test_logging_performance() {
    print_section "Testing Logging Performance Impact"
    
    mkdir -p "$TEST_LOG_DIR"
    cd "$PROJECT_ROOT"
    
    export LOG_DIR="$TEST_LOG_DIR"
    export LOG_TO_FILE="true"
    
    # Test with different log levels and measure performance
    local levels=("ERROR" "INFO" "DEBUG")
    
    for level in "${levels[@]}"; do
        print_info "Performance test with log level: $level"
        
        # Start server
        python3 main.py --log-level "$level" &
        local pid=$!
        
        sleep 3
        
        # Performance test: make multiple requests
        local start_time=$(date +%s.%N)
        
        for i in {1..10}; do
            curl -s http://localhost:8000/ > /dev/null
        done
        
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.0")
        
        print_success "Level $level: 10 requests in ${duration}s"
        
        # Stop server
        kill $pid 2>/dev/null || true
        wait $pid 2>/dev/null || true
        
        # Check log file size
        if [ -f "$TEST_LOG_DIR/patient-risk-predictor.log" ]; then
            local file_size=$(du -h "$TEST_LOG_DIR/patient-risk-predictor.log" | cut -f1)
            print_info "Log file size: $file_size"
        fi
        
        rm -rf "$TEST_LOG_DIR"
        mkdir -p "$TEST_LOG_DIR"
        sleep 1
    done
    
    rm -rf "$TEST_LOG_DIR"
    print_success "Performance testing completed"
}

# =============================================================================
# Main Testing Function
# =============================================================================

run_test_suite() {
    local test_type="$1"
    
    case "$test_type" in
        "local")
            test_local_basic
            test_local_log_levels
            test_local_training
            ;;
        "docker")
            test_docker_basic
            test_docker_log_levels
            test_docker_compose
            ;;
        "performance")
            test_logging_performance
            ;;
        "all")
            test_local_basic
            test_local_log_levels
            test_local_training
            test_docker_basic
            test_docker_log_levels
            test_docker_compose
            test_logging_performance
            ;;
        *)
            echo "Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
}

show_usage() {
    echo "Usage: $0 [TEST_TYPE] [OPTIONS]"
    echo ""
    echo "Test the logging implementation in local and Docker environments"
    echo ""
    echo "Test Types:"
    echo "  local          Test local Python execution with different log levels"
    echo "  docker         Test Docker container execution with logging"
    echo "  performance    Test logging performance impact"
    echo "  all            Run all test suites (default)"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --clean    Clean up before and after testing"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 local              # Test local execution only"
    echo "  $0 docker             # Test Docker execution only"
    echo "  $0 --clean all        # Clean and run all tests"
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local test_type="all"
    local clean_flag=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--clean)
                clean_flag=true
                shift
                ;;
            local|docker|performance|all)
                test_type="$1"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Print header
    print_header "PATIENT RISK PREDICTOR - LOGGING SYSTEM TESTING"
    
    # Check dependencies
    check_dependencies
    
    # Clean up if requested
    if [ "$clean_flag" = true ]; then
        cleanup
    fi
    
    # Show current configuration
    print_info "Project root: $PROJECT_ROOT"
    print_info "Test type: $test_type"
    print_info "Clean flag: $clean_flag"
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    # Run the test suite
    echo ""
    if run_test_suite "$test_type"; then
        print_success "All tests completed successfully"
    else
        print_error "Some tests failed"
        exit 1
    fi
    
    # Final message
    echo ""
    print_header "TESTING COMPLETED"
    print_info "Logging system tested across different environments and configurations"
    print_info "Check individual test results above for detailed information"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi