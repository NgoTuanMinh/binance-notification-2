# 🤖 Binance Futures Public Scanner

Bot quét thị trường Binance Futures tự động để tìm cơ hội giao dịch theo chiến lược đa khung thời gian (Multi-Timeframe Analysis).

## 🔒 Bảo mật & Quyền riêng tư

Bot sử dụng **BINANCE_API_KEY** và **BINANCE_SECRET_KEY** với ccxt để lấy dữ liệu (load_markets, OHLCV, tickers). **Khuyến nghị:** Tạo API Key trên Binance với quyền **chỉ đọc (Read)**; không bật quyền giao dịch (Trade) hay rút tiền (Withdraw) để giảm rủi ro.

## 📊 Chiến lược giao dịch

Bot sử dụng phễu lọc 3 bước từ khung lớn đến khung nhỏ với **3 luồng quét độc lập**:

### Bước 1: H4 - Trend Filter (Quét mỗi 1 giờ)
- ✅ Giá nằm **trên/dưới EMA 200**
- ✅ Cấu trúc **Higher High/Higher Low** (hoặc Lower High/Lower Low)
- 📤 Output: **Candidate_Symbols** với trend direction

### Bước 2: H1 - Value Zone (Quét mỗi 15 phút cho Candidates)
- ✅ Pullback về **Fibonacci 0.5-0.618** của sóng H4
- ✅ HOẶC chạm **EMA 20/50** trên H1
- 📤 Output: **Hot_Watchlist** sẵn sàng vào lệnh

### Bước 3: M15 - Entry Signal (Quét mỗi 1-3 phút cho Watchlist)
- ✅ **Candlestick Patterns**: Bullish/Bearish Engulfing, Pinbar, Shooting Star
- ✅ **RSI Divergence** (tùy chọn để tăng độ tin cậy)
- ✅ **Volume Confirmation**: Volume > trung bình 20 nến (BẮT BUỘC)
- 📤 Output: **Trading Signals** gửi Telegram

## 🚀 Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.8 trở lên
- Kết nối Internet ổn định

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Telegram Bot

1. Tạo bot Telegram mới:
   - Mở Telegram và tìm `@BotFather`
   - Gửi lệnh `/newbot` và làm theo hướng dẫn
   - Lưu lại **Bot Token** (dạng: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. Lấy Chat ID:
   - Mở bot vừa tạo và gửi một tin nhắn bất kỳ
   - Truy cập: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Tìm giá trị `"id"` trong `"chat"` (dạng: `123456789`)

3. Tạo file `.env`:

```bash
cp .env.example .env
```

4. Mở file `.env` và điền thông tin:

```env
# Telegram (bắt buộc)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Binance (bắt buộc cho ccxt)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

**Lưu ý:** Bot dùng ccxt với API Key/Secret Binance để lấy dữ liệu (load_markets, OHLCV, tickers). Chỉ cần quyền đọc (Read) là đủ; không cần quyền giao dịch.

## 📖 Sử dụng

### Chạy bot liên tục (Production)

```bash
python main.py
```

Bot sẽ chạy **3 luồng quét độc lập song song**:
- 🔵 **H4 Loop**: Quét mỗi 1 giờ - lọc trend
- 🟢 **H1 Loop**: Quét mỗi 15 phút - tìm value zone
- 🟡 **M15 Loop**: Quét mỗi 2 phút - tìm entry signals
- 📊 **Stats Reporter**: Báo cáo thống kê mỗi giờ

### Chạy một lần (Testing)

```bash
python main.py --once
```

Hữu ích để test cấu hình và xem kết quả ngay lập tức.

### Test từng module riêng

```bash
# Test market data fetching
python market_data.py

# Test strategy engine
python strategy_engine.py

# Test Telegram bot
python telegram_bot.py
```

## 📁 Cấu trúc dự án

```
Binance-2/
├── main.py                 # File chính - orchestration
├── market_data.py          # Lấy dữ liệu OHLCV từ Binance
├── strategy_engine.py      # Logic chiến lược MTF
├── telegram_bot.py         # Gửi thông báo qua Telegram
├── config.py              # Cấu hình và biến môi trường
├── requirements.txt       # Python dependencies
├── .env.example          # Template file môi trường
├── .env                  # File môi trường (TỰ TẠO)
├── README.md             # Tài liệu này
└── PROJECT_SPEC.md       # Đặc tả dự án chi tiết
```

## ⚙️ Tùy chỉnh

### Điều chỉnh tham số trong `config.py` hoặc `.env`:

```python
# Thay đổi chu kỳ quét (giây)
SCAN_INTERVAL_H4 = 3600   # H4: 1 giờ
SCAN_INTERVAL_H1 = 900    # H1: 15 phút
SCAN_INTERVAL_M15 = 120   # M15: 2 phút

# Giới hạn số symbols để tối ưu performance
MAX_SYMBOLS_TO_SCAN = None  # None = tất cả, hoặc số (ví dụ: 50, 100)
SYMBOL_SORT_METHOD = 'volume'  # 'volume' hoặc 'alphabetical'

# Thay đổi chỉ báo kỹ thuật
EMA_TREND = 200      # EMA cho H4
EMA_VALUE_FAST = 20  # EMA nhanh cho H1
EMA_VALUE_SLOW = 50  # EMA chậm cho H1

# Fibonacci levels
FIB_LEVEL_MIN = 0.5    # Min Fib level
FIB_LEVEL_MAX = 0.618  # Max Fib level

# Volume confirmation
VOLUME_MA_PERIOD = 20      # Volume MA period
VOLUME_MULTIPLIER = 1.0    # Min volume ratio

# Pattern parameters
PINBAR_WICK_RATIO = 0.6      # Pinbar wick >= 60%
ENGULFING_BODY_RATIO = 1.0   # Full engulfing

# Điều chỉnh rate limiting
MAX_CONCURRENT_REQUESTS = 5  # Số request đồng thời
REQUEST_DELAY_SECONDS = 0.5  # Độ trễ giữa các request
```

### Tối ưu Performance với Symbol Filtering

Để giảm thời gian quét và API calls, bạn có thể giới hạn số lượng symbols:

**Trong file `.env`:**
```env
# Quét tất cả symbols (mặc định)
MAX_SYMBOLS_TO_SCAN=

# Hoặc giới hạn top 50 symbols có volume cao nhất
MAX_SYMBOLS_TO_SCAN=50

# Hoặc top 100
MAX_SYMBOLS_TO_SCAN=100

# Phương pháp sắp xếp
SYMBOL_SORT_METHOD=volume  # 'volume' (khuyến nghị) hoặc 'alphabetical'
```

**Lợi ích:**
- ✅ Giảm thời gian quét (50 symbols ~2-3 phút vs 300 symbols ~10-15 phút)
- ✅ Giảm API calls
- ✅ Focus vào các cặp có thanh khoản cao (khi dùng sort by volume)
- ✅ Phù hợp cho testing và development

## 🔧 Xử lý sự cố

### Lỗi: "TELEGRAM_BOT_TOKEN is not set"
- Kiểm tra file `.env` đã được tạo chưa
- Đảm bảo các giá trị trong `.env` không có dấu ngoặc kép

### Lỗi: Rate limit exceeded
- Tăng `REQUEST_DELAY_SECONDS` trong `.env`
- Giảm `MAX_CONCURRENT_REQUESTS` trong `.env`

### Bot không tìm thấy tín hiệu
- Điều này là bình thường! Chiến lược có bộ lọc nghiêm ngặt
- Thị trường cần có điều kiện phù hợp mới xuất hiện tín hiệu
- Hãy kiên nhẫn và để bot chạy liên tục

### Kiểm tra kết nối Telegram
```bash
python telegram_bot.py
```

Nếu thành công, bạn sẽ nhận được tin nhắn test.

## 📊 Hiệu suất & Tối ưu

Bot sử dụng **3 luồng quét độc lập** với chu kỳ khác nhau:

### Kiến trúc thông minh:
- 🔵 **H4**: Quét 300 symbols mỗi 1 giờ → ~50 candidates
- 🟢 **H1**: Quét 50 candidates mỗi 15 phút → ~10 watchlist
- 🟡 **M15**: Quét 10 watchlist mỗi 2 phút → 0-5 signals

### So với quét tuần tự mỗi 15 phút:
- **Trước**: 300 × 3 × 4 = **3,600 requests/giờ**
- **Sau**: 300 + (50×4) + (10×30) = **800 requests/giờ**
- **Tiết kiệm: 78% API calls!**

### Lợi ích:
- ✅ Tránh bị Binance rate limit/ban IP
- ✅ Phát hiện tín hiệu nhanh hơn (M15 quét 2 phút 1 lần)
- ✅ Tối ưu tài nguyên hệ thống
- ✅ Độ chính xác cao hơn (lọc kỹ từng bước)

## ⚠️ Disclaimer

- Bot này chỉ cung cấp **tín hiệu tham khảo**
- **KHÔNG** phải lời khuyên tài chính
- Luôn thực hiện nghiên cứu riêng (DYOR)
- Quản lý rủi ro cẩn thận
- Chỉ giao dịch với số tiền bạn có thể chấp nhận mất

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo Pull Request hoặc mở Issue nếu bạn có ý tưởng cải thiện.

---

**Happy Trading! 🚀📈**
