# 🎯 Tính năng & Cải tiến

## ✨ Tính năng nổi bật

### 🔄 Kiến trúc 3 luồng quét độc lập

Thay vì quét tuần tự, bot chạy 3 luồng song song với chu kỳ tối ưu:

```
┌─────────────────────────────────────────────────┐
│  🔵 H4 Loop (Mỗi 1 giờ)                        │
│  └─> Quét 300 symbols                          │
│      └─> Output: ~50 Candidate_Symbols         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  🟢 H1 Loop (Mỗi 15 phút)                      │
│  └─> Quét 50 candidates                        │
│      └─> Output: ~10 Hot_Watchlist             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  🟡 M15 Loop (Mỗi 2 phút)                      │
│  └─> Quét 10 watchlist                         │
│      └─> Output: 0-5 Trading Signals           │
└─────────────────────────────────────────────────┘
```

**Lợi ích:**
- ⚡ Phản ứng nhanh: M15 quét mỗi 2 phút thay vì 15 phút
- 💰 Tiết kiệm 78% API calls (800 vs 3,600 requests/giờ)
- 🎯 Độ chính xác cao hơn với lọc từng bước

---

## 📈 Bộ lọc H4: Trend Filter (Chu kỳ 1 giờ)

### Điều kiện Long:
1. ✅ **Price > EMA 200** (3 nến liên tiếp)
2. ✅ **Higher High/Higher Low structure**
   - Đỉnh gần nhất cao hơn đỉnh trước
   - Đáy gần nhất cao hơn đáy trước

### Điều kiện Short:
1. ✅ **Price < EMA 200** (3 nến liên tiếp)
2. ✅ **Lower High/Lower Low structure**
   - Đỉnh gần nhất thấp hơn đỉnh trước
   - Đáy gần nhất thấp hơn đáy trước

### Implementation:
```python
def is_trend_aligned(df_h4):
    # Check EMA200 alignment
    # Check market structure (HH/HL or LH/LL)
    # Return: BULLISH, BEARISH, or None
```

---

## 💎 Bộ lọc H1: Value Zone (Chu kỳ 15 phút)

### Phương pháp 1: Fibonacci Retracement
- ✅ Tính Fibonacci từ sóng H4 gần nhất
- ✅ Tìm pullback về **vùng 0.5 - 0.618**
- 🎯 Đây là "golden zone" - vùng giá trị tốt nhất

### Phương pháp 2: EMA Pullback
- ✅ Giá chạm **EMA 20** (support/resistance động)
- ✅ HOẶC chạm **EMA 50** (support/resistance mạnh hơn)
- 🎯 Với tolerance 1% để tránh bỏ lỡ

### Implementation:
```python
def is_in_value_zone(df_h1, df_h4, trend):
    # Calculate Fibonacci levels from H4 swing
    # Check if price in 0.5-0.618 zone
    # OR check if touching EMA20/50
    # Return: (is_in_zone, description, fib_level)
```

---

## 🎯 Bộ lọc M15: Entry Signal (Chu kỳ 1-3 phút)

### 1. Candlestick Patterns

#### Bullish Engulfing (LONG)
```
  ┌──┐
  │▓▓│  <- Nến xanh "nuốt chửng" nến đỏ trước
┌─┤▓▓│
│░│▓▓│
└─┘└──┘
```
- Nến trước: Đỏ (bearish)
- Nến hiện tại: Xanh (bullish) và engulf hoàn toàn

#### Bearish Engulfing (SHORT)
```
┌──┐
│▓▓├─┐
│▓▓│░│
└──┘└─┘
```
- Nến trước: Xanh (bullish)
- Nến hiện tại: Đỏ (bearish) và engulf hoàn toàn

#### Bullish Pinbar (LONG)
```
    │
    │  <- Long lower wick (≥60% of candle)
    ┼
   ┌┴┐
   └─┘
```
- Đuôi dưới dài (≥60% chiều cao nến)
- Đuôi trên ngắn
- Rejection của support

#### Shooting Star (SHORT)
```
   ┌─┐
   └┬┘
    ┼
    │  <- Long upper wick (≥60% of candle)
    │
```
- Đuôi trên dài (≥60% chiều cao nến)
- Đuôi dưới ngắn
- Rejection của resistance

### 2. RSI Divergence (Tùy chọn)

#### Bullish Divergence:
```
Price:  \  /\  (Lower low)
         \/
RSI:     /\  /\ (Higher low) ✅
         \/
```
- Giá tạo đáy thấp hơn
- RSI tạo đáy cao hơn
- Tín hiệu: Trend đang yếu, sắp đảo chiều tăng

#### Bearish Divergence:
```
Price:  /\  /\ (Higher high)
       /  \/
RSI:    \/    (Lower high) ✅
       /  \
```
- Giá tạo đỉnh cao hơn
- RSI tạo đỉnh thấp hơn
- Tín hiệu: Trend đang yếu, sắp đảo chiều giảm

### 3. Volume Confirmation (BẮT BUỘC)

```
Volume MA(20)  ─────────────────
               
Current Vol    ████████████████  <- Must be ≥ 1.0x average
```

- Nến tín hiệu **PHẢI** có volume ≥ trung bình 20 nến
- Xác nhận có tiền "thật" đang vào
- Không volume = Không signal (bỏ qua)

### Implementation:
```python
def get_entry_signal(df_m15, trend):
    # Check candlestick patterns
    pattern = detect_engulfing() or detect_pinbar()
    
    # Check RSI divergence (optional boost)
    has_divergence = detect_rsi_divergence()
    
    # Check volume (REQUIRED)
    volume_confirmed, ratio = check_volume_confirmation()
    if not volume_confirmed:
        return None  # Skip if no volume
    
    return signal
```

---

## 🔧 Tham số cấu hình

### Chu kỳ quét (config.py)
```python
SCAN_INTERVAL_H4 = 3600   # 1 giờ
SCAN_INTERVAL_H1 = 900    # 15 phút
SCAN_INTERVAL_M15 = 120   # 2 phút (có thể điều chỉnh 60-180s)
```

### Symbol Filtering (Performance Optimization) ⭐
```python
# Giới hạn số symbols để scan
MAX_SYMBOLS_TO_SCAN = None  # None = all, or number (50, 100, etc.)

# Phương pháp sắp xếp
SYMBOL_SORT_METHOD = 'volume'  # 'volume' or 'alphabetical'
```

**Use cases:**
- **Testing**: Set to 10-20 symbols để test nhanh
- **Development**: Set to 50 để develop với thời gian hợp lý
- **Production (limited)**: Set to 100 để focus vào top coins
- **Production (full)**: Set to None để quét tất cả

**Benefits khi giới hạn:**
- ⚡ Faster scanning (50 symbols ~2-3 min vs 300 ~10-15 min)
- 💰 Fewer API calls
- 🎯 Focus on high liquidity pairs (when using 'volume' sort)
- 🧪 Perfect for testing strategies

### Technical Indicators
```python
EMA_TREND = 200           # EMA xu hướng chính
EMA_VALUE_FAST = 20       # EMA nhanh
EMA_VALUE_SLOW = 50       # EMA chậm
RSI_PERIOD = 14           # RSI period
```

### Market Structure
```python
HH_HL_LOOKBACK = 20       # Số nến để tìm swing points
```

### Fibonacci Levels
```python
FIB_LEVEL_MIN = 0.5       # Fibonacci min (50%)
FIB_LEVEL_MAX = 0.618     # Fibonacci max (61.8%)
```

### Volume Confirmation
```python
VOLUME_MA_PERIOD = 20     # Volume MA period
VOLUME_MULTIPLIER = 1.0   # Current vol >= 1.0x average
```

### Pattern Detection
```python
PINBAR_WICK_RATIO = 0.6       # Wick >= 60% of candle
ENGULFING_BODY_RATIO = 1.0    # Full engulfing required
```

---

## 📊 Ví dụ Signal đầy đủ

```
🟢 TÍN HIỆU LONG 🟢

📊 Cặp: ETH/USDT
💰 Giá Entry: 2450.00
🛑 Stop Loss: 2430.00 (0.82%)
🎯 Take Profit: 2490.00 (1.63%)
📈 R:R Ratio: 1:2.00

⏰ Khung thời gian: M15
🔍 Pattern: Bullish Pinbar

📌 Lý do:
H4 trend BULLISH with HH/HL structure, 
H1 Fibonacci 0.618 zone, 
M15 Bullish Pinbar, 
RSI Divergence, 
Volume 1.8x

📊 Chỉ báo:
• H4 EMA200: 2300.00
• H1 EMA20: 2445.00
• H1 EMA50: 2440.00
• RSI(14): 42.50
• Volume: 1.80x trung bình
• Fibonacci: 0.618 level
• Giá hiện tại: 2450.00
```

**Phân tích signal này:**
1. ✅ **H4**: Trend tăng rõ ràng với cấu trúc HH/HL
2. ✅ **H1**: Pullback chính xác về Fib 0.618 (golden zone)
3. ✅ **M15**: Pinbar rejection + RSI divergence + Volume cao
4. 🎯 **Risk/Reward**: 1:2 (risk 0.82%, reward 1.63%)
5. ⚡ **Confluences**: 5 điều kiện cùng xuất hiện → độ tin cậy cao

---

## 🚀 So sánh với phiên bản cũ

| Tính năng | Phiên bản cũ | Phiên bản mới |
|-----------|--------------|---------------|
| **Kiến trúc** | 1 luồng tuần tự | 3 luồng song song |
| **Chu kỳ H4** | 15 phút | 1 giờ ✅ |
| **Chu kỳ H1** | 15 phút | 15 phút |
| **Chu kỳ M15** | 15 phút | 2 phút ⚡ |
| **H4 Filter** | Chỉ EMA200 | EMA200 + HH/HL ✅ |
| **H1 Filter** | Chỉ EMA20/50 | EMA + Fibonacci ✅ |
| **M15 Patterns** | Chỉ Engulfing | Engulfing + Pinbar + Shooting Star ✅ |
| **RSI** | Không | Divergence detection ✅ |
| **Volume** | Không | Confirmation required ✅ |
| **API calls/giờ** | 3,600 | 800 (-78%) ✅ |
| **Phản ứng** | 15 phút | 2 phút ⚡ |

---

## 🎓 Tài liệu tham khảo

- **README.md**: Hướng dẫn đầy đủ
- **QUICKSTART.md**: Bắt đầu nhanh trong 5 phút
- **PROJECT_SPEC.md**: Đặc tả ban đầu
- **config.py**: Tham số cấu hình
- **strategy_engine.py**: Implementation chi tiết

---

## 💡 Tips sử dụng

1. **Kiên nhẫn**: Chiến lược nghiêm ngặt, không phải lúc nào cũng có signal
2. **Backtest**: Test với mode `--once` trước khi chạy production
3. **Điều chỉnh**: Có thể điều chỉnh các tham số trong `config.py`
4. **Theo dõi**: Xem báo cáo thống kê mỗi giờ để đánh giá hiệu quả
5. **Risk Management**: Luôn đặt SL và chỉ risk 1-2% tài khoản/lệnh

---

**Happy Trading! 🚀📈**
