# 🐧 Ubuntu Server Setup Guide

Hướng dẫn cài đặt bot trên Ubuntu 22.04 LTS

---

## ⚡ Quick Install (1 command)

```bash
# Upload code lên server, sau đó:
cd /path/to/Binance-2
chmod +x install_ubuntu.sh
./install_ubuntu.sh
```

Script sẽ tự động:
- ✅ Update system packages
- ✅ Cài Python 3.8+ (nếu chưa có)
- ✅ Cài system dependencies
- ✅ Tạo virtual environment
- ✅ Cài tất cả Python packages
- ✅ Test imports
- ✅ Setup systemd service (optional)

---

## 📋 Step by Step Manual Installation

### Bước 1: Update system
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Bước 2: Cài Python và dependencies
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl
```

### Bước 3: Upload code lên server

**Option A: Git (nếu có repo)**
```bash
git clone <your-repo-url>
cd Binance-2
```

**Option B: SCP (upload từ máy local)**
```bash
# Trên máy local
scp -r /path/to/Binance-2 user@your-server:/home/user/

# SSH vào server
ssh user@your-server
cd ~/Binance-2
```

**Option C: SFTP hoặc file manager**
- Dùng FileZilla, WinSCP, hoặc VS Code Remote

### Bước 4: Setup Virtual Environment
```bash
cd Binance-2
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Bước 5: Cài packages
```bash
pip install -r requirements.txt
```

### Bước 6: Configure
```bash
# Copy template
cp .env.example .env

# Edit config
nano .env
# Add:
# TELEGRAM_BOT_TOKEN=your_token
# TELEGRAM_CHAT_ID=your_chat_id
# MAX_SYMBOLS_TO_SCAN=50  (optional, for faster testing)
```

### Bước 7: Test
```bash
# Test imports
python test_imports.py

# Test setup
python test_setup.py

# Test run
python main.py --once
```

---

## 🚀 Running the Bot

### Option 1: Direct Run (for testing)
```bash
source venv/bin/activate
python main.py
```

### Option 2: Screen (simple background)
```bash
# Install screen
sudo apt-get install screen

# Create screen session
screen -S crypto-bot

# Run bot
source venv/bin/activate
python main.py

# Detach: Ctrl+A, D
# Reattach: screen -r crypto-bot
# Kill: screen -X -S crypto-bot quit
```

### Option 3: Systemd Service (recommended for production)

#### Create service file:
```bash
sudo nano /etc/systemd/system/binance-bot.service
```

#### Add content:
```ini
[Unit]
Description=Binance Futures Scanner Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Binance-2
Environment="PATH=/home/YOUR_USERNAME/Binance-2/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/YOUR_USERNAME/Binance-2/venv/bin/python /home/YOUR_USERNAME/Binance-2/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/Binance-2/bot.log
StandardError=append:/home/YOUR_USERNAME/Binance-2/bot.log

[Install]
WantedBy=multi-user.target
```

**Note:** Thay `YOUR_USERNAME` bằng username của bạn

#### Enable và start:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (auto-start on boot)
sudo systemctl enable binance-bot

# Start service
sudo systemctl start binance-bot

# Check status
sudo systemctl status binance-bot

# View logs
sudo journalctl -u binance-bot -f

# Stop service
sudo systemctl stop binance-bot

# Restart service
sudo systemctl restart binance-bot
```

---

## 📦 Quản lý service Python (kiểu PM2)

Trên Ubuntu không có PM2 mặc định, nhưng có thể dùng các cách sau để quản lý bot giống PM2 (start/stop/restart, auto-restart, xem log).

| Cách | Giống PM2 | Ghi chú |
|------|-----------|--------|
| **systemd** | ✅ | Có sẵn trên Ubuntu, dùng lệnh `systemctl` (đã hướng dẫn ở Option 3 trên). |
| **Supervisor** | ✅✅ | CLI gần giống PM2: `supervisorctl start/stop/restart`, xem log, nhiều process. |
| **PM2** | ✅✅✅ | Cài Node.js + PM2, chạy được cả Python: `pm2 start main.py --interpreter python3`. |

### Dùng systemd (đã setup ở Option 3)

Lệnh tương ứng PM2:

```bash
# PM2          →  systemd
# pm2 start    →  sudo systemctl start binance-bot
# pm2 stop     →  sudo systemctl stop binance-bot
# pm2 restart  →  sudo systemctl restart binance-bot
# pm2 status   →  sudo systemctl status binance-bot
# pm2 logs     →  sudo journalctl -u binance-bot -f
# pm2 save     →  sudo systemctl enable binance-bot   (auto-start khi reboot)
```

### Dùng Supervisor (giống PM2, nhiều app)

**Cài đặt:**
```bash
sudo apt-get update
sudo apt-get install -y supervisor
```

**Tạo config:**
```bash
sudo nano /etc/supervisor/conf.d/binance-bot.conf
```

**Nội dung (sửa path và user):**
```ini
[program:binance-bot]
command=/home/YOUR_USERNAME/Binance-2/venv/bin/python /home/YOUR_USERNAME/Binance-2/main.py
directory=/home/YOUR_USERNAME/Binance-2
user=YOUR_USERNAME
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/YOUR_USERNAME/Binance-2/bot.log
environment=PATH="/home/YOUR_USERNAME/Binance-2/venv/bin"
```

**Quản lý (giống pm2):**
```bash
# Reload config sau khi sửa file
sudo supervisorctl reread
sudo supervisorctl update

# Start / Stop / Restart
sudo supervisorctl start binance-bot
sudo supervisorctl stop binance-bot
sudo supervisorctl restart binance-bot

# Trạng thái tất cả app
sudo supervisorctl status

# Xem log realtime
sudo supervisorctl tail -f binance-bot stdout
```

### Dùng PM2 cho Python (nếu đã quen PM2)

**Cài Node.js + PM2:**
```bash
# Cài Node.js (nvm hoặc package)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Cài PM2 global
sudo npm install -g pm2
```

**Chạy bot Python bằng PM2:**
```bash
cd /path/to/Binance-2

# Chạy bằng python trong venv
pm2 start main.py --name binance-bot --interpreter ./venv/bin/python

# Hoặc dùng script shell (tạo start.sh rồi: pm2 start start.sh --name binance-bot)
# Nội dung start.sh (sửa path):
#   #!/bin/bash
#   cd /path/to/Binance-2 && source venv/bin/activate && exec python main.py
```

**Lệnh quen thuộc:**
```bash
pm2 list
pm2 logs binance-bot
pm2 restart binance-bot
pm2 stop binance-bot
pm2 save && pm2 startup   # auto-start khi reboot
```

---

## 🔒 Security Best Practices

### 1. Firewall
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (IMPORTANT!)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Check status
sudo ufw status
```

### 2. Fail2Ban (prevent brute force)
```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Keep system updated
```bash
# Setup automatic updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4. Secure .env file
```bash
# Set proper permissions
chmod 600 .env

# Never commit to git
echo ".env" >> .gitignore
```

### 5. Create dedicated user (optional)
```bash
# Create user for bot
sudo adduser botuser

# Switch to bot user
su - botuser

# Install in bot user's home
cd /home/botuser
# ... continue installation
```

---

## 📊 Monitoring

### 1. Check bot is running
```bash
# If using systemd
sudo systemctl status binance-bot

# If using screen
screen -ls
```

### 2. View logs
```bash
# Systemd logs
sudo journalctl -u binance-bot -f

# Or direct log file
tail -f bot.log
```

### 3. Check resources
```bash
# CPU and Memory
htop

# Or specific process
ps aux | grep python
```

### 4. Test connectivity
```bash
# Test Binance API
curl https://fapi.binance.com/fapi/v1/ping

# Test Telegram
curl https://api.telegram.org/botYOUR_TOKEN/getMe
```

---

## 🔧 Troubleshooting

### Bot không start
```bash
# Check logs
sudo journalctl -u binance-bot -n 50

# Check permissions
ls -la /home/user/Binance-2

# Test manually
source venv/bin/activate
python main.py --once
```

### Lỗi module not found
```bash
# Activate venv
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt

# Test imports
python test_imports.py
```

### Lỗi Permission denied
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/Binance-2

# Fix permissions
chmod -R 755 /path/to/Binance-2
chmod 600 .env
```

### Bot stops after a while
```bash
# Check memory
free -h

# Check disk space
df -h

# Check logs for errors
tail -100 bot.log
```

---

## 📦 Backup và Update

### Backup
```bash
# Backup .env
cp .env .env.backup

# Backup entire project
tar -czf binance-bot-backup-$(date +%Y%m%d).tar.gz Binance-2/
```

### Update code
```bash
# Stop bot
sudo systemctl stop binance-bot

# Backup
cp .env .env.backup

# Pull updates (if using git)
git pull

# Or upload new files via SCP

# Restore config
cp .env.backup .env

# Reinstall packages (if requirements changed)
source venv/bin/activate
pip install -r requirements.txt

# Restart bot
sudo systemctl start binance-bot
```

---

## 💡 Performance Tips

### 1. Symbol filtering (faster testing)
```bash
# In .env
MAX_SYMBOLS_TO_SCAN=50
SYMBOL_SORT_METHOD=volume
```

### 2. Adjust scan intervals
```bash
# For slower markets
SCAN_INTERVAL_H4=7200   # 2 hours
SCAN_INTERVAL_M15=180   # 3 minutes
```

### 3. Monitor resources
```bash
# Install monitoring tools
sudo apt-get install htop iotop

# Monitor
htop
```

---

## 🌐 Remote Access

### SSH with key (more secure)
```bash
# On local machine, generate key
ssh-keygen -t ed25519

# Copy to server
ssh-copy-id user@your-server

# Now you can SSH without password
ssh user@your-server
```

### VS Code Remote
1. Install "Remote - SSH" extension
2. Connect to server
3. Open project folder
4. Edit and run directly on server

---

## 📞 Quick Commands Reference

```bash
# Start bot
sudo systemctl start binance-bot

# Stop bot
sudo systemctl stop binance-bot

# Restart bot
sudo systemctl restart binance-bot

# Check status
sudo systemctl status binance-bot

# View logs (live)
sudo journalctl -u binance-bot -f

# View logs (last 100 lines)
sudo journalctl -u binance-bot -n 100

# Enable auto-start on boot
sudo systemctl enable binance-bot

# Disable auto-start
sudo systemctl disable binance-bot

# Test run manually
source venv/bin/activate
python main.py --once

# Test imports
python test_imports.py

# Update system
sudo apt-get update && sudo apt-get upgrade
```

---

## 📖 Additional Resources

- **START_HERE.md** - Quick start guide
- **DEPLOYMENT.md** - Detailed deployment options
- **INSTALLATION_FIX.md** - Troubleshooting
- **README.md** - Full documentation

---

## ✅ Checklist

- [ ] Ubuntu 22.04 LTS server
- [ ] SSH access
- [ ] Python 3.8+ installed
- [ ] Code uploaded to server
- [ ] Virtual environment created
- [ ] Packages installed
- [ ] .env configured with Telegram credentials
- [ ] test_setup.py passed
- [ ] Bot runs with `python main.py --once`
- [ ] Systemd service configured (optional)
- [ ] Firewall configured
- [ ] Monitoring setup

---

**🚀 Ready to deploy! Good luck!**
