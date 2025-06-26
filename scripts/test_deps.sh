#!/bin/bash
# Dependency compatibility testing script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Python Dependencies Compatibility${NC}"
echo "=================================================="

# Function to test requirements file
test_requirements() {
    local req_file=$1
    local label=$2
    
    echo -e "\n${YELLOW}Testing $label...${NC}"
    
    # Test with dry-run
    pip install -r "$req_file" --dry-run > /tmp/pip_test.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $label: Compatible${NC}"
        return 0
    else
        echo -e "${RED}❌ $label: Has conflicts${NC}"
        echo -e "${YELLOW}Conflicts found:${NC}"
        grep -A10 "conflict is caused by" /tmp/pip_test.log || cat /tmp/pip_test.log | tail -20
        return 1
    fi
}

# Test current Python version
echo -e "Current Python version: ${GREEN}$(python --version)${NC}"
echo -e "Current pip version: ${GREEN}$(pip --version)${NC}"

# Test both requirements files
overall_result=0

test_requirements "requirements.txt" "Main Requirements"
if [ $? -ne 0 ]; then
    overall_result=1
fi

test_requirements "requirements-prod.txt" "Production Requirements"
if [ $? -ne 0 ]; then
    overall_result=1
fi

# Summary
echo -e "\n=================================================="
if [ $overall_result -eq 0 ]; then
    echo -e "${GREEN}🎉 All dependency files are compatible!${NC}"
else
    echo -e "${RED}⚠️  Some dependency conflicts found${NC}"
    echo -e "${YELLOW}Fix the conflicts above before committing${NC}"
fi

# Cleanup
rm -f /tmp/pip_test.log

exit $overall_result