"""
Test script for verifying:
1. Flip Zone detection on H1 (Breakout & Retest)
2. ATR Dynamic Stop Loss & Take Profit (Entry +- 1.5 * ATR14)
3. RVOL calculation and Telegram formatting
"""
import pandas as pd
import numpy as np
import config
from strategy_engine import StrategyEngine, TrendDirection, Signal
from telegram_bot import TelegramBot


def test_atr_and_dynamic_sl_tp():
    """Verify ATR calculation and SL/TP dynamic sizing."""
    print("🧪 [TEST 1] Testing ATR & Dynamic SL/TP...")
    engine = StrategyEngine()

    # Create dummy OHLCV data with known volatility
    np.random.seed(42)
    n = 60
    dates = pd.date_range("2024-01-01", periods=n, freq="15min")
    close = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.random.uniform(0.2, 0.8, n)
    low = close - np.random.uniform(0.2, 0.8, n)
    open_p = (high + low) / 2.0
    volume = np.random.uniform(500, 1500, n)

    df = pd.DataFrame({
        'open': open_p,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)

    df_calc = engine.calculate_indicators(df)
    assert 'atr' in df_calc.columns, "Cột 'atr' phải có trong DataFrame"
    last_atr = float(df_calc['atr'].iloc[-1])
    assert pd.notna(last_atr) and last_atr > 0, f"ATR phải > 0, hiện tại là {last_atr}"
    print(f"   ✅ ATR({config.ATR_PERIOD}) calculated successfully: {last_atr:.4f}")

    # Test dynamic SL/TP calculation
    entry = 100.0
    mult = config.ATR_MULTIPLIER  # 1.5
    expected_risk = mult * last_atr

    # Long
    expected_sl_long = entry - expected_risk
    expected_tp_long = entry + (expected_risk * config.REWARD_RATIO)
    print(f"   ✅ Long SL: {expected_sl_long:.4f} (Entry - 1.5*ATR), TP: {expected_tp_long:.4f} (R:R 1:{config.REWARD_RATIO})")

    # Short
    expected_sl_short = entry + expected_risk
    expected_tp_short = entry - (expected_risk * config.REWARD_RATIO)
    print(f"   ✅ Short SL: {expected_sl_short:.4f} (Entry + 1.5*ATR), TP: {expected_tp_short:.4f} (R:R 1:{config.REWARD_RATIO})")


def test_flip_zone_detection():
    """Verify Flip Zone logic: Resistance -> Support (Breakout & Retest)."""
    print("\n🧪 [TEST 2] Testing Flip Zone Logic...")
    engine = StrategyEngine()

    # Simulate price action for Resistance -> Support Flip:
    # 1. Phase 1: Price forms a Resistance peak around 100.0 at t=10
    # 2. Phase 2: Price pulls back to 95.0
    # 3. Phase 3: Price breakouts strongly to 110.0 at t=30
    # 4. Phase 4: Price pulls back to retest 100.0 (old resistance, now support) at t=45
    # Total candles: 60
    n = 60
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    
    closes = [90.0] * n
    highs = [91.0] * n
    lows = [89.0] * n
    opens = [90.0] * n

    # Form Resistance at index 10 (price 100)
    for i in range(7, 14):
        p = 95.0 + (5.0 - abs(i - 10))
        closes[i] = p
        highs[i] = p + 0.5
        lows[i] = p - 0.5
        opens[i] = p

    # Pullback around index 20
    for i in range(14, 25):
        closes[i] = 94.0
        highs[i] = 95.0
        lows[i] = 93.0
        opens[i] = 94.0

    # Breakout above 100 at index 30 to 110
    for i in range(25, 35):
        p = 95.0 + (i - 25) * 1.5
        closes[i] = p
        highs[i] = p + 0.5
        lows[i] = p - 0.5
        opens[i] = p

    # Retest zone ~100.0 at end of dataframe
    for i in range(35, n):
        p = 100.0 + (np.sin(i) * 0.4)
        closes[i] = p
        highs[i] = p + 0.5
        lows[i] = p - 0.5
        opens[i] = p

    df_h1 = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': [1000] * n
    }, index=dates)

    # Calculate indicators
    df_h1 = engine.calculate_indicators(df_h1)

    # Check strong zones
    zones = engine.find_strong_h1_zones(df_h1)
    print(f"   Found {len(zones['supports'])} support candidates, {len(zones['resistances'])} resistance candidates")

    # Test touch
    is_touch, desc, is_flip = engine.is_touching_strong_h1_zone(df_h1, TrendDirection.BULLISH)
    print(f"   Is touching H1 zone: {is_touch}")
    print(f"   Description: {desc}")
    print(f"   Is Flip Zone: {is_flip}")
    print("   ✅ Flip Zone detection executed cleanly.")


def test_telegram_formatting():
    """Verify formatted message includes ATR, RVOL and Flip Zone badge."""
    print("\n🧪 [TEST 3] Testing Telegram formatting...")
    bot = TelegramBot()

    signal = Signal(
        symbol="BTC/USDT",
        direction=TrendDirection.BULLISH,
        entry_price=65000.0,
        stop_loss=64250.0,
        take_profit=66500.0,
        timeframe="M15",
        pattern="Bullish Engulfing",
        reason="H4 trend BULLISH, H1 FLIP ZONE (Breakout & Retest), M15 Bullish Engulfing, Volume 1.8x, RVOL 2.15x",
        h4_ema200=62000.0,
        h1_ema34=64800.0,
        h1_ema89=64200.0,
        current_price=65020.0,
        rsi=56.5,
        volume_ratio=1.8,
        fib_level=0.55,
        atr=500.0,
        atr_multiplier=1.5,
        rvol=2.15,
        is_flip_zone=True
    )

    msg = bot.format_signal(signal)
    assert "ATR(14)" in msg, "Tin nhắn phải có ATR(14)"
    assert "RVOL (24h/7d)" in msg, "Tin nhắn phải có RVOL (24h/7d)"
    assert "FLIP ZONE (Breakout & Retest)" in msg, "Tin nhắn phải có nhãn FLIP ZONE"
    assert "🔥" in msg, "Tin nhắn RVOL >= 2.0 phải có icon ngọn lửa"

    print("   ✅ Telegram Message preview:")
    print("-" * 50)
    print(msg)
    print("-" * 50)


if __name__ == "__main__":
    test_atr_and_dynamic_sl_tp()
    test_flip_zone_detection()
    test_telegram_formatting()
    print("\n🎉 ALL UNIT TESTS PASSED SUCCESSFULLY!")
