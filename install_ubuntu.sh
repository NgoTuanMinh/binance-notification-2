#!/bin/bash
# Installation script for Ubuntu/Debian (apt-based)
# Automated setup for Binance Futures Scanner

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 Binance Futures Scanner - Ubuntu/Debian Install     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Running as root. Consider using a regular user.${NC}"
    echo ""
fi

# Detect apt-based distro
if ! command -v apt-get &> /dev/null; then
    echo -e "${RED}❌ This script requires apt-get (Ubuntu/Debian).${NC}"
    exit 1
fi

# Use sudo only when needed/available
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    if command -v sudo &> /dev/null; then
        SUDO="sudo"
    else
        echo -e "${RED}❌ sudo not found. Run this script as root or install sudo.${NC}"
        exit 1
    fi
fi

# Step 1: Update system
echo -e "${GREEN}1️⃣  Updating system packages...${NC}"
$SUDO apt-get update -qq
echo -e "${GREEN}✅ System updated${NC}"
echo ""

# Step 2: Check Python
echo -e "${GREEN}2️⃣  Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
    
    # Check Python version (need 3.8+)
    PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VER="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VER" "$PYTHON_VER" | sort -V | head -n1)" = "$REQUIRED_VER" ]; then 
        echo -e "${GREEN}✅ Python version is sufficient (>= 3.8)${NC}"
    else
        echo -e "${RED}❌ Python 3.8+ required, found $PYTHON_VER${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Python 3 not found. Installing...${NC}"
    $SUDO apt-get install -y python3 python3-pip python3-venv
    echo -e "${GREEN}✅ Python 3 installed${NC}"
fi
echo ""

# Step 3: Install system dependencies
echo -e "${GREEN}3️⃣  Installing system dependencies...${NC}"
$SUDO apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget
echo -e "${GREEN}✅ System dependencies installed${NC}"
echo ""

# Step 4: Check pip
echo -e "${GREEN}4️⃣  Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✅ Found: $PIP_VERSION${NC}"
else
    echo -e "${YELLOW}Installing pip3...${NC}"
    $SUDO apt-get install -y python3-pip
    echo -e "${GREEN}✅ pip3 installed${NC}"
fi

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python3 -m pip install --upgrade pip --user
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Step 5: Virtual Environment
echo -e "${GREEN}5️⃣  Setting up Virtual Environment...${NC}"

if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  venv folder already exists${NC}"
    read -p "Remove and recreate? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment recreated${NC}"
    else
        echo -e "${YELLOW}Using existing venv${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip in venv
pip install --upgrade pip
echo ""

# Step 6: Install Python packages
echo -e "${GREEN}6️⃣  Installing Python packages...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"
echo ""

# Install packages from requirements.txt
if pip install -r requirements.txt; then
    echo -e "${GREEN}✅ All packages installed successfully!${NC}"
else
    echo -e "${RED}❌ Installation failed!${NC}"
    echo ""
    echo "Trying alternative installation method..."
    
    # Try installing packages one by one
    for package in ccxt pandas pandas-ta python-dotenv aiohttp numpy; do
        echo "Installing $package..."
        pip install $package || echo "Failed to install $package"
    done
fi
echo ""

# Step 7: Test imports
echo -e "${GREEN}7️⃣  Testing package imports...${NC}"
python test_imports.py
IMPORT_STATUS=$?
echo ""

# Step 8: Create .env if not exists
echo -e "${GREEN}8️⃣  Setting up configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env and add your Telegram credentials!${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi
echo ""

# Step 9: Setup systemd service (optional)
echo -e "${GREEN}9️⃣  Setup systemd service?${NC}"
echo -e "${YELLOW}This allows bot to run as a background service and auto-start on boot${NC}"
read -p "Setup systemd service? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    USER=$(whoami)
    WORK_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/binance-bot.service"
    
    echo -e "${YELLOW}Creating systemd service file...${NC}"
    $SUDO tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Binance Futures Scanner Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$WORK_DIR/venv/bin/python $WORK_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$WORK_DIR/bot.log
StandardError=append:$WORK_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✅ Service file created at $SERVICE_FILE${NC}"
    
    # Reload systemd
    $SUDO systemctl daemon-reload
    
    echo ""
    echo -e "${YELLOW}Service commands:${NC}"
    echo "  Start:   sudo systemctl start binance-bot"
    echo "  Stop:    sudo systemctl stop binance-bot"
    echo "  Status:  sudo systemctl status binance-bot"
    echo "  Enable:  sudo systemctl enable binance-bot  (auto-start on boot)"
    echo "  Logs:    sudo journalctl -u binance-bot -f"
    echo ""
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🎉 Installation Completed Successfully!                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $IMPORT_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ All packages are working correctly!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo ""
    echo "1️⃣  Configure Telegram credentials:"
    echo "   nano .env"
    echo "   # Add your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
    echo ""
    echo "2️⃣  (Optional) Configure symbol filtering for faster testing:"
    echo "   # In .env, add:"
    echo "   MAX_SYMBOLS_TO_SCAN=50"
    echo ""
    echo "3️⃣  Test the setup:"
    echo "   source venv/bin/activate"
    echo "   python test_setup.py"
    echo ""
    echo "4️⃣  Run bot (test once):"
    echo "   python main.py --once"
    echo ""
    echo "5️⃣  Run bot continuously:"
    echo "   python main.py"
    echo ""
    echo "   Or using systemd service (if configured):"
    echo "   sudo systemctl start binance-bot"
    echo "   sudo systemctl enable binance-bot  # auto-start on boot"
    echo ""
    echo -e "${YELLOW}📖 Documentation:${NC}"
    echo "   - START_HERE.md      Quick start guide"
    echo "   - QUICKSTART.md      5-minute setup"
    echo "   - DEPLOYMENT.md      Production deployment"
    echo "   - README.md          Full documentation"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "   - Always activate venv: source venv/bin/activate"
    echo "   - View logs: tail -f bot.log"
    echo "   - Monitor with: sudo systemctl status binance-bot"
    echo ""
else
    echo -e "${RED}⚠️  Some packages failed to import${NC}"
    echo ""
    echo "Please check the errors above and:"
    echo "1. Read INSTALLATION_FIX.md for troubleshooting"
    echo "2. Try manual installation: pip install <package>"
    echo "3. Run: python test_imports.py"
    echo ""
fi

echo -e "${GREEN}🚀 Happy Trading!${NC}"
echo ""

# Deactivate venv (optional)
# deactivate
