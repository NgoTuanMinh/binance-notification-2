# 🚀 Hướng dẫn Deployment

## 📋 Checklist trước khi deploy

### 📱 Platform-specific Guides

**🍎 macOS**: Xem `INSTALLATION_FIX.md` và chạy `./install_mac.sh`  
**🐧 Ubuntu/Linux**: Xem `UBUNTU_SETUP.md` và chạy `./install_ubuntu.sh`  
**🪟 Windows**: Manual installation (xem below)

### 1. Environment Setup
- [ ] Python 3.8+ đã cài đặt
- [ ] pip hoặc pip3 available
- [ ] Internet connection ổn định

### 2. Dependencies
```bash
pip install -r requirements.txt
```

Verify installation:
```bash
python -c "import ccxt, pandas, pandas_ta, aiohttp, dotenv; print('✅ All packages installed')"
```

### 3. Telegram Bot Setup

#### Bước 3.1: Tạo Bot
1. Mở Telegram, tìm **@BotFather**
2. Gửi: `/newbot`
3. Đặt tên bot (ví dụ: `My Crypto Scanner Bot`)
4. Đặt username (ví dụ: `my_crypto_scanner_bot`)
5. **Copy Bot Token** (dạng: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Bước 3.2: Lấy Chat ID
1. Mở bot vừa tạo và gửi: `/start`
2. Truy cập URL (thay `<TOKEN>` bằng bot token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. Tìm: `"chat":{"id":123456789,...}`
4. **Copy Chat ID** (số 123456789)

#### Bước 3.3: Cấu hình .env
```bash
cp .env.example .env
nano .env  # hoặc dùng editor khác
```

Điền:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 4. Test Setup
```bash
python test_setup.py
```

Kết quả mong đợi:
```
✅ Imports
✅ Config
✅ Binance Connection
✅ Data Fetching
✅ Strategy Engine
✅ Telegram Bot

🎉 TẤT CẢ TEST QUAN TRỌNG ĐÃ PASS!
```

---

## 🧪 Testing Phase

### Test 1: Single Scan (Khuyến nghị)
```bash
python main.py --once
```

Điều này sẽ:
- Quét H4 → tìm candidates
- Quét H1 → tìm watchlist
- Quét M15 → tìm signals
- Gửi signals (nếu có) qua Telegram

**Thời gian**: 2-5 phút tùy số lượng symbols

### Test 2: Test từng module
```bash
# Test market data
python market_data.py

# Test strategy
python strategy_engine.py

# Test telegram
python telegram_bot.py
```

---

## 🏃 Production Deployment

### Option 1: Chạy trực tiếp (Development/Testing)
```bash
python main.py
```

**Ưu điểm:**
- Đơn giản, dễ debug
- Thấy output real-time

**Nhược điểm:**
- Phải giữ terminal mở
- Dừng khi tắt máy/terminal

### Option 2: Screen/Tmux (Linux/Mac)

#### Sử dụng Screen
```bash
# Tạo session mới
screen -S crypto_bot

# Chạy bot
python main.py

# Detach: Ctrl+A, D
# Reattach: screen -r crypto_bot
# Kill: screen -X -S crypto_bot quit
```

#### Sử dụng Tmux
```bash
# Tạo session mới
tmux new -s crypto_bot

# Chạy bot
python main.py

# Detach: Ctrl+B, D
# Reattach: tmux attach -t crypto_bot
# Kill: tmux kill-session -t crypto_bot
```

### Option 3: Systemd Service (Linux Production) - RECOMMENDED

**🐧 Ubuntu/Debian Quick Setup:**
```bash
# Automatic setup (recommended)
./install_ubuntu.sh
# Script will ask if you want to setup systemd service

# Or use template manually
nano binance-bot.service.example
# Edit: Replace YOUR_USERNAME and paths
sudo cp binance-bot.service.example /etc/systemd/system/binance-bot.service
sudo systemctl daemon-reload
sudo systemctl enable binance-bot
sudo systemctl start binance-bot
```

**📖 Detailed Guide:** See `UBUNTU_SETUP.md`

#### Manual Setup

**Bước 1: Tạo service file**
```bash
sudo nano /etc/systemd/system/binance-bot.service
```

**Nội dung:**
```ini
[Unit]
Description=Binance Futures Scanner Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/Binance-2
Environment="PATH=/home/your_username/Binance-2/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/your_username/Binance-2/venv/bin/python /home/your_username/Binance-2/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/your_username/Binance-2/bot.log
StandardError=append:/home/your_username/Binance-2/bot.log

[Install]
WantedBy=multi-user.target
```

**Bước 2: Enable và start**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (tự động start khi boot)
sudo systemctl enable binance-bot

# Start service
sudo systemctl start binance-bot

# Check status
sudo systemctl status binance-bot

# View logs
sudo journalctl -u binance-bot -f
```

**Bước 3: Quản lý**
```bash
# Stop
sudo systemctl stop binance-bot

# Restart
sudo systemctl restart binance-bot

# Disable (không auto-start)
sudo systemctl disable binance-bot

# View logs (last 100 lines)
sudo journalctl -u binance-bot -n 100

# View logs (follow live)
sudo journalctl -u binance-bot -f
```

### Option 4: Docker (Advanced)

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  crypto-bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

#### Commands
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

### Option 5: Nohup (Simple Background)
```bash
# Start
nohup python main.py > bot.log 2>&1 &

# Get PID
ps aux | grep main.py

# Stop (thay <PID>)
kill <PID>

# View logs
tail -f bot.log
```

---

## 📊 Monitoring

### 1. Telegram Notifications
Bot tự động gửi:
- ✅ Startup message
- 📊 Hourly statistics
- 🎯 Trading signals
- ❌ Error alerts

### 2. Log Files (Nếu setup)
```bash
# Real-time logs
tail -f bot.log

# Search for errors
grep "❌" bot.log

# Count signals
grep "🎯 SIGNAL" bot.log | wc -l
```

### 3. System Resources
```bash
# Check CPU/Memory
top -p $(pgrep -f main.py)

# hoặc
htop
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Rate limit exceeded"
1. Tăng `REQUEST_DELAY_SECONDS` trong `.env`:
   ```env
   REQUEST_DELAY_SECONDS=1.0
   ```
2. Giảm `MAX_CONCURRENT_REQUESTS`:
   ```env
   MAX_CONCURRENT_REQUESTS=3
   ```

### Issue: "Telegram Bot Token invalid"
1. Verify token từ @BotFather
2. Đảm bảo không có khoảng trắng thừa trong `.env`
3. Test bằng:
   ```bash
   python telegram_bot.py
   ```

### Issue: "No symbols found"
1. Check internet connection
2. Verify Binance API accessible:
   ```bash
   curl https://fapi.binance.com/fapi/v1/exchangeInfo
   ```

### Issue: Bot crashes frequently
1. Check logs để tìm lỗi
2. Đảm bảo RAM đủ (khuyến nghị ≥2GB)
3. Check Python version (cần 3.8+)

---

## 🛡️ Security Best Practices

### 1. Environment Variables
- ❌ **KHÔNG** commit file `.env` lên Git
- ✅ **LUÔN** sử dụng `.env.example` làm template
- ✅ Giữ `.env` trong `.gitignore`

### 2. Server Security
```bash
# Update system
sudo apt update && sudo apt upgrade

# Firewall (nếu cần)
sudo ufw allow ssh
sudo ufw enable

# Fail2ban (tùy chọn)
sudo apt install fail2ban
```

### 3. Backup
```bash
# Backup .env
cp .env .env.backup

# Backup toàn bộ project
tar -czf crypto-bot-backup-$(date +%Y%m%d).tar.gz Binance-2/
```

---

## 📈 Performance Optimization

### 1. Symbol Filtering (Khuyến nghị cho testing/development) ⭐

**Trong file `.env`:**
```env
# Option 1: Quét tất cả (production)
MAX_SYMBOLS_TO_SCAN=

# Option 2: Top 50 symbols (development/testing)
MAX_SYMBOLS_TO_SCAN=50

# Option 3: Top 100 symbols (production với ít coins)
MAX_SYMBOLS_TO_SCAN=100

# Sắp xếp theo volume để lấy coins có thanh khoản cao
SYMBOL_SORT_METHOD=volume
```

**Impact:**
| Symbols | H4 Time | API/hour | Use Case |
|---------|---------|----------|----------|
| 10 | ~30s | ~100 | Quick testing |
| 50 | ~2 min | ~250 | Development |
| 100 | ~4 min | ~450 | Production (focused) |
| All (~300) | ~10 min | ~800 | Production (full) |

### 2. Tối ưu chu kỳ quét (config.py hoặc .env)
```python
# Cho thị trường ít biến động
SCAN_INTERVAL_H4 = 7200   # 2 giờ thay vì 1 giờ
SCAN_INTERVAL_M15 = 180   # 3 phút thay vì 2 phút

# Cho thị trường biến động cao
SCAN_INTERVAL_M15 = 60    # 1 phút để catch nhanh hơn
```

### 3. Optimize rate limiting
```python
# Nếu không bị rate limit
MAX_CONCURRENT_REQUESTS = 10  # Tăng từ 5
REQUEST_DELAY_SECONDS = 0.3   # Giảm từ 0.5
```

### 4. Recommended Configurations

#### For Testing/Development
```env
MAX_SYMBOLS_TO_SCAN=20
SCAN_INTERVAL_M15=180
MAX_CONCURRENT_REQUESTS=3
```

#### For Production (Focused)
```env
MAX_SYMBOLS_TO_SCAN=100
SCAN_INTERVAL_H4=3600
SCAN_INTERVAL_M15=120
MAX_CONCURRENT_REQUESTS=5
```

#### For Production (Full Coverage)
```env
MAX_SYMBOLS_TO_SCAN=
SCAN_INTERVAL_H4=3600
SCAN_INTERVAL_M15=120
MAX_CONCURRENT_REQUESTS=5
```

---

## 📞 Support & Maintenance

### Regular Checks (Khuyến nghị)
- **Hàng ngày**: Check Telegram có nhận signals không
- **Hàng tuần**: Review hourly stats, optimize parameters
- **Hàng tháng**: Update dependencies, backup data

### Update Dependencies
```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade ccxt

# Update all
pip install --upgrade -r requirements.txt
```

### Git Updates (Nếu có updates)
```bash
# Backup current .env
cp .env .env.backup

# Pull updates
git pull origin main

# Restore .env
cp .env.backup .env

# Reinstall dependencies (if needed)
pip install -r requirements.txt

# Restart bot
```

---

## ✅ Deployment Checklist

Trước khi deploy production:

- [ ] Đã test với `python main.py --once`
- [ ] Đã chạy `test_setup.py` và tất cả pass
- [ ] Đã nhận được test message từ Telegram
- [ ] Đã backup file `.env`
- [ ] Đã setup monitoring (logs, Telegram notifications)
- [ ] Đã đọc và hiểu cách stop/restart bot
- [ ] Đã chuẩn bị plan để handle errors
- [ ] Đã set reasonable expectations (không phải lúc nào cũng có signals)

---

## 🎓 Production Tips

1. **Kiên nhẫn**: Chiến lược nghiêm ngặt, có thể vài giờ mới có 1 signal
2. **Monitor**: Check Telegram hourly stats để biết bot còn chạy
3. **Don't overtrade**: Không phải signal nào cũng vào lệnh
4. **Risk management**: Luôn đặt SL, chỉ risk 1-2% mỗi lệnh
5. **Keep learning**: Theo dõi signals để hiểu strategy behavior

---

## 📚 Additional Resources

- **README.md**: Full documentation
- **FEATURES.md**: Detailed features explanation
- **SUMMARY.md**: Project overview
- **QUICKSTART.md**: 5-minute quick start

---

**Ready to deploy? Good luck and happy trading! 🚀📈**
