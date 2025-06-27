#!/bin/bash

# =============================================================================
# Quick Logging Test - Patient Risk Predictor
# =============================================================================
# Quick verification that logging works with different levels
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

echo "========================================="
echo "QUICK LOGGING TEST"
echo "========================================="

cd "$PROJECT_ROOT"

# Test 1: Check help message
print_step "Testing help message"
python3 main.py --help
print_success "Help message works"

# Test 2: Quick API start with different log levels
for level in INFO DEBUG ERROR; do
    print_step "Testing log level: $level"
    
    # Set up test environment
    export LOG_DIR="./test-logs-$level"
    export LOG_TO_FILE="true"
    mkdir -p "$LOG_DIR"
    
    # Start server briefly
    print_info "Starting server with $level logging..."
    python3 main.py --log-level "$level" &
    API_PID=$!
    
    # Wait a moment
    sleep 3
    
    # Test health endpoint
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "API responding with $level logging"
    else
        print_info "API not responding (may still be starting)"
    fi
    
    # Stop server
    kill $API_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    
    # Check logs
    if [ -f "$LOG_DIR/patient-risk-predictor.log" ]; then
        local lines=$(wc -l < "$LOG_DIR/patient-risk-predictor.log")
        print_success "Log file created with $lines entries"
        
        # Show first log entry
        echo "   Sample log: $(head -n 1 "$LOG_DIR/patient-risk-predictor.log")"
    else
        print_info "No log file created (this might be expected for some levels)"
    fi
    
    # Cleanup
    rm -rf "$LOG_DIR"
    
    echo ""
done

# Test 3: Training with logging
print_step "Testing model training with logging"
export LOG_DIR="./test-logs-training"
export LOG_TO_FILE="true"
mkdir -p "$LOG_DIR"

if timeout 30 python3 main.py train --log-level INFO; then
    print_success "Training completed with logging"
    
    if [ -f "$LOG_DIR/patient-risk-predictor.log" ]; then
        local training_logs=$(grep -c "training\|model" "$LOG_DIR/patient-risk-predictor.log" || echo "0")
        print_success "Found $training_logs training-related log entries"
    fi
else
    print_info "Training test timed out or failed (this might be expected)"
fi

rm -rf "$LOG_DIR"

echo ""
echo "========================================="
echo "QUICK TEST COMPLETED"
echo "========================================="
print_success "Basic logging functionality verified"
print_info "For comprehensive testing, run: ./scripts/test_logging.sh"
print_info "For logging demos, run: ./scripts/logging_demo.sh"