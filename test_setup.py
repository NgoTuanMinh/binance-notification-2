"""
Test script to verify all components are working correctly.
Run this after installation to ensure everything is set up properly.
"""
import asyncio
import sys


async def test_imports():
    """Test that all required packages can be imported."""
    print("🧪 Test 1: Kiểm tra imports...")
    
    try:
        import ccxt
        import pandas
        import pandas_ta
        import aiohttp
        from dotenv import load_dotenv
        print("  ✅ Tất cả packages đã được import thành công")
        return True
    except ImportError as e:
        print(f"  ❌ Lỗi import: {e}")
        print("  💡 Chạy: pip install -r requirements.txt")
        return False


async def test_config():
    """Test configuration loading."""
    print("\n🧪 Test 2: Kiểm tra cấu hình...")
    
    try:
        import config
        
        # Check if .env file exists
        import os
        if not os.path.exists('.env'):
            print("  ⚠️  File .env chưa tồn tại")
            print("  💡 Tạo file .env từ .env.example: cp .env.example .env")
            print("  💡 Sau đó điền thông tin Telegram vào file .env")
            return False
        
        # Try to validate config
        try:
            config.validate_config()
            print("  ✅ Cấu hình hợp lệ")
            print(f"     Bot Token: {config.TELEGRAM_BOT_TOKEN[:10]}...")
            print(f"     Chat ID: {config.TELEGRAM_CHAT_ID}")
            return True
        except ValueError as e:
            print(f"  ⚠️  Cấu hình chưa đầy đủ: {e}")
            print("  💡 Vui lòng điền TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID trong .env")
            return False
            
    except Exception as e:
        print(f"  ❌ Lỗi khi load config: {e}")
        return False


async def test_binance_connection():
    """Test connection to Binance public API."""
    print("\n🧪 Test 3: Kiểm tra kết nối Binance...")
    
    try:
        from market_data import MarketDataFetcher
        import config
        
        async with MarketDataFetcher() as fetcher:
            # Try to get symbols
            symbols = await fetcher.get_futures_symbols("volume", config.MAX_SYMBOLS_TO_SCAN)
            
            if symbols:
                print(f"  ✅ Kết nối Binance thành công")
                print(f"     Tìm thấy {len(symbols)} cặp Futures")
                print(f"     Ví dụ: {', '.join(symbols[:5])}")
                return True
            else:
                print("  ❌ Không thể lấy danh sách symbols")
                return False
                
    except Exception as e:
        print(f"  ❌ Lỗi kết nối Binance: {e}")
        return False


async def test_data_fetching():
    """Test fetching candle data."""
    print("\n🧪 Test 4: Kiểm tra lấy dữ liệu nến...")
    
    try:
        from market_data import MarketDataFetcher
        import config
        
        async with MarketDataFetcher() as fetcher:
            # Try to fetch BTC/USDT data
            symbol = 'BTC/USDT'
            print(f"  Đang lấy dữ liệu {symbol}...")
            
            data = await fetcher.fetch_multi_timeframe_data(
                symbol,
                config.TIMEFRAMES
            )

            success = True
            for name, df in data.items():
                if df is not None and not df.empty:
                    print(f"  ✅ {name} ({config.TIMEFRAMES[name]}): {len(df)} nến")
                else:
                    print(f"  ❌ {name}: Không có dữ liệu")
                    success = False
            
            return success
            
    except Exception as e:
        print(f"  ❌ Lỗi khi lấy dữ liệu: {e}")
        return False


async def test_strategy_engine():
    """Test strategy calculations."""
    print("\n🧪 Test 5: Kiểm tra strategy engine...")
    
    try:
        from strategy_engine import StrategyEngine
        import pandas as pd
        from datetime import datetime, timedelta
        
        engine = StrategyEngine()
        
        # Create sample data
        dates = pd.date_range(end=datetime.now(), periods=300, freq='1h')
        sample_data = pd.DataFrame({
            'open': range(40000, 40300),
            'high': range(40100, 40400),
            'low': range(39900, 40200),
            'close': range(40000, 40300),
            'volume': [1000] * 300
        }, index=dates)
        
        # Test indicator calculation
        df = engine.calculate_indicators(sample_data)
        
        required_indicators = ['ema20', 'ema50', 'ema200', 'rsi']
        missing = [ind for ind in required_indicators if ind not in df.columns]
        
        if not missing:
            print("  ✅ Strategy engine hoạt động tốt")
            print(f"     Chỉ báo: {', '.join(required_indicators)}")
            return True
        else:
            print(f"  ❌ Thiếu chỉ báo: {missing}")
            return False
            
    except Exception as e:
        print(f"  ❌ Lỗi strategy engine: {e}")
        return False


async def test_telegram():
    """Test Telegram bot connection."""
    print("\n🧪 Test 6: Kiểm tra Telegram bot...")
    
    try:
        import config
        config.validate_config()
    except ValueError as e:
        print(f"  ⚠️  Bỏ qua test Telegram: {e}")
        return None  # Skip if not configured
    
    try:
        from telegram_bot import TelegramBot
        
        bot = TelegramBot()
        
        # Try to send a test message
        print("  Đang gửi tin nhắn test...")
        success = await bot.send_message(
            "🧪 *TEST MESSAGE*\n\n"
            "Bot setup hoàn tất! Hệ thống đang hoạt động bình thường. ✅"
        )
        
        if success:
            print("  ✅ Telegram bot hoạt động tốt")
            print("  💬 Kiểm tra tin nhắn test trong Telegram của bạn")
            return True
        else:
            print("  ❌ Không thể gửi tin nhắn Telegram")
            print("  💡 Kiểm tra lại Bot Token và Chat ID")
            return False
            
    except Exception as e:
        print(f"  ❌ Lỗi Telegram bot: {e}")
        return False


async def main():
    """Run all tests."""
    print("="*60)
    print("🚀 KIỂM TRA CÀI ĐẶT DỰ ÁN")
    print("="*60)
    
    results = []
    
    # Run tests sequentially
    results.append(('Imports', await test_imports()))
    results.append(('Config', await test_config()))
    results.append(('Binance Connection', await test_binance_connection()))
    results.append(('Data Fetching', await test_data_fetching()))
    results.append(('Strategy Engine', await test_strategy_engine()))
    results.append(('Telegram Bot', await test_telegram()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 KẾT QUẢ TỔNG HỢP")
    print("="*60)
    
    for test_name, result in results:
        if result is True:
            print(f"  ✅ {test_name}")
        elif result is False:
            print(f"  ❌ {test_name}")
        else:
            print(f"  ⚠️  {test_name} (Bỏ qua)")
    
    # Check if all critical tests passed
    critical_tests = results[:5]  # All except Telegram
    all_passed = all(r is True for _, r in critical_tests)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 TẤT CẢ TEST QUAN TRỌNG ĐÃ PASS!")
        print("="*60)
        print("\n✅ Dự án đã sẵn sàng!")
        print("\n📚 Bước tiếp theo:")
        print("   1. Nếu chưa test Telegram: Cấu hình .env và chạy lại")
        print("   2. Chạy bot: python main.py")
        print("   3. Hoặc test một lần: python main.py --once")
    else:
        print("⚠️  MỘT SỐ TEST CHƯA PASS")
        print("="*60)
        print("\n💡 Vui lòng khắc phục các lỗi trên trước khi chạy bot.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test bị hủy bởi người dùng")
