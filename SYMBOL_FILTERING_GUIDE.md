# 🎯 Symbol Filtering - Quick Guide

## Tính năng mới: Giới hạn số lượng symbols để quét

Giúp tăng tốc độ test và tối ưu performance.

---

## ⚡ TL;DR (Too Long; Didn't Read)

**Muốn test nhanh?** Thêm vào file `.env`:
```env
MAX_SYMBOLS_TO_SCAN=50
```

**Muốn quét hết?** Để trống hoặc xóa dòng đó:
```env
MAX_SYMBOLS_TO_SCAN=
```

---

## 🚀 Quick Examples

### Example 1: Test với 10 symbols (cực nhanh ~30 giây)
```env
MAX_SYMBOLS_TO_SCAN=10
SYMBOL_SORT_METHOD=volume
```

```bash
python main.py --once
```

**Output:**
```
✅ Khởi tạo: 10 cặp Futures (giới hạn 10 cặp top volume)
   Top 10 by volume: BTC/USDT, ETH/USDT, SOL/USDT, ...
```

---

### Example 2: Development với top 50 (~2-3 phút)
```env
MAX_SYMBOLS_TO_SCAN=50
SYMBOL_SORT_METHOD=volume
```

**Lợi ích:**
- ✅ Balance tốt giữa speed và coverage
- ✅ Bao gồm hầu hết major coins
- ✅ Đủ nhanh để iterate quickly

---

### Example 3: Production focused với top 100
```env
MAX_SYMBOLS_TO_SCAN=100
SYMBOL_SORT_METHOD=volume
```

**Lợi ích:**
- ✅ Coverage rộng (top 100 coins)
- ✅ Vẫn nhanh hơn quét tất cả
- ✅ Focus vào coins có thanh khoản

---

### Example 4: Production full (quét tất cả ~300+ symbols)
```env
MAX_SYMBOLS_TO_SCAN=
# Hoặc comment out dòng này
```

**Lợi ích:**
- ✅ Complete market coverage
- ✅ Không bỏ lỡ cơ hội nào
- ✅ Tìm được hidden gems

---

## 📊 Performance Comparison

| Symbols | H4 Time | Total Cycle | API/hour | Best For |
|---------|---------|-------------|----------|----------|
| 10 | 30s | ~2 min | 100 | Quick testing |
| 50 | 2 min | ~5 min | 250 | Development |
| 100 | 4 min | ~8 min | 450 | Production (focused) |
| 300+ | 12 min | ~20 min | 800 | Production (full) |

---

## 🎨 Sorting Methods

### Option 1: Volume (Khuyến nghị) 📊
```env
SYMBOL_SORT_METHOD=volume
```

Lấy coins có volume giao dịch cao nhất:
- BTC/USDT, ETH/USDT, BNB/USDT, ...
- Thanh khoản tốt
- Dễ vào/ra lệnh

### Option 2: Alphabetical 🔤
```env
SYMBOL_SORT_METHOD=alphabetical
```

Lấy theo thứ tự ABC:
- 1INCH/USDT, AAVE/USDT, ADA/USDT, ...
- Deterministic (luôn giống nhau)
- Không cần fetch volume data

---

## 🔧 Cách Setup

### Bước 1: Mở file .env
```bash
nano .env
# hoặc dùng editor khác
```

### Bước 2: Thêm config
```env
# Telegram config (đã có từ trước)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Symbol filtering (THÊM MỚI)
MAX_SYMBOLS_TO_SCAN=50
SYMBOL_SORT_METHOD=volume
```

### Bước 3: Save và chạy bot
```bash
python main.py --once
```

### Bước 4: Check output
```
✅ Khởi tạo: 50 cặp Futures (giới hạn 50 cặp top volume)
   Top 5 by volume: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT
```

---

## 💡 Use Cases

### Use Case 1: Learning (Người mới)
```env
MAX_SYMBOLS_TO_SCAN=20
```
→ Learn bot behavior với ít noise

### Use Case 2: Testing Strategy Changes
```env
MAX_SYMBOLS_TO_SCAN=30
```
→ Quick iterations để test parameters

### Use Case 3: Development
```env
MAX_SYMBOLS_TO_SCAN=50
```
→ Balance giữa coverage và speed

### Use Case 4: Production Trading
```env
MAX_SYMBOLS_TO_SCAN=100
# hoặc để trống cho full coverage
```
→ Real trading với coverage tốt

---

## ❓ FAQ

### Q: Giá trị nào tốt nhất?
**A:** Depends on use case:
- Testing: 10-20
- Development: 50
- Production: 100 hoặc trống (all)

### Q: Volume hay Alphabetical?
**A:** Volume cho trading, Alphabetical cho testing cố định

### Q: Có ảnh hưởng đến signal quality không?
**A:** Không! Chỉ ảnh hưởng số lượng symbols được quét

### Q: Có thể change trong khi bot chạy?
**A:** Không, phải restart bot

### Q: Làm sao biết bot đang dùng config nào?
**A:** Check message khởi động trong Telegram hoặc console

---

## 🎯 Recommended Configs

### Scenario 1: First Time Running
```env
MAX_SYMBOLS_TO_SCAN=10
```
Chạy `python main.py --once` để verify mọi thứ hoạt động

### Scenario 2: Learning Phase
```env
MAX_SYMBOLS_TO_SCAN=30
```
Chạy vài ngày để học bot behavior

### Scenario 3: Going Live (Conservative)
```env
MAX_SYMBOLS_TO_SCAN=50
```
Start với coverage vừa phải

### Scenario 4: Going Live (Aggressive)
```env
MAX_SYMBOLS_TO_SCAN=
```
Full coverage để không bỏ lỡ opportunities

---

## 📈 Real Example

**Before (No limit):**
```
✅ Khởi tạo: 287 cặp Futures
📈 BƯỚC 1: Lọc Trend H4 (EMA200)
   [... 12 minutes later ...]
📊 Kết quả BƯỚC 1: 42/287 cặp pass
```

**After (With limit):**
```
✅ Khởi tạo: 50 cặp Futures (giới hạn 50 cặp top volume)
   Top 5 by volume: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT
📈 BƯỚC 1: Lọc Trend H4 (EMA200)
   [... 2 minutes later ...]
📊 Kết quả BƯỚC 1: 8/50 cặp pass
```

**Result:** 6x faster! 🚀

---

## 🔗 Related Docs

- **PERFORMANCE_TUNING.md** - Detailed tuning guide
- **DEPLOYMENT.md** - Production configurations
- **README.md** - Full documentation

---

**Quick start:** Set `MAX_SYMBOLS_TO_SCAN=50` và bắt đầu! 🚀
