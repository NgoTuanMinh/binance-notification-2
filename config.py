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

# Binance Configuration
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
EMA_VALUE_FAST = 20  # Fast EMA for value zone on H1
EMA_VALUE_SLOW = 50  # Slow EMA for value zone on H1
RSI_PERIOD = 14      # RSI period for divergence detection

# Higher High/Higher Low Parameters
HH_HL_LOOKBACK = 20  # Number of candles to look back for swing points

# Fibonacci Retracement Levels
FIB_LEVEL_MIN = 0.5   # Minimum Fibonacci level
FIB_LEVEL_MAX = 0.618 # Maximum Fibonacci level

# Volume Parameters
VOLUME_MA_PERIOD = 20  # Period for volume moving average
VOLUME_MULTIPLIER = 1.0  # Current volume must be >= this * average

# Candle Pattern Parameters
PINBAR_WICK_RATIO = 0.6  # Wick must be at least 60% of candle range
ENGULFING_BODY_RATIO = 1.0  # Body must fully engulf previous candle

# Candle lookback periods
CANDLE_LIMIT = 500   # Number of candles to fetch per request

def validate_config():
    """Validate that required configuration is set."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is not set in .env file")
    return True
