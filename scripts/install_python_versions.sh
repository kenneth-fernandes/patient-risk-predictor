#!/bin/bash
# Script to help install multiple Python versions for testing

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐍 Python Version Installation Helper${NC}"
echo "======================================"

echo -e "${YELLOW}This script provides instructions for installing multiple Python versions${NC}"
echo ""

# Check if pyenv is available
if command -v pyenv &> /dev/null; then
    echo -e "${GREEN}✅ pyenv is available!${NC}"
    echo ""
    echo -e "${BLUE}To install Python versions for testing:${NC}"
    echo "  pyenv install 3.11.9"
    echo "  pyenv install 3.12.3"
    echo ""
    echo -e "${BLUE}To make them available globally:${NC}"
    echo "  pyenv global system 3.11.9 3.12.3"
    echo ""
    echo -e "${BLUE}To check available versions:${NC}"
    echo "  pyenv versions"
else
    echo -e "${YELLOW}⚠️  pyenv not found${NC}"
    echo ""
    echo -e "${BLUE}Installation options:${NC}"
    echo ""
    echo -e "${YELLOW}1. Install pyenv (recommended):${NC}"
    echo "   # On macOS with Homebrew:"
    echo "   brew install pyenv"
    echo "   # Then add to your shell profile (~/.zshrc or ~/.bash_profile):"
    echo '   export PATH="$HOME/.pyenv/bin:$PATH"'
    echo '   eval "$(pyenv init -)"'
    echo ""
    echo -e "${YELLOW}2. Use official Python downloads:${NC}"
    echo "   Visit: https://www.python.org/downloads/"
    echo "   Download and install Python 3.11, 3.12"
    echo ""
    echo -e "${YELLOW}3. Use conda/miniconda:${NC}"
    echo "   conda create -n py311 python=3.11"
    echo "   conda create -n py312 python=3.12"
fi

echo ""
echo -e "${BLUE}After installation, test with:${NC}"
echo "  ./scripts/test_deps_multi.sh"
echo ""
echo -e "${GREEN}Note: You only need multiple versions for comprehensive testing.${NC}"
echo -e "${GREEN}Single version testing with ./scripts/test_deps.sh is usually sufficient.${NC}"