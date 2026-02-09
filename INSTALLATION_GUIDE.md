# 📦 Installation Guide - All Platforms

Quick links to platform-specific installation guides.

---

## 🎯 Choose Your Platform

### 🍎 macOS

**Quick Install:**
```bash
./install_mac.sh
```

**Documentation:**
- `install_mac.sh` - Automated installation script
- `INSTALLATION_FIX.md` - Troubleshooting for macOS
- `QUICK_FIX.txt` - Quick reference commands

**Common Issues:**
- SSL Certificate errors → Fixed by script automatically
- pandas-ta version → Fixed in requirements.txt

---

### 🐧 Ubuntu / Linux Server

**Quick Install:**
```bash
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

**Documentation:**
- `install_ubuntu.sh` - Automated installation script (150 lines)
- `UBUNTU_SETUP.md` - Complete Ubuntu guide
- `UBUNTU_QUICKSTART.txt` - Quick reference card
- `binance-bot.service.example` - Systemd service template

**Features:**
- ✅ Automatic system dependency installation
- ✅ Virtual environment setup
- ✅ Python package installation
- ✅ Systemd service configuration (optional)
- ✅ Security hardening tips

---

### 🪟 Windows

**Manual Installation:**

1. **Install Python 3.8+**
   - Download from https://python.org
   - Check "Add Python to PATH"

2. **Open PowerShell/CMD in project folder**
   ```powershell
   # Create virtual environment
   python -m venv venv
   
   # Activate
   venv\Scripts\activate
   
   # Install packages
   pip install -r requirements.txt
   ```

3. **Configure**
   ```powershell
   copy .env.example .env
   notepad .env
   # Add Telegram credentials
   ```

4. **Run**
   ```powershell
   python main.py --once
   ```

**Documentation:**
- `INSTALLATION_FIX.md` - Some tips may apply
- `README.md` - General documentation

---

## 🧪 Test Installation

After installation, verify everything works:

```bash
# Test imports
python test_imports.py

# Test full setup
python test_setup.py

# Test bot (single run)
python main.py --once
```

Expected output:
```
✅ All packages installed successfully!
✅ Telegram bot connected
✅ Binance API accessible
```

---

## 📁 Installation Files Reference

| File | Platform | Description |
|------|----------|-------------|
| `install_mac.sh` | 🍎 macOS | Automated installer for Mac |
| `install_ubuntu.sh` | 🐧 Ubuntu | Automated installer for Ubuntu |
| `requirements.txt` | All | Python packages list |
| `.env.example` | All | Configuration template |
| `test_imports.py` | All | Test if packages installed |
| `test_setup.py` | All | Test full system setup |
| `binance-bot.service.example` | 🐧 Linux | Systemd service template |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `START_HERE.md` | Main starting point |
| `QUICKSTART.md` | 5-minute quick setup |
| `INSTALLATION_GUIDE.md` | This file - platform overview |
| `INSTALLATION_FIX.md` | macOS troubleshooting |
| `UBUNTU_SETUP.md` | Complete Ubuntu guide |
| `UBUNTU_QUICKSTART.txt` | Ubuntu quick reference |
| `QUICK_FIX.txt` | macOS quick reference |
| `DEPLOYMENT.md` | Production deployment guide |
| `README.md` | Full documentation |

---

## 🚀 Quick Start by Platform

### macOS (Local Development)
```bash
./install_mac.sh
cp .env.example .env
nano .env  # Add Telegram credentials
python main.py --once
```

### Ubuntu Server (Production)
```bash
./install_ubuntu.sh
cp .env.example .env
nano .env  # Add Telegram credentials
sudo systemctl start binance-bot
sudo systemctl enable binance-bot
```

### Windows (Local Development)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
python main.py --once
```

---

## 🔧 Common Post-Installation Tasks

### 1. Configure Telegram
```bash
# Get Bot Token from @BotFather
# Get Chat ID from your bot

# Edit .env
nano .env
# Add:
# TELEGRAM_BOT_TOKEN=your_token
# TELEGRAM_CHAT_ID=your_chat_id
```

### 2. Optimize Performance (Optional)
```bash
# Edit .env
nano .env
# Add for faster testing:
# MAX_SYMBOLS_TO_SCAN=50
# SYMBOL_SORT_METHOD=volume
```

### 3. Test Configuration
```bash
# Test Telegram
python telegram_bot.py

# Test full setup
python test_setup.py

# Test single scan
python main.py --once
```

---

## 💡 Tips

### For Development (Local Machine)
- Use `--once` flag for testing
- Set `MAX_SYMBOLS_TO_SCAN=20` for quick tests
- Use virtual environment always

### For Production (Server)
- Use systemd service (Linux)
- Set up monitoring
- Configure firewall
- Enable auto-start on boot
- Keep system updated

### For Testing New Features
- Create separate virtual environment
- Test with `MAX_SYMBOLS_TO_SCAN=10`
- Use `main.py --once` first

---

## 🆘 Get Help

1. **Read platform-specific guide**
   - macOS: `INSTALLATION_FIX.md`
   - Ubuntu: `UBUNTU_SETUP.md`

2. **Run test scripts**
   ```bash
   python test_imports.py
   python test_setup.py
   ```

3. **Check common issues**
   - SSL errors → Run install script
   - Module not found → Reinstall packages
   - Permission denied → Check file permissions

4. **View logs**
   - Console output
   - `bot.log` file
   - Systemd logs: `sudo journalctl -u binance-bot -f`

---

## ✅ Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Packages installed (`test_imports.py` passes)
- [ ] `.env` file configured with Telegram credentials
- [ ] Optional: Symbol filtering configured
- [ ] `test_setup.py` passes
- [ ] Bot runs with `python main.py --once`
- [ ] Production: Systemd service configured (Linux)
- [ ] Production: Firewall configured
- [ ] Production: Monitoring setup

---

**Choose your platform above and follow the guide. Happy trading! 🚀**
