#!/bin/bash
# Multi-Python version dependency testing script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Dependencies Across Python Versions${NC}"
echo "=================================================="

# Function to test with specific Python version
test_python_version() {
    local python_cmd=$1
    local version_name=$2
    
    if ! command -v "$python_cmd" &> /dev/null; then
        echo -e "${YELLOW}⚠️  $version_name not available, skipping${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}Testing with $version_name...${NC}"
    local actual_version=$($python_cmd --version 2>&1)
    echo -e "Version: ${GREEN}$actual_version${NC}"
    
    # Create temporary virtual environment
    local temp_env="temp_test_env_$$"
    $python_cmd -m venv "$temp_env" > /dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        return 1
    fi
    
    source "$temp_env/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Test requirements
    local result=0
    
    echo -e "  ${YELLOW}Testing requirements.txt...${NC}"
    pip install -r requirements.txt --dry-run > /tmp/pip_test_$$.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ requirements.txt: Compatible${NC}"
    else
        echo -e "  ${RED}❌ requirements.txt: Has conflicts${NC}"
        # Show first conflict for debugging
        grep -A2 "conflict is caused by" /tmp/pip_test_$$.log | head -3 | sed 's/^/    /'
        result=1
    fi
    
    echo -e "  ${YELLOW}Testing requirements-prod.txt...${NC}"
    pip install -r requirements-prod.txt --dry-run > /tmp/pip_test_prod_$$.log 2>&1
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ requirements-prod.txt: Compatible${NC}"
    else
        echo -e "  ${RED}❌ requirements-prod.txt: Has conflicts${NC}"
        # Show first conflict for debugging
        grep -A2 "conflict is caused by" /tmp/pip_test_prod_$$.log | head -3 | sed 's/^/    /'
        result=1
    fi
    
    # Cleanup temp files
    rm -f /tmp/pip_test_$$.log /tmp/pip_test_prod_$$.log
    
    deactivate
    rm -rf "$temp_env"
    
    return $result
}

# Test current Python version first
echo -e "Current Python: ${GREEN}$(python --version)${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/test_deps.sh" ]; then
    "$SCRIPT_DIR/test_deps.sh"
else
    echo -e "${YELLOW}⚠️  test_deps.sh not found, running inline test${NC}"
    pip install -r requirements.txt --dry-run > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Current Python requirements: Compatible${NC}"
    else
        echo -e "${RED}❌ Current Python requirements: Has conflicts${NC}"
    fi
fi

# Test other Python versions if available
overall_result=0

# List of Python versions to test (matching CI matrix)
python_versions=(
    "python3.11:Python 3.11"
    "python3.12:Python 3.12"
)

for version_info in "${python_versions[@]}"; do
    IFS=':' read -r python_cmd version_name <<< "$version_info"
    test_python_version "$python_cmd" "$version_name"
    if [ $? -ne 0 ]; then
        overall_result=1
    fi
done

echo -e "\n=================================================="
if [ $overall_result -eq 0 ]; then
    echo -e "${GREEN}🎉 All Python versions are compatible!${NC}"
else
    echo -e "${RED}⚠️  Some versions have conflicts${NC}"
fi

exit $overall_result