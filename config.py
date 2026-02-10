"""
Configuration module for loading environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Binance Configuration (used in market_data.py when initializing ccxt)
# API Key và Secret dùng cho ccxt (load_markets, fetch_ohlcv, fetch_tickers, ...)
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '') or os.getenv('BINANCE_SECRET', '')
# Override base URL nếu cần region khác (binance.us) hoặc proxy
BINANCE_FUTURE_API_BASE_URL = os.getenv('BINANCE_FUTURE_API_BASE_URL', 'https://fapi.binance.com/')

# Rate Limiting Settings
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
REQUEST_DELAY_SECONDS = float(os.getenv('REQUEST_DELAY_SECONDS', '0.5'))

# Symbol Filtering (Performance Optimization)
# Set to None to scan all symbols, or set a number to limit symbols
# Examples: None (all), 50 (top 50), 100 (top 100)
MAX_SYMBOLS_TO_SCAN = os.getenv('MAX_SYMBOLS_TO_SCAN', None)
if MAX_SYMBOLS_TO_SCAN is not None:
    try:
        MAX_SYMBOLS_TO_SCAN = int(MAX_SYMBOLS_TO_SCAN)
    except (ValueError, TypeError):
        MAX_SYMBOLS_TO_SCAN = None

# Symbol sorting method for filtering
# 'volume': Sort by 24h volume (recommended - most liquid pairs first)
# 'alphabetical': Sort alphabetically
SYMBOL_SORT_METHOD = os.getenv('SYMBOL_SORT_METHOD', 'volume')

# Trading Strategy Parameters
TIMEFRAMES = {
    'trend': '4h',      # H4 for trend identification
    'value': '1h',      # H1 for value zone
    'signal': '15m'     # M15 for entry signal
}

# Scanning Intervals (in seconds)
SCAN_INTERVAL_H4 = 3600      # 1 hour for H4 trend filter
SCAN_INTERVAL_H1 = 900       # 15 minutes for H1 value zone
SCAN_INTERVAL_M15 = 120      # 2 minutes for M15 signals (1-3 minutes range)

# Technical Indicators Parameters
EMA_TREND = 200      # EMA for trend filter on H4
EMA_VALUE_FAST = 34  # Fast EMA for value zone on H1
EMA_VALUE_SLOW = 89  # Slow EMA for value zone on H1
RSI_PERIOD = 14      # RSI period for divergence detection

# Higher High/Higher Low Parameters
HH_HL_LOOKBACK = 34  # Number of candles to look back for swing points

# Fibonacci Retracement Levels
FIB_LEVEL_MIN = 0.5   # Minimum Fibonacci level
FIB_LEVEL_MAX = 0.618 # Maximum Fibonacci level

# H1 Strong Support/Resistance Zone Filter
H1_SR_LOOKBACK_CANDLES = int(os.getenv('H1_SR_LOOKBACK_CANDLES', '180'))  # ~7.5 days of H1 candles
H1_SR_SWING_LOOKBACK = int(os.getenv('H1_SR_SWING_LOOKBACK', '3'))        # swing detection sensitivity
H1_SR_MIN_TOUCHES = int(os.getenv('H1_SR_MIN_TOUCHES', '5'))              # minimum touches to call a zone "strong"
H1_SR_ZONE_MIN_PERCENT = float(os.getenv('H1_SR_ZONE_MIN_PERCENT', '1.0'))  # zone half-width min (%)
H1_SR_ZONE_MAX_PERCENT = float(os.getenv('H1_SR_ZONE_MAX_PERCENT', '1.5'))  # zone half-width max (%)

# Volume Parameters
VOLUME_MA_PERIOD = 34  # Period for volume moving average
VOLUME_MULTIPLIER = 1.0  # Current volume must be >= this * average

# Candle Pattern Parameters
PINBAR_WICK_RATIO = 0.6  # Wick must be at least 60% of candle range
ENGULFING_BODY_RATIO = 1.0  # Body must fully engulf previous candle

# Stop Loss (khoảng cách từ entry, theo % giá)
# Nếu SL từ nến quá ngắn → nới ra tối thiểu STOP_LOSS_MIN_PERCENT; quá xa → thu lại tối đa STOP_LOSS_MAX_PERCENT
STOP_LOSS_MIN_PERCENT = float(os.getenv('STOP_LOSS_MIN_PERCENT', '0.3'))   # tối thiểu 0.3%
STOP_LOSS_MAX_PERCENT = float(os.getenv('STOP_LOSS_MAX_PERCENT', '3.0'))   # tối đa 3%

# Candle lookback periods
CANDLE_LIMIT = 500   # Number of candles to fetch per request

def validate_config():
    """Validate that required configuration is set."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is not set in .env file")
    if not (BINANCE_API_KEY and BINANCE_SECRET_KEY):
        raise ValueError(
            "BINANCE_API_KEY và BINANCE_SECRET_KEY phải được set trong .env (ccxt cần để gọi API)"
        )
    return True
