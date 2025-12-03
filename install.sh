#!/bin/bash

# Linux Desktop AI Agent Installation Script
# Installs all dependencies and sets up the agent

set -e

echo "=========================================="
echo "Linux Desktop AI Agent - Installation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${RED}Error: This script only works on Linux${NC}"
    exit 1
fi

# Detect package manager
if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt install -y"
    UPDATE_CMD="sudo apt update"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    INSTALL_CMD="sudo dnf install -y"
    UPDATE_CMD="sudo dnf check-update"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
    UPDATE_CMD="sudo pacman -Sy"
else
    echo -e "${RED}Error: Unsupported package manager${NC}"
    exit 1
fi

echo -e "${GREEN}Detected package manager: $PKG_MANAGER${NC}"
echo ""

# Step 1: Update package lists
echo -e "${YELLOW}Step 1: Updating package lists...${NC}"
$UPDATE_CMD
echo -e "${GREEN}✓ Package lists updated${NC}"
echo ""

# Step 2: Install system dependencies
echo -e "${YELLOW}Step 2: Installing system dependencies...${NC}"
$INSTALL_CMD python3 python3-pip python3-dev libnotify-bin net-tools wireless-tools

# Optional security tools
echo -e "${YELLOW}Installing optional security tools...${NC}"
$INSTALL_CMD clamav rkhunter || true

echo -e "${GREEN}✓ System dependencies installed${NC}"
echo ""

# Step 3: Install Python dependencies
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"
pip3 install -r requirements_linux.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 4: Check for Ollama
echo -e "${YELLOW}Step 4: Checking for Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    OLLAMA_VERSION_OUTPUT=$(ollama --version 2>&1)
    if echo "$OLLAMA_VERSION_OUTPUT" | grep -q "0\.13\.0"; then
        echo -e "${GREEN}✓ Verified Ollama 0.13.0${NC}"
    else
        echo -e "${YELLOW}⚠ Detected ${OLLAMA_VERSION_OUTPUT:-unknown}. This project targets Ollama 0.13.0.${NC}"
        echo "  Please reinstall/upgrade Ollama if you encounter issues:"
        echo "    curl -fsSL https://ollama.ai/install.sh | sh"
    fi
else
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
    echo "Re-run 'ollama --version' to confirm it reports 0.13.0"
fi
echo ""

# Step 5: Pull Llama model
echo -e "${YELLOW}Step 5: Pulling Llama 3.1 8B model...${NC}"
echo "Note: This may take a few minutes on first run"
ollama pull llama3.1:8b || echo -e "${YELLOW}Note: Make sure Ollama is running (ollama serve)${NC}"
echo -e "${GREEN}✓ Llama model ready${NC}"
echo ""

# Step 6: Make agent executable
echo -e "${YELLOW}Step 6: Setting permissions...${NC}"
chmod +x linux_desktop_agent.py
chmod +x install.sh
echo -e "${GREEN}✓ Permissions set${NC}"
echo ""

# Step 7: Create configuration directory
echo -e "${YELLOW}Step 7: Creating configuration directory...${NC}"
mkdir -p ~/.config/linux-desktop-agent
echo -e "${GREEN}✓ Configuration directory created${NC}"
echo ""

# Step 8: Optional - Install systemd service
echo -e "${YELLOW}Step 8: Optional - Install systemd service?${NC}"
read -p "Install systemd service for auto-start? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing systemd service..."
    sudo cp linux-desktop-agent.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable linux-desktop-agent.service
    echo -e "${GREEN}✓ Systemd service installed${NC}"
    echo "  Start with: sudo systemctl start linux-desktop-agent"
    echo "  Status: sudo systemctl status linux-desktop-agent"
    echo "  Logs: journalctl -u linux-desktop-agent -f"
fi
echo ""

# Step 9: Verify installation
echo -e "${YELLOW}Step 9: Verifying installation...${NC}"
echo "Checking Python..."
python3 --version
echo "Checking psutil..."
python3 -c "import psutil; print('✓ psutil OK')"
echo "Checking Ollama..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama running" || echo "⚠ Ollama not running (start with: ollama serve)"
echo ""

# Installation complete
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start Ollama (if not already running):"
echo "   ${YELLOW}ollama serve${NC}"
echo ""
echo "2. Run the agent in interactive mode:"
echo "   ${YELLOW}python3 linux_desktop_agent.py${NC}"
echo ""
echo "3. Or execute a single command:"
echo "   ${YELLOW}python3 linux_desktop_agent.py \"check my system health\"${NC}"
echo ""
echo "4. View help:"
echo "   ${YELLOW}python3 linux_desktop_agent.py interactive${NC}"
echo "   Then type: ${YELLOW}help${NC}"
echo ""
echo "Documentation: ${YELLOW}README_LINUX.md${NC}"
echo ""
