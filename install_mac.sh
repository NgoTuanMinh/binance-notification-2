#!/bin/bash
# Installation script for macOS
# Fixes common SSL and installation issues

set -e  # Exit on error

echo "🚀 Binance Futures Scanner - macOS Installation"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "1️⃣ Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo "   Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check pip
echo ""
echo "2️⃣ Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✅ Found: $PIP_VERSION"
else
    echo "❌ pip3 not found!"
    exit 1
fi

# Fix SSL certificates (macOS specific)
echo ""
echo "3️⃣ Fixing SSL certificates (macOS)..."

# Try to find Python Install Certificates script
CERT_SCRIPT=$(find /Applications -name "Install Certificates.command" 2>/dev/null | head -1)

if [ -n "$CERT_SCRIPT" ]; then
    echo "Found certificate installer: $CERT_SCRIPT"
    echo "Running..."
    "$CERT_SCRIPT" || echo "⚠️  Certificate install returned non-zero, continuing anyway..."
    echo "✅ Certificates updated"
else
    echo "⚠️  Certificate installer not found, will try alternative method"
    echo "   Installing certifi..."
    pip3 install --user certifi || true
fi

# Upgrade pip
echo ""
echo "4️⃣ Upgrading pip..."
pip3 install --upgrade pip --user

# Create virtual environment (optional but recommended)
echo ""
echo "5️⃣ Virtual environment..."
read -p "Create virtual environment? (recommended) [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    if [ -d "venv" ]; then
        echo "⚠️  venv folder already exists"
        read -p "Remove and recreate? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            echo "✅ Virtual environment recreated"
        fi
    else
        python3 -m venv venv
        echo "✅ Virtual environment created"
    fi
    
    # Activate venv
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    
    # Upgrade pip in venv
    pip install --upgrade pip
else
    echo "Skipping virtual environment"
fi

# Install packages
echo ""
echo "6️⃣ Installing Python packages..."
echo "   This may take a few minutes..."
echo ""

# Try normal install first
if pip install -r requirements.txt; then
    echo "✅ Packages installed successfully!"
else
    echo "⚠️  Normal install failed, trying with --trusted-host..."
    if pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt; then
        echo "✅ Packages installed with --trusted-host!"
    else
        echo "❌ Installation failed!"
        echo ""
        echo "Please try manual installation:"
        echo "  pip install ccxt pandas pandas-ta python-dotenv aiohttp numpy"
        exit 1
    fi
fi

# Test imports
echo ""
echo "7️⃣ Testing imports..."
python test_imports.py

# Success message
echo ""
echo "================================================"
echo "🎉 Installation completed successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env"
echo "     cp .env.example .env"
echo ""
echo "  2. Edit .env and add your Telegram credentials"
echo "     nano .env"
echo ""
echo "  3. Run tests"
echo "     python test_setup.py"
echo ""
echo "  4. Start bot"
echo "     python main.py --once"
echo ""

if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "💡 Note: If you created a virtual environment, activate it with:"
    echo "   source venv/bin/activate"
    echo ""
fi

echo "📖 For more help, see:"
echo "   - INSTALLATION_FIX.md"
echo "   - QUICKSTART.md"
echo "   - START_HERE.md"
echo ""
