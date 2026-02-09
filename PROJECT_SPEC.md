Project Spec: Public Crypto Screener (Binance Futures - No Account Access)

1. Mục tiêu & Bảo mật (Privacy First)
   Bảo mật: Bot chỉ sử dụng Public Endpoints của Binance (https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info). Không yêu cầu API Key/Secret của sàn.

Phạm vi: Quét dữ liệu thị trường công khai để tìm tín hiệu, không truy cập dữ liệu người dùng.

Thông báo: Sử dụng Telegram Bot để gửi tín hiệu (Cần Token và Chat ID).

2. Chiến thuật Giao dịch (Logic Core)
   Bot thực hiện quét theo phễu lọc 3 bước từ khung lớn đến khung nhỏ:

H4 (Trend): Lọc các cặp có giá đóng cửa nằm trên/dưới EMA 200.

H1 (Value Zone): Xác định các cặp đang có sự điều chỉnh (Pullback) về vùng EMA 20 hoặc EMA 50.

M15 (Signal): Kiểm tra nến đảo chiều (Bullish/Bearish Engulfing) và RSI Phân kỳ.

3. Cấu trúc Module
   A. Module Dữ liệu (market_data.py)
   Sử dụng ccxt.async_support.binance.

Khởi tạo: exchange = ccxt.binance({'enableRateLimit': True}). (Không truyền apiKey/secret).

get_symbols(): Lấy danh sách tất cả các cặp /USDT trên thị trường Futures.

fetch_candles(symbol, timeframe): Lấy dữ liệu OHLCV công khai.

B. Module Phân tích (strategy_engine.py)
Sử dụng pandas_ta.

Tính toán chỉ báo kỹ thuật trên dữ liệu nến nhận được.

Hàm is_trend_aligned(df_h4): Kiểm tra EMA 200.

Hàm is_in_zone(df_h1): Kiểm tra giá chạm vùng EMA 20/50.

Hàm get_entry_signal(df_m15): Nhận diện nến Engulfing/Pinbar.

C. Module Thông báo (telegram_bot.py)
Chỉ sử dụng TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID.

Format tin nhắn gửi về điện thoại với các thông số: Cặp tiền, Khung giờ, Giá entry dự kiến, SL/TP dựa trên cấu trúc nến.

4. Cấu hình Môi trường (.env)
   Chỉ cần các thông tin sau:

Đoạn mã
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
BINANCE_FUTURE_API_BASE_URL=https://fapi.binance.com/

5. Lưu ý về kỹ thuật khi dùng API Public:
   Rate Limit: API Public của Binance có giới hạn request theo IP (thường là 1200 weight/phút). Khi viết code, hãy dùng asyncio.sleep() giữa các lần quét không để tránh bị "soft ban".

Tối ưu hóa: Thay vì quét 300 coin ở khung M15, "Chỉ quét M15 cho những coin nào đã vượt qua bộ lọc H4 và H1". Điều này tiết kiệm 90% số lượng request API.
