# 🚀 Quick Start Guide

Hướng dẫn nhanh để chạy bot trong 5 phút!

## Bước 1: Cài đặt Python packages

```bash
pip install -r requirements.txt
```

## Bước 2: Tạo Telegram Bot

1. Mở Telegram, tìm `@BotFather`
2. Gửi: `/newbot`
3. Đặt tên bot theo hướng dẫn
4. **Lưu Bot Token** (dạng: `123456:ABC-DEF...`)

## Bước 3: Lấy Chat ID

1. Mở bot vừa tạo và gửi tin nhắn: `/start`
2. Truy cập URL này (thay `<YOUR_BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Tìm số `"id"` trong phần `"chat"` (ví dụ: `123456789`)

## Bước 4: Cấu hình môi trường

```bash
# Copy file mẫu
cp .env.example .env

# Mở file .env và điền thông tin
# TELEGRAM_BOT_TOKEN=paste_bot_token_here
# TELEGRAM_CHAT_ID=paste_chat_id_here
```

### 💡 Tùy chọn: Giới hạn symbols để test nhanh hơn

Nếu bạn muốn test nhanh hoặc chỉ quan tâm đến top coins:

```env
# Trong file .env, thêm dòng này:
MAX_SYMBOLS_TO_SCAN=50

# Hoặc để trống để quét tất cả (mặc định)
MAX_SYMBOLS_TO_SCAN=
```

**Lợi ích:**
- 🚀 Test nhanh hơn (50 symbols ~2-3 phút thay vì 10-15 phút)
- 🎯 Focus vào coins có volume cao
- 💰 Tiết kiệm API calls

## Bước 5: Test cài đặt

```bash
python test_setup.py
```

Nếu tất cả đều ✅, bạn đã sẵn sàng!

## Bước 6: Chạy bot

### Chạy một lần để test (khuyến nghị cho lần đầu)

```bash
python main.py --once
```

Bot sẽ chạy 1 chu kỳ hoàn chỉnh: H4 → H1 → M15

### Chạy liên tục (production mode)

```bash
python main.py
```

Bot sẽ chạy **3 luồng độc lập song song**:
- 🔵 **H4 Loop**: Quét mỗi 1 giờ để lọc trend
- 🟢 **H1 Loop**: Quét mỗi 15 phút để tìm value zone
- 🟡 **M15 Loop**: Quét mỗi 2 phút để tìm entry signal
- 📊 **Stats**: Báo cáo thống kê mỗi giờ

Bot sẽ tự động:
- Gửi tín hiệu qua Telegram khi tìm thấy cơ hội
- Báo cáo thống kê định kỳ
- Chạy cho đến khi bạn dừng (Ctrl+C)

## 🎯 Hiểu kết quả

Khi bot tìm thấy tín hiệu, bạn sẽ nhận được tin nhắn dạng:

```
🟢 TÍN HIỆU LONG 🟢

📊 Cặp: BTC/USDT
💰 Giá Entry: 45000.0000
🛑 Stop Loss: 44500.0000 (1.11%)
🎯 Take Profit: 46000.0000 (2.22%)
📈 R:R Ratio: 1:2.00

⏰ Khung thời gian: M15
🔍 Pattern: Bullish Engulfing

📌 Lý do:
H4 trend BULLISH with HH/HL structure, 
H1 Fibonacci 0.618 zone, 
M15 Bullish Engulfing, 
Volume 1.5x

📊 Chỉ báo:
• H4 EMA200: 43000.0000
• H1 EMA20: 44800.0000
• H1 EMA50: 44600.0000
• RSI(14): 45.50
• Volume: 1.50x trung bình
• Fibonacci: 0.618 level
• Giá hiện tại: 45000.0000
```

**Giải thích các điều kiện:**
- ✅ H4: Trend tăng + cấu trúc HH/HL (Higher High/Higher Low)
- ✅ H1: Pullback về vùng Fibonacci 0.618 (hoặc EMA20/50)
- ✅ M15: Nến Engulfing + Volume cao
- 📊 RSI Divergence (nếu có) tăng độ tin cậy

## ⚠️ Lưu ý quan trọng

1. **Bảo mật**: Bot chỉ dùng Public API, không cần Binance API Key
2. **Tín hiệu**: Chỉ là tham khảo, không phải lời khuyên đầu tư
3. **Kiên nhẫn**: Chiến lược khắt khe, không phải lúc nào cũng có tín hiệu
4. **Quản lý rủi ro**: Luôn đặt Stop Loss và không all-in một lệnh

## 🔧 Xử lý sự cố nhanh

### Bot không chạy?
```bash
python test_setup.py  # Kiểm tra lỗi
```

### Không nhận được tin nhắn Telegram?
```bash
python telegram_bot.py  # Test riêng Telegram
```

### Lỗi "Rate limit exceeded"?
- Đợi 5 phút và chạy lại
- Hoặc tăng `REQUEST_DELAY_SECONDS` trong `.env`

## 📚 Tìm hiểu thêm

- **README.md**: Tài liệu đầy đủ
- **PROJECT_SPEC.md**: Chi tiết chiến lược
- **config.py**: Tùy chỉnh tham số

---

**Happy Trading! 🚀**
