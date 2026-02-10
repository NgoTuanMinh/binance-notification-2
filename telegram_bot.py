"""
Telegram Bot Module - Sends trading signals via Telegram.
"""
import aiohttp
from typing import Optional
from strategy_engine import Signal, TrendDirection
import config


class TelegramBot:
    """
    Sends formatted trading signals to Telegram.
    Uses only Bot Token and Chat ID - no user data access.
    """
    
    def __init__(self):
        """Initialize Telegram bot with credentials from config."""
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    async def send_message(self, message: str) -> bool:
        """
        Send a text message to the configured Telegram chat.
        
        Args:
            message: Message text to send (supports Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.token or not self.chat_id:
            print("❌ Telegram credentials not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Telegram API error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
    
    def format_signal(self, signal: Signal) -> str:
        """
        Format a trading signal into a readable Telegram message.
        
        Args:
            signal: Signal object containing trade details
            
        Returns:
            Formatted message string
        """
        # Direction emoji
        direction_emoji = "🟢" if signal.direction == TrendDirection.BULLISH else "🔴"
        direction_text = "LONG" if signal.direction == TrendDirection.BULLISH else "SHORT"
        
        # Calculate risk/reward
        risk = abs(signal.entry_price - signal.stop_loss)
        reward = abs(signal.take_profit - signal.entry_price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        # Build indicators section
        indicators_text = f"""📊 *Chỉ báo:*
• H4 EMA200: `{signal.h4_ema200:.4f}`
• H1 EMA34: `{signal.h1_ema34:.4f}`
• H1 EMA89: `{signal.h1_ema89:.4f}`
• RSI(14): `{signal.rsi:.2f}`
• Volume: `{signal.volume_ratio:.2f}x` trung bình"""
        
        # Add Fibonacci if available
        if signal.fib_level is not None:
            indicators_text += f"\n• Fibonacci: `{signal.fib_level:.3f}` level"
        
        indicators_text += f"\n• Giá hiện tại: `{signal.current_price:.4f}`"
        
        # Format message
        message = f"""
{direction_emoji} *TÍN HIỆU {direction_text}* {direction_emoji}

📊 *Cặp:* `{signal.symbol}`
💰 *Giá Entry:* `{signal.entry_price:.4f}`
🛑 *Stop Loss:* `{signal.stop_loss:.4f}` ({risk/signal.entry_price*100:.2f}%)
🎯 *Take Profit:* `{signal.take_profit:.4f}` ({reward/signal.entry_price*100:.2f}%)
📈 *R:R Ratio:* `1:{rr_ratio:.2f}`

⏰ *Khung thời gian:* {signal.timeframe}
🔍 *Pattern:* {signal.pattern}

📌 *Lý do:*
{signal.reason}

{indicators_text}

        """.strip()
        
        return message
    
    async def send_signal(self, signal: Signal) -> bool:
        """
        Send a trading signal to Telegram.
        
        Args:
            signal: Signal object to send
            
        Returns:
            True if sent successfully
        """
        message = self.format_signal(signal)
        success = await self.send_message(message)
        
        if success:
            print(f"✅ Đã gửi tín hiệu {signal.symbol} qua Telegram")
        else:
            print(f"❌ Không thể gửi tín hiệu {signal.symbol}")
        
        return success
    
    async def send_startup_message(self, total_symbols: int) -> bool:
        """
        Send a message when the bot starts scanning.
        
        Args:
            total_symbols: Number of symbols to scan
            
        Returns:
            True if sent successfully
        """
        message = f"""
🤖 *BOT KHỞI ĐỘNG*

Bot đã bắt đầu quét thị trường Binance Futures
📊 Số cặp tiền: {total_symbols}
⏰ Chiến lược: MTF (H4 + H1 + M15)

🔍 Đang tìm kiếm cơ hội...
        """.strip()
        
        return await self.send_message(message)
    
    async def send_scan_complete(
        self, 
        total_scanned: int, 
        signals_found: int,
        duration_seconds: float
    ) -> bool:
        """
        Send a summary message after completing a scan.
        
        Args:
            total_scanned: Total symbols scanned
            signals_found: Number of signals found
            duration_seconds: Time taken for scan
            
        Returns:
            True if sent successfully
        """
        message = f"""
✅ *QUÉT HOÀN TẤT*

📊 Đã quét: {total_scanned} cặp
🎯 Tìm thấy: {signals_found} tín hiệu
⏱ Thời gian: {duration_seconds:.1f}s

Chờ lần quét tiếp theo...
        """.strip()
        
        return await self.send_message(message)
    
    async def send_error(self, error_message: str) -> bool:
        """
        Send an error notification.
        
        Args:
            error_message: Error description
            
        Returns:
            True if sent successfully
        """
        message = f"""
⚠️ *LỖI XẢY RA*

{error_message}

Bot sẽ tiếp tục thử...
        """.strip()
        
        return await self.send_message(message)


async def test_telegram():
    """Test function to verify Telegram bot."""
    # Load config
    try:
        config.validate_config()
    except ValueError as e:
        print(f"❌ Config error: {e}")
        print("💡 Tạo file .env từ .env.example và điền thông tin Telegram")
        return
    
    bot = TelegramBot()
    
    # Test sending a simple message
    print("🧪 Testing Telegram bot...")
    success = await bot.send_message("🧪 *Test Message*\n\nBot hoạt động bình thường!")
    
    if success:
        print("✅ Telegram bot test passed!")
    else:
        print("❌ Telegram bot test failed!")
    
    # Test signal formatting (without sending)
    from strategy_engine import Signal, TrendDirection
    
    test_signal = Signal(
        symbol="BTC/USDT",
        direction=TrendDirection.BULLISH,
        entry_price=45000.0,
        stop_loss=44500.0,
        take_profit=46000.0,
        timeframe="M15",
        pattern="Bullish Engulfing",
        reason="H4 trend BULLISH with HH/HL structure, H1 Fibonacci 0.618 zone, M15 Bullish Engulfing, Volume 1.5x",
        h4_ema200=43000.0,
        h1_ema34=44800.0,
        h1_ema89=44600.0,
        current_price=45000.0,
        rsi=45.5,
        volume_ratio=1.5,
        fib_level=0.618
    )
    
    formatted = bot.format_signal(test_signal)
    print("\n📝 Formatted signal preview:")
    print(formatted)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_telegram())
