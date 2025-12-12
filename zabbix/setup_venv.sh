#!/bin/bash
# ============================================
# Virtual Environment Setup Script
# ============================================
# This script creates a Python virtual environment
# and installs all required dependencies for
# NetBox-Zabbix integration scripts
#
# Usage:
#   ./setup_venv.sh
#
# After setup, activate the venv with:
#   source venv/bin/activate

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║     NetBox-Zabbix Virtual Environment Setup               ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# Check Python installation
# ============================================
echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo -e "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Found Python ${PYTHON_VERSION}"

# Check Python version (need 3.8+)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
    echo -e "Current version: ${PYTHON_VERSION}"
    exit 1
fi

# ============================================
# Check if venv module is available
# ============================================
echo -e "\n${YELLOW}[2/5]${NC} Checking venv module..."

if ! python3 -m venv --help &> /dev/null; then
    echo -e "${RED}❌ Python venv module is not available${NC}"
    echo -e "Install with: sudo apt-get install python3-venv"
    exit 1
fi

echo -e "${GREEN}✓${NC} venv module is available"

# ============================================
# Create virtual environment
# ============================================
echo -e "\n${YELLOW}[3/5]${NC} Creating virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠${NC}  Virtual environment already exists at: ${VENV_DIR}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo -e "Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created at: ${VENV_DIR}"
else
    echo -e "${GREEN}✓${NC} Using virtual environment at: ${VENV_DIR}"
fi

# ============================================
# Activate virtual environment
# ============================================
echo -e "\n${YELLOW}[4/5]${NC} Activating virtual environment..."

source "${VENV_DIR}/bin/activate"

if [ "$VIRTUAL_ENV" != "" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# ============================================
# Upgrade pip
# ============================================
echo -e "\n${YELLOW}[5/5]${NC} Upgrading pip..."

python -m pip install --upgrade pip > /dev/null 2>&1

PIP_VERSION=$(pip --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} pip upgraded to version ${PIP_VERSION}"

# ============================================
# Install requirements
# ============================================
echo -e "\n${YELLOW}[6/6]${NC} Installing Python packages..."

if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo -e "Installing from requirements.txt..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
    echo -e "${GREEN}✓${NC} All packages installed successfully"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    echo -e "Installing packages manually..."
    pip install pynetbox pyzabbix requests python-dotenv
    echo -e "${GREEN}✓${NC} Basic packages installed"
fi

# ============================================
# Verify installations
# ============================================
echo -e "\n${BLUE}Verifying installations...${NC}"

# Check pynetbox
if python -c "import pynetbox" 2>/dev/null; then
    PYNETBOX_VERSION=$(python -c "import pynetbox; print(pynetbox.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓${NC} pynetbox ${PYNETBOX_VERSION}"
else
    echo -e "${RED}✗${NC} pynetbox"
fi

# Check pyzabbix
if python -c "import pyzabbix" 2>/dev/null; then
    PYZABBIX_VERSION=$(python -c "import pyzabbix; print(pyzabbix.__version__)" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓${NC} pyzabbix ${PYZABBIX_VERSION}"
else
    echo -e "${RED}✗${NC} pyzabbix"
fi

# Check requests
if python -c "import requests" 2>/dev/null; then
    REQUESTS_VERSION=$(python -c "import requests; print(requests.__version__)")
    echo -e "${GREEN}✓${NC} requests ${REQUESTS_VERSION}"
else
    echo -e "${RED}✗${NC} requests"
fi

# Check python-dotenv
if python -c "import dotenv" 2>/dev/null; then
    DOTENV_VERSION=$(python -c "import dotenv; print(dotenv.__version__)")
    echo -e "${GREEN}✓${NC} python-dotenv ${DOTENV_VERSION}"
else
    echo -e "${RED}✗${NC} python-dotenv"
fi

# ============================================
# Setup complete
# ============================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║               ✅ Setup Complete!                           ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Activate the virtual environment:"
echo -e "     ${GREEN}source venv/bin/activate${NC}"
echo ""
echo -e "  2. Configure your environment:"
echo -e "     ${GREEN}cp .env.example .env${NC}"
echo -e "     ${GREEN}nano .env${NC}"
echo ""
echo -e "  3. Test connections:"
echo -e "     ${GREEN}python test_connections.py${NC}"
echo ""
echo -e "  4. Run sync script:"
echo -e "     ${GREEN}python netbox_to_zabbix_sync.py${NC}"
echo ""
echo -e "  5. Deactivate when done:"
echo -e "     ${GREEN}deactivate${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} The virtual environment is located at:"
echo -e "      ${VENV_DIR}"
echo ""
