#!/bin/bash

# =============================================================================
# Patient Risk Predictor - Logging System Demonstration
# =============================================================================
# This script demonstrates the comprehensive logging capabilities of the
# Patient Risk Predictor application including structured logging, error
# tracking, and performance monitoring.
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Use configurable log directory
DEFAULT_LOG_DIR="$PROJECT_ROOT/logs"
LOG_DIR="${LOG_DIR:-$DEFAULT_LOG_DIR}"
DEMO_LOG="$LOG_DIR/logging-demo.log"

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
    command -v jq >/dev/null 2>&1 || missing_deps+=("jq")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies:"
        echo "  Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}"
        echo "  macOS: brew install ${missing_deps[*]}"
        exit 1
    fi
}

setup_environment() {
    print_section "Setting up environment"
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    print_success "Created logs directory: $LOG_DIR"
    
    # Set environment variables for demo
    export ENVIRONMENT="development"
    export LOG_LEVEL="DEBUG"
    export ENABLE_STRUCTURED_LOGGING="false"
    export LOG_TO_FILE="true"
    export LOG_DIR="$LOG_DIR"
    
    print_info "Environment variables set:"
    print_info "  ENVIRONMENT=$ENVIRONMENT"
    print_info "  LOG_LEVEL=$LOG_LEVEL"
    print_info "  ENABLE_STRUCTURED_LOGGING=$ENABLE_STRUCTURED_LOGGING"
    print_info "  LOG_TO_FILE=$LOG_TO_FILE"
    print_info "  LOG_DIR=$LOG_DIR"
}

# =============================================================================
# Logging Demonstrations
# =============================================================================

demo_basic_logging() {
    print_section "Basic Logging Demonstration"
    
    echo "Testing basic logging functionality..."
    
    # Create a simple Python script to test logging
    cat > "$PROJECT_ROOT/temp_logging_test.py" << 'EOF'
import sys
import os
sys.path.insert(0, '.')
from src.utils.logging_config import get_logger, setup_application_logging

setup_application_logging()
logger = get_logger(__name__)

# Test different log levels
logger.debug("This is a DEBUG message - detailed debugging information")
logger.info("This is an INFO message - general operational information")  
logger.warning("This is a WARNING message - potential issues detected")
logger.error("This is an ERROR message - error condition occurred")

# Test structured logging
logger.info(
    "Structured logging example",
    extra={
        "event": "demo_event",
        "user_id": "demo_user_123",
        "operation": "basic_logging_test",
        "success": True,
        "processing_time_ms": 42
    }
)

print("Basic logging test completed successfully!")
EOF

    # Run the test
    cd "$PROJECT_ROOT"
    if python3 temp_logging_test.py; then
        print_success "Basic logging test passed"
    else
        print_error "Basic logging test failed"
        return 1
    fi
    
    # Clean up
    rm -f temp_logging_test.py
}

demo_api_logging() {
    print_section "API Request Logging Demonstration"
    
    echo "Starting API server for logging demonstration..."
    
    # Start the API server in background
    cd "$PROJECT_ROOT"
    python3 main.py &
    API_PID=$!
    
    # Wait for server to start
    echo "Waiting for API server to start..."
    sleep 5
    
    # Check if server is running
    if ! kill -0 $API_PID 2>/dev/null; then
        print_error "API server failed to start"
        return 1
    fi
    
    print_success "API server started (PID: $API_PID)"
    
    # Test health check endpoint
    echo "Testing health check endpoint..."
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "Health check endpoint responding"
    else
        print_warning "Health check endpoint not responding"
    fi
    
    # Test prediction endpoint with valid data
    echo "Testing prediction endpoint with valid data..."
    prediction_response=$(curl -s -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{
            "age": 45,
            "sex": 1,
            "cp": 2,
            "trestbps": 130,
            "chol": 200,
            "fbs": 0,
            "restecg": 1,
            "thalach": 175,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 1,
            "ca": 0,
            "thal": 2
        }')
    
    if [ $? -eq 0 ]; then
        print_success "Prediction request successful"
        print_info "Response: $prediction_response"
    else
        print_warning "Prediction request failed"
    fi
    
    # Test prediction endpoint with invalid data to generate error logs
    echo "Testing prediction endpoint with invalid data..."
    error_response=$(curl -s -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{
            "age": "invalid",
            "sex": 1
        }' || true)
    
    if [ $? -eq 0 ]; then
        print_success "Error handling test completed"
    fi
    
    # Stop the API server
    echo "Stopping API server..."
    kill $API_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    print_success "API server stopped"
}

demo_model_training_logging() {
    print_section "Model Training Logging Demonstration"
    
    echo "Running model training to demonstrate ML operation logging..."
    
    cd "$PROJECT_ROOT"
    if python3 main.py train; then
        print_success "Model training completed successfully"
    else
        print_warning "Model training encountered issues (check logs)"
    fi
}

demo_structured_logging() {
    print_section "Structured JSON Logging Demonstration"
    
    echo "Testing structured JSON logging format..."
    
    # Set environment for JSON logging
    export ENABLE_STRUCTURED_LOGGING="true"
    export ENVIRONMENT="production"
    
    # Create test script for JSON logging
    cat > "$PROJECT_ROOT/temp_json_test.py" << 'EOF'
import sys
import time
sys.path.insert(0, '.')
from src.utils.logging_config import get_logger, setup_application_logging, set_correlation_id

setup_application_logging()
logger = get_logger(__name__)

# Set correlation ID
correlation_id = set_correlation_id("json-demo-001")

# Test JSON structured logging
logger.info(
    "JSON logging demonstration",
    extra={
        "event": "json_demo_start",
        "environment": "production",
        "features_tested": ["correlation_id", "structured_format", "performance_metrics"],
        "timestamp": time.time()
    }
)

# Simulate some processing
time.sleep(0.1)

logger.info(
    "Processing completed",
    extra={
        "event": "json_demo_complete",
        "status": "success",
        "processing_duration_ms": 100,
        "items_processed": 42
    }
)

print("JSON logging test completed!")
EOF

    # Run JSON test
    if python3 temp_json_test.py; then
        print_success "JSON logging test passed"
    else
        print_error "JSON logging test failed"
    fi
    
    # Reset environment
    export ENABLE_STRUCTURED_LOGGING="false"
    export ENVIRONMENT="development"
    
    # Clean up
    rm -f temp_json_test.py
}

# =============================================================================
# Log Analysis Functions
# =============================================================================

analyze_logs() {
    print_section "Log Analysis"
    
    if [ ! -f "$LOG_DIR/patient-risk-predictor.log" ]; then
        print_warning "No log file found at $LOG_DIR/patient-risk-predictor.log"
        return
    fi
    
    local log_file="$LOG_DIR/patient-risk-predictor.log"
    
    echo "Analyzing generated logs..."
    
    # Count log entries by level
    echo "Log entries by level:"
    grep -o '"level":"[^"]*"' "$log_file" 2>/dev/null | sort | uniq -c | sed 's/^/  /' || {
        echo "  DEBUG: $(grep -c "DEBUG" "$log_file" 2>/dev/null || echo 0)"
        echo "  INFO: $(grep -c "INFO" "$log_file" 2>/dev/null || echo 0)"
        echo "  WARNING: $(grep -c "WARNING" "$log_file" 2>/dev/null || echo 0)"
        echo "  ERROR: $(grep -c "ERROR" "$log_file" 2>/dev/null || echo 0)"
    }
    
    # Show correlation ID usage
    echo "Correlation ID entries:"
    grep -c "correlation_id" "$log_file" 2>/dev/null | sed 's/^/  Total: /' || echo "  Total: 0"
    
    # Show recent log entries
    echo "Recent log entries (last 5):"
    tail -n 5 "$log_file" | sed 's/^/  /'
    
    # Show file size
    local file_size=$(du -h "$log_file" | cut -f1)
    print_info "Log file size: $file_size"
}

show_log_locations() {
    print_section "Log File Locations"
    
    echo "Generated log files:"
    
    for log_file in "$LOG_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local size=$(du -h "$log_file" | cut -f1)
            local entries=$(wc -l < "$log_file" 2>/dev/null || echo "0")
            printf "  %-40s %8s (%s entries)\n" "$(basename "$log_file")" "$size" "$entries"
        fi
    done
    
    if [ ! -d "$LOG_DIR" ] || [ -z "$(ls -A "$LOG_DIR" 2>/dev/null)" ]; then
        print_warning "No log files found"
        print_info "Log files will be created when the application runs"
    fi
}

# =============================================================================
# Performance Testing
# =============================================================================

performance_test() {
    print_section "Logging Performance Test"
    
    echo "Testing logging performance impact..."
    
    cat > "$PROJECT_ROOT/temp_perf_test.py" << 'EOF'
import sys
import time
sys.path.insert(0, '.')
from src.utils.logging_config import get_logger, setup_application_logging

setup_application_logging()
logger = get_logger(__name__)

# Test logging performance
start_time = time.time()
num_logs = 1000

for i in range(num_logs):
    logger.info(
        f"Performance test log entry {i}",
        extra={
            "iteration": i,
            "test_type": "performance",
            "batch_size": num_logs
        }
    )

duration = time.time() - start_time
avg_time_per_log = (duration / num_logs) * 1000  # Convert to milliseconds

print(f"Performance test results:")
print(f"  Total logs: {num_logs}")
print(f"  Total time: {duration:.3f} seconds")
print(f"  Average time per log: {avg_time_per_log:.3f} ms")
print(f"  Logs per second: {num_logs / duration:.1f}")
EOF

    if python3 temp_perf_test.py; then
        print_success "Performance test completed"
    else
        print_error "Performance test failed"
    fi
    
    rm -f temp_perf_test.py
}

# =============================================================================
# Main Demo Function
# =============================================================================

run_demo() {
    local demo_type="$1"
    
    case "$demo_type" in
        "basic")
            demo_basic_logging
            ;;
        "api")
            demo_api_logging
            ;;
        "training")
            demo_model_training_logging
            ;;
        "json")
            demo_structured_logging
            ;;
        "performance")
            performance_test
            ;;
        "analysis")
            analyze_logs
            ;;
        "all")
            demo_basic_logging
            demo_structured_logging
            demo_model_training_logging
            performance_test
            analyze_logs
            ;;
        *)
            echo "Unknown demo type: $demo_type"
            show_usage
            exit 1
            ;;
    esac
}

show_usage() {
    echo "Usage: $0 [OPTION] [DEMO_TYPE]"
    echo ""
    echo "Demonstrate the logging capabilities of Patient Risk Predictor"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -c, --clean    Clean up log files before running"
    echo "  -v, --verbose  Enable verbose output"
    echo ""
    echo "Demo Types:"
    echo "  basic          Basic logging functionality"
    echo "  api            API request logging (starts server)"
    echo "  training       Model training logging" 
    echo "  json           Structured JSON logging"
    echo "  performance    Logging performance test"
    echo "  analysis       Analyze existing log files"
    echo "  all            Run all demonstrations (default)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all demonstrations"
    echo "  $0 basic              # Run basic logging demo only"
    echo "  $0 --clean api        # Clean logs and run API demo"
    echo "  $0 analysis           # Analyze existing logs"
}

clean_logs() {
    print_section "Cleaning Log Files"
    
    if [ -d "$LOG_DIR" ]; then
        rm -rf "$LOG_DIR"/*
        print_success "Cleaned log directory: $LOG_DIR"
    else
        print_info "Log directory does not exist: $LOG_DIR"
    fi
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    local clean_logs_flag=false
    local verbose=false
    local demo_type="all"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--clean)
                clean_logs_flag=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            basic|api|training|json|performance|analysis|all)
                demo_type="$1"
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
    print_header "PATIENT RISK PREDICTOR - LOGGING DEMONSTRATION"
    
    # Check dependencies
    check_dependencies
    
    # Clean logs if requested
    if [ "$clean_logs_flag" = true ]; then
        clean_logs
    fi
    
    # Setup environment
    setup_environment
    
    # Show current configuration
    print_info "Project root: $PROJECT_ROOT"
    print_info "Log directory: $LOG_DIR"
    print_info "Demo type: $demo_type"
    
    # Run the demonstration
    echo ""
    if run_demo "$demo_type"; then
        print_success "Demonstration completed successfully"
    else
        print_error "Demonstration encountered issues"
        exit 1
    fi
    
    # Show log file locations
    echo ""
    show_log_locations
    
    # Final message
    echo ""
    print_header "DEMONSTRATION COMPLETED"
    print_info "Check the logs directory for generated log files:"
    print_info "  Log directory: $LOG_DIR"
    print_info "  Main logs: $LOG_DIR/patient-risk-predictor.log"
    print_info "  Error logs: $LOG_DIR/patient-risk-predictor-errors.log"
    echo ""
    print_info "To view logs in real-time:"
    print_info "  tail -f $LOG_DIR/patient-risk-predictor.log"
    echo ""
    print_info "For JSON log analysis:"
    print_info "  cat $LOG_DIR/patient-risk-predictor.log | jq ."
    echo ""
    print_info "To use a different log directory:"
    print_info "  LOG_DIR=/custom/path ./scripts/logging_demo.sh"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi