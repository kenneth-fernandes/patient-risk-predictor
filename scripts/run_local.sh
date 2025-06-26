#!/bin/bash
# Comprehensive script for fully local execution (no Docker dependencies)

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
    echo -e "${CYAN}║${WHITE}${BOLD}                PATIENT RISK PREDICTOR                       ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${YELLOW}                    FULLY LOCAL EXECUTION                     ${NC}${CYAN}║${NC}"
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

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print info messages
print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_header

# Function to show usage
show_usage() {
    print_section "USAGE GUIDE"
    
    echo -e "${WHITE}${BOLD}Usage:${NC} $0 [COMMAND] [OPTIONS]"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Commands:${NC}"
    echo -e "  ${GREEN}flush${NC}               Flush/clear all environment variables"
    echo -e "  ${GREEN}cleanup${NC}             Clean up corrupted MLflow directories"
    echo -e "  ${GREEN}train${NC}               Train the model only"
    echo -e "  ${GREEN}api${NC}                 Run API with default settings"
    echo -e "  ${GREEN}api-custom${NC}          Run API with custom host and port"
    echo -e "  ${GREEN}full${NC}                Train model and run API ${CYAN}[DEFAULT]${NC}"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Options (for full mode):${NC}"
    echo -e "  ${PURPLE}--server, -s${NC}        Start with local MLflow server (includes web UI)"
    echo -e "  ${PURPLE}--simple, -f${NC}        Use file-based MLflow (no server, no UI) ${CYAN}[DEFAULT]${NC}"
    echo -e "  ${PURPLE}--help, -h${NC}          Show this help message"
    echo ""
    
    echo -e "${YELLOW}${BOLD}Examples:${NC}"
    echo -e "  ${CYAN}$0 flush${NC}            ${WHITE}# Clear environment variables${NC}"
    echo -e "  ${CYAN}$0 cleanup${NC}          ${WHITE}# Clean corrupted MLflow directories${NC}"
    echo -e "  ${CYAN}$0 train${NC}            ${WHITE}# Train model only${NC}"
    echo -e "  ${CYAN}$0 api${NC}              ${WHITE}# Run API with defaults${NC}"
    echo -e "  ${CYAN}$0 api-custom${NC}       ${WHITE}# Run API with custom host:port${NC}"
    echo -e "  ${CYAN}$0 full --server${NC}    ${WHITE}# Full workflow with MLflow server${NC}"
    echo -e "  ${CYAN}$0${NC}                  ${WHITE}# Full workflow (default)${NC}"
    echo ""
}

# Function to cleanup background processes
cleanup() {
    print_section "🧹 CLEANUP"
    print_info "Terminating background processes..."
    if [ ! -z "$MLFLOW_PID" ]; then
        print_info "Stopping MLflow server (PID: $MLFLOW_PID)"
        kill $MLFLOW_PID 2>/dev/null
        print_success "MLflow server terminated"
    fi
    print_success "Cleanup completed"
    echo ""
    exit 0
}

# Function to clean up corrupted MLflow directories
cleanup_mlflow() {
    print_section "🧹 MLFLOW CLEANUP"
    print_info "Checking for corrupted MLflow experiments..."
    
    if [ -d "./mlruns" ]; then
        # Find directories without meta.yaml files
        local corrupted_dirs=()
        for exp_dir in ./mlruns/[0-9]*; do
            if [ -d "$exp_dir" ] && [ ! -f "$exp_dir/meta.yaml" ]; then
                corrupted_dirs+=($(basename "$exp_dir"))
            fi
        done
        
        if [ ${#corrupted_dirs[@]} -gt 0 ]; then
            print_warning "Found corrupted experiment directories: ${corrupted_dirs[*]}"
            for exp_id in "${corrupted_dirs[@]}"; do
                print_info "Removing corrupted experiment: $exp_id"
                rm -rf "./mlruns/$exp_id"
                print_success "Cleaned experiment: $exp_id"
            done
        else
            print_success "No corrupted experiments found"
        fi
    else
        print_info "No MLflow directory found (will be created on first run)"
    fi
    echo ""
}

# Function to flush environment variables
flush_env() {
    print_section "🔄 ENVIRONMENT FLUSH"
    print_info "Clearing environment variables..."
    
    # Store which variables were actually set
    local cleared_vars=()
    [ ! -z "$MLFLOW_TRACKING_URI" ] && cleared_vars+=("MLFLOW_TRACKING_URI")
    [ ! -z "$HOST" ] && cleared_vars+=("HOST")
    [ ! -z "$PORT" ] && cleared_vars+=("PORT")
    [ ! -z "$ENVIRONMENT" ] && cleared_vars+=("ENVIRONMENT")
    [ ! -z "$WORKERS" ] && cleared_vars+=("WORKERS")
    [ ! -z "$LOG_LEVEL" ] && cleared_vars+=("LOG_LEVEL")
    
    unset MLFLOW_TRACKING_URI
    unset HOST
    unset PORT
    unset ENVIRONMENT
    unset WORKERS
    unset LOG_LEVEL
    
    if [ ${#cleared_vars[@]} -eq 0 ]; then
        print_info "No environment variables were set"
    else
        for var in "${cleared_vars[@]}"; do
            print_success "Cleared: $var"
        done
    fi
    echo ""
}

# Function to train model
train_model() {
    print_section "🤖 MODEL TRAINING"
    print_info "Starting model training process..."
    echo ""
    
    # Clean up any corrupted MLflow directories first
    cleanup_mlflow
    
    python main.py train
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        print_success "Model training completed successfully!"
        print_info "Model artifacts saved to MLflow"
    else
        print_error "Model training failed with exit code: $exit_code"
        exit 1
    fi
    echo ""
}

# Function to run API with defaults
run_api() {
    print_section "🚀 API SERVER"
    print_info "Starting API server with default settings..."
    echo ""
    
    echo -e "${GREEN}🌐 Server Details:${NC}"
    echo -e "  ${CYAN}URL:${NC} http://localhost:8000"
    echo -e "  ${CYAN}Environment:${NC} Development"
    echo -e "  ${CYAN}Workers:${NC} 1"
    echo ""
    
    echo -e "${YELLOW}🧪 Test Commands:${NC}"
    echo -e "  ${WHITE}Health Check:${NC}"
    echo -e "    ${CYAN}curl http://localhost:8000/${NC}"
    echo ""
    echo -e "  ${WHITE}Prediction Test:${NC}"
    echo -e "    ${CYAN}curl -X POST http://localhost:8000/predict \\${NC}"
    echo -e "      ${CYAN}-H 'Content-Type: application/json' \\${NC}"
    echo -e "      ${CYAN}-d '{\"age\":63,\"sex\":1,\"cp\":3,\"trestbps\":145,\"chol\":233,\"fbs\":1,\"restecg\":0,\"thalach\":150,\"exang\":0,\"oldpeak\":2.3,\"slope\":0,\"ca\":0,\"thal\":1}'${NC}"
    echo ""
    
    print_warning "Press Ctrl+C to stop the server"
    echo ""
    
    python main.py
}

# Function to run API with custom settings
run_api_custom() {
    print_section "⚙️  CUSTOM API SERVER"
    
    echo -e "${YELLOW}Enter custom API settings:${NC}"
    echo ""
    
    echo -ne "${WHITE}Host${NC} (default: ${CYAN}127.0.0.1${NC}): "
    read custom_host
    echo -ne "${WHITE}Port${NC} (default: ${CYAN}8000${NC}): "
    read custom_port
    
    custom_host=${custom_host:-127.0.0.1}
    custom_port=${custom_port:-8000}
    
    echo ""
    print_info "Starting API server with custom configuration..."
    echo ""
    
    echo -e "${GREEN}🌐 Server Details:${NC}"
    echo -e "  ${CYAN}URL:${NC} http://${custom_host}:${custom_port}"
    echo -e "  ${CYAN}Host:${NC} ${custom_host}"
    echo -e "  ${CYAN}Port:${NC} ${custom_port}"
    echo ""
    
    print_warning "Press Ctrl+C to stop the server"
    echo ""
    
    python main.py $custom_host $custom_port
}

# Function to start MLflow server
start_mlflow_server() {
    print_section "📊 MLFLOW SERVER"
    
    # More aggressive cleanup of MLflow processes
    print_info "Cleaning up existing MLflow processes..."
    pkill -9 -f "mlflow server" 2>/dev/null || true
    pkill -9 -f "gunicorn.*mlflow" 2>/dev/null || true
    
    # Wait for processes to fully terminate
    sleep 3
    print_success "Process cleanup completed"
    echo ""
    
    # Use port 5001 to avoid conflicts
    MLFLOW_PORT=5001
    print_info "Starting MLflow server on port ${MLFLOW_PORT}..."
    
    echo -e "${GREEN}📋 Server Configuration:${NC}"
    echo -e "  ${CYAN}Backend Store:${NC} sqlite:///mlflow.db"
    echo -e "  ${CYAN}Artifact Root:${NC} ./mlruns"
    echo -e "  ${CYAN}Host:${NC} 127.0.0.1"
    echo -e "  ${CYAN}Port:${NC} ${MLFLOW_PORT}"
    echo ""
    
    mlflow server \
        --backend-store-uri sqlite:///mlflow.db \
        --default-artifact-root ./mlruns \
        --host 127.0.0.1 \
        --port ${MLFLOW_PORT} &
    
    MLFLOW_PID=$!
    print_success "MLflow server started (PID: $MLFLOW_PID)"
    echo -e "${GREEN}🌐 MLflow UI:${NC} http://localhost:${MLFLOW_PORT}"
    echo ""
    
    # Wait for MLflow to start with better health checking
    print_info "Waiting for MLflow server to initialize..."
    print_warning "This may take 10-20 seconds on first startup"
    echo ""
    
    # Wait longer and check if server responds
    for i in {1..20}; do
        sleep 2
        if curl -s http://localhost:${MLFLOW_PORT}/ >/dev/null 2>&1; then
            print_success "MLflow server is ready! (took $((i*2)) seconds)"
            sleep 2  # Give it a bit more time to fully initialize
            echo ""
            break
        else
            echo -e "${BLUE}⏳${NC} Checking server health... ($i/20)"
        fi
        
        if [ $i -eq 20 ]; then
            print_warning "MLflow server taking longer than expected"
            print_info "Continuing anyway... (server may need more time)"
            sleep 5
            echo ""
        fi
    done
}

# Main script logic
COMMAND=${1:-full}

case $COMMAND in
    flush)
        print_info "Executing: ${BOLD}Environment Flush${NC}"
        flush_env
        ;;
    cleanup)
        print_info "Executing: ${BOLD}MLflow Cleanup${NC}"
        cleanup_mlflow
        ;;
    train)
        print_info "Executing: ${BOLD}Model Training${NC}"
        flush_env
        train_model
        ;;
    api)
        print_info "Executing: ${BOLD}API Server (Default)${NC}"
        flush_env
        run_api
        ;;
    api-custom)
        print_info "Executing: ${BOLD}API Server (Custom)${NC}"
        flush_env
        run_api_custom
        ;;
    full)
        print_info "Executing: ${BOLD}Full Workflow (Train + API)${NC}"
        echo ""
        # Handle options for full mode
        shift
        USE_SERVER=false
        
        while [[ $# -gt 0 ]]; do
            case $1 in
                --server|-s)
                    USE_SERVER=true
                    shift
                    ;;
                --simple|-f)
                    USE_SERVER=false
                    shift
                    ;;
                --help|-h)
                    show_usage
                    exit 0
                    ;;
                *)
                    print_error "Unknown option: $1"
                    echo ""
                    show_usage
                    exit 1
                    ;;
            esac
        done
        
        # Clear environment variables
        flush_env
        
        # Setup based on mode
        if [ "$USE_SERVER" = true ]; then
            # Check if MLflow is installed
            if ! command -v mlflow &> /dev/null; then
                print_error "MLflow is not installed"
                print_info "Please run: ${CYAN}pip install mlflow${NC}"
                exit 1
            fi
            
            print_info "${BOLD}Mode:${NC} Local MLflow server with web UI"
            trap cleanup EXIT INT TERM
            start_mlflow_server
            export MLFLOW_TRACKING_URI=http://localhost:5001
            print_success "MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI"
        else
            print_info "${BOLD}Mode:${NC} File-based MLflow (no server)"
            print_info "Models will be saved to: ${CYAN}./mlruns${NC}"
        fi
        
        echo ""
        
        # Train model
        train_model
        
        # Start API server
        print_section "🚀 FINAL API SERVER"
        print_info "Starting main API server..."
        echo ""
        
        echo -e "${GREEN}🌐 Service URLs:${NC}"
        echo -e "  ${CYAN}API Server:${NC} http://localhost:8000"
        if [ "$USE_SERVER" = true ]; then
            echo -e "  ${CYAN}MLflow UI:${NC} http://localhost:5001"
        fi
        echo ""
        
        echo -e "${YELLOW}🧪 Test Commands:${NC}"
        echo -e "  ${WHITE}Health Check:${NC}"
        echo -e "    ${CYAN}curl http://localhost:8000/${NC}"
        echo ""
        echo -e "  ${WHITE}Prediction Test:${NC}"
        echo -e "    ${CYAN}curl -X POST http://localhost:8000/predict \\${NC}"
        echo -e "      ${CYAN}-H 'Content-Type: application/json' \\${NC}"
        echo -e "      ${CYAN}-d '{\"age\":63,\"sex\":1,\"cp\":3,\"trestbps\":145,\"chol\":233,\"fbs\":1,\"restecg\":0,\"thalach\":150,\"exang\":0,\"oldpeak\":2.3,\"slope\":0,\"ca\":0,\"thal\":1}'${NC}"
        echo ""
        
        print_warning "Press Ctrl+C to stop all services"
        echo ""
        
        python main.py
        ;;
    --help|-h)
        show_usage
        exit 0
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac