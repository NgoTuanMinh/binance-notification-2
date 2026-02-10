"""
Strategy Engine Module - Implements enhanced multi-timeframe filtering strategy.
3-step funnel with advanced pattern recognition and structure analysis.
"""
import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum
import config


class TrendDirection(Enum):
    """Trend direction enumeration."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass
class Signal:
    """Trading signal data structure."""
    symbol: str
    direction: TrendDirection
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    pattern: str
    reason: str
    h4_ema200: float
    h1_ema34: float
    h1_ema89: float
    current_price: float
    rsi: float
    volume_ratio: float
    fib_level: Optional[float] = None


class StrategyEngine:
    """
    Implements the enhanced 3-step filtering strategy:
    1. H4: Price above/below EMA 200 + Higher High/Higher Low structure
    2. H1: Pullback to Fibonacci 0.5-0.618 or EMA 34/89
    3. M15: Candlestick patterns + RSI Divergence + Volume confirmation
    """
    
    def __init__(self):
        self.ema_trend = config.EMA_TREND
        self.ema_fast = config.EMA_VALUE_FAST
        self.ema_slow = config.EMA_VALUE_SLOW
        self.rsi_period = config.RSI_PERIOD
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators on OHLCV data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        if df is None or df.empty:
            return df
        
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Calculate EMAs (H1 dùng 34/89, H4 dùng 200)
        df['ema34'] = ta.ema(df['close'], length=34)
        df['ema89'] = ta.ema(df['close'], length=89)
        df['ema200'] = ta.ema(df['close'], length=200)
        
        # Calculate RSI
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        
        # Calculate Volume MA
        df['volume_ma'] = df['volume'].rolling(window=config.VOLUME_MA_PERIOD).mean()
        
        return df
    
    def find_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> Tuple[List[int], List[int]]:
        """
        Find swing highs and swing lows in price data.
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Number of candles on each side to confirm swing point
            
        Returns:
            Tuple of (swing_high_indices, swing_low_indices)
        """
        highs = []
        lows = []
        
        for i in range(lookback, len(df) - lookback):
            # Check if it's a swing high
            is_high = True
            for j in range(1, lookback + 1):
                if df['high'].iloc[i] <= df['high'].iloc[i-j] or df['high'].iloc[i] <= df['high'].iloc[i+j]:
                    is_high = False
                    break
            if is_high:
                highs.append(i)
            
            # Check if it's a swing low
            is_low = True
            for j in range(1, lookback + 1):
                if df['low'].iloc[i] >= df['low'].iloc[i-j] or df['low'].iloc[i] >= df['low'].iloc[i+j]:
                    is_low = False
                    break
            if is_low:
                lows.append(i)
        
        return highs, lows
    
    def check_higher_structure(self, df: pd.DataFrame, trend: TrendDirection) -> bool:
        """
        Check for Higher High/Higher Low (bullish) or Lower High/Lower Low (bearish) structure.
        
        Args:
            df: DataFrame with OHLCV data
            trend: Expected trend direction
            
        Returns:
            True if structure is aligned with trend
        """
        if df is None or len(df) < config.HH_HL_LOOKBACK:
            return False
        
        # Get recent data
        recent_df = df.tail(config.HH_HL_LOOKBACK).reset_index(drop=True)
        
        # Find swing points
        swing_highs, swing_lows = self.find_swing_points(recent_df, lookback=3)
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return False
        
        # Get last 2 swing highs and lows
        last_two_highs = [recent_df['high'].iloc[i] for i in swing_highs[-2:]]
        last_two_lows = [recent_df['low'].iloc[i] for i in swing_lows[-2:]]
        
        if trend == TrendDirection.BULLISH:
            # Check for Higher High and Higher Low
            higher_high = last_two_highs[-1] > last_two_highs[-2]
            higher_low = last_two_lows[-1] > last_two_lows[-2]
            return higher_high and higher_low
        
        elif trend == TrendDirection.BEARISH:
            # Check for Lower High and Lower Low
            lower_high = last_two_highs[-1] < last_two_highs[-2]
            lower_low = last_two_lows[-1] < last_two_lows[-2]
            return lower_high and lower_low
        
        return False
    
    def is_trend_aligned(self, df_h4: pd.DataFrame) -> Optional[TrendDirection]:
        """
        Step 1: Check if H4 trend is aligned (price vs EMA 200 + market structure).
        
        Args:
            df_h4: H4 timeframe DataFrame with indicators
            
        Returns:
            TrendDirection or None if no clear trend
        """
        if df_h4 is None or df_h4.empty or 'ema200' not in df_h4.columns:
            return None
        
        # Check last 3 candles for confirmation
        recent_candles = df_h4.tail(3)
        current_close = df_h4['close'].iloc[-1]
        ema200 = df_h4['ema200'].iloc[-1]
        
        # Skip if EMA200 not ready
        if pd.isna(ema200):
            return None
        
        # Bullish: price above EMA 200 + Higher High/Higher Low
        if all(recent_candles['close'] > recent_candles['ema200']):
            if self.check_higher_structure(df_h4, TrendDirection.BULLISH):
                return TrendDirection.BULLISH
        
        # Bearish: price below EMA 200 + Lower High/Lower Low
        if all(recent_candles['close'] < recent_candles['ema200']):
            if self.check_higher_structure(df_h4, TrendDirection.BEARISH):
                return TrendDirection.BEARISH
        
        return None
    
    def calculate_fibonacci_levels(self, df: pd.DataFrame, trend: TrendDirection) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels from recent swing.
        
        Args:
            df: DataFrame with OHLCV data
            trend: Current trend direction
            
        Returns:
            Dict with Fibonacci levels
        """
        if df is None or len(df) < 20:
            return {}
        
        recent_df = df.tail(50)
        
        if trend == TrendDirection.BULLISH:
            # For bullish, find the recent low to high swing
            swing_low = recent_df['low'].min()
            swing_high = recent_df['high'].max()
        else:
            # For bearish, find the recent high to low swing
            swing_high = recent_df['high'].max()
            swing_low = recent_df['low'].min()
        
        diff = swing_high - swing_low
        
        return {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'fib_0.236': swing_high - (diff * 0.236),
            'fib_0.382': swing_high - (diff * 0.382),
            'fib_0.5': swing_high - (diff * 0.5),
            'fib_0.618': swing_high - (diff * 0.618),
            'fib_0.786': swing_high - (diff * 0.786),
        }

    def _calculate_h1_sr_zone_percent(self, df_h1: pd.DataFrame) -> float:
        """
        Calculate dynamic H1 S/R zone half-width (%), clamped in configured range.
        Uses recent median candle range as a volatility proxy.
        """
        min_pct = config.H1_SR_ZONE_MIN_PERCENT
        max_pct = config.H1_SR_ZONE_MAX_PERCENT

        if df_h1 is None or len(df_h1) < 20:
            return (min_pct + max_pct) / 2.0

        recent = df_h1.tail(20)
        close = recent['close'].replace(0, np.nan)
        range_pct_series = ((recent['high'] - recent['low']) / close) * 100
        range_pct = float(range_pct_series.median()) if not range_pct_series.dropna().empty else (min_pct + max_pct) / 2.0

        return float(np.clip(range_pct, min_pct, max_pct))

    def _cluster_levels_to_strong_zones(
        self,
        levels: List[float],
        zone_percent: float
    ) -> List[Dict]:
        """Cluster nearby swing levels; keep clusters with enough touches as strong zones."""
        clean_levels = sorted([float(x) for x in levels if pd.notna(x) and x > 0])
        if not clean_levels:
            return []

        clusters: List[List[float]] = [[clean_levels[0]]]
        for level in clean_levels[1:]:
            current_center = float(np.mean(clusters[-1]))
            diff_pct = abs(level - current_center) / current_center * 100
            if diff_pct <= zone_percent:
                clusters[-1].append(level)
            else:
                clusters.append([level])

        zones = []
        for cluster in clusters:
            touches = len(cluster)
            if touches < config.H1_SR_MIN_TOUCHES:
                continue

            level = float(np.mean(cluster))
            half_width = level * (zone_percent / 100.0)
            zones.append({
                'level': level,
                'touches': touches,
                'zone_percent': zone_percent,
                'zone_low': level - half_width,
                'zone_high': level + half_width,
            })

        return zones

    def find_strong_h1_zones(self, df_h1: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Build strong support/resistance zones on H1 from clustered swing highs/lows.
        """
        if df_h1 is None or len(df_h1) < max(50, config.H1_SR_LOOKBACK_CANDLES):
            return {'supports': [], 'resistances': []}

        recent_df = df_h1.tail(config.H1_SR_LOOKBACK_CANDLES).reset_index(drop=True)
        swing_highs, swing_lows = self.find_swing_points(
            recent_df,
            lookback=config.H1_SR_SWING_LOOKBACK
        )

        support_levels = [recent_df['low'].iloc[i] for i in swing_lows]
        resistance_levels = [recent_df['high'].iloc[i] for i in swing_highs]
        zone_percent = self._calculate_h1_sr_zone_percent(recent_df)

        supports = self._cluster_levels_to_strong_zones(support_levels, zone_percent)
        resistances = self._cluster_levels_to_strong_zones(resistance_levels, zone_percent)

        # Sort for easier nearest-zone matching
        supports = sorted(supports, key=lambda z: z['level'])
        resistances = sorted(resistances, key=lambda z: z['level'])

        return {'supports': supports, 'resistances': resistances}

    def is_touching_strong_h1_zone(
        self,
        df_h1: pd.DataFrame,
        trend: TrendDirection
    ) -> Tuple[bool, str]:
        """
        Confirm current H1 candle is touching a strong zone:
        - Bullish: strong support zone
        - Bearish: strong resistance zone
        """
        zones = self.find_strong_h1_zones(df_h1)
        if not zones['supports'] and not zones['resistances']:
            return False, ""

        last = df_h1.iloc[-1]
        close = float(last['close'])
        high = float(last['high'])
        low = float(last['low'])

        if trend == TrendDirection.BULLISH:
            candidates = zones['supports']
            zone_label = "support"
        elif trend == TrendDirection.BEARISH:
            candidates = zones['resistances']
            zone_label = "resistance"
        else:
            return False, ""

        touched = []
        for zone in candidates:
            zone_low = zone['zone_low']
            zone_high = zone['zone_high']
            wick_touches = low <= zone_high and high >= zone_low
            close_in_zone = zone_low <= close <= zone_high
            if wick_touches or close_in_zone:
                distance_pct = abs(close - zone['level']) / zone['level'] * 100
                touched.append((distance_pct, zone))

        if not touched:
            return False, ""

        # Best zone = nearest to current close; tie-breaker: more touches
        touched.sort(key=lambda item: (item[0], -item[1]['touches']))
        distance_pct, best = touched[0]
        return (
            True,
            (
                f"H1 strong {zone_label} zone "
                f"{best['zone_low']:.4f}-{best['zone_high']:.4f} "
                f"({best['touches']} touches, {distance_pct:.2f}% from center)"
            )
        )
    
    def is_in_value_zone(
        self, 
        df_h1: pd.DataFrame, 
        df_h4: pd.DataFrame,
        trend: TrendDirection
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Step 2: Check if H1 price is in value zone.
        - Pullback to Fibonacci 0.5-0.618 from H4 swing
        - OR touching EMA 34/89 on H1
        
        Args:
            df_h1: H1 timeframe DataFrame with indicators
            df_h4: H4 timeframe DataFrame for Fibonacci calculation
            trend: Current trend direction from H4
            
        Returns:
            Tuple of (is_in_zone, zone_description, fib_level)
        """
        if df_h1 is None or df_h1.empty:
            return False, "", None
        
        if 'ema34' not in df_h1.columns or 'ema89' not in df_h1.columns:
            return False, "", None
        
        last_candle = df_h1.iloc[-1]
        close = last_candle['close']
        high = last_candle['high']
        low = last_candle['low']
        ema34 = last_candle['ema34']
        ema89 = last_candle['ema89']
        
        # Skip if EMAs not ready
        if pd.isna(ema34) or pd.isna(ema89):
            return False, "", None
        
        # Calculate Fibonacci levels from H4
        fib_levels = self.calculate_fibonacci_levels(df_h4, trend)
        
        if not fib_levels:
            return False, "", None
        
        fib_50 = fib_levels['fib_0.5']
        fib_618 = fib_levels['fib_0.618']
        
        tolerance = 0.01  # 1% tolerance
        
        base_match = False
        base_desc = ""
        fib_level: Optional[float] = None

        if trend == TrendDirection.BULLISH:
            # Check Fibonacci zone (price should be between 0.5 and 0.618)
            if fib_618 <= close <= fib_50:
                fib_level = (close - fib_618) / (fib_50 - fib_618) * 0.118 + 0.5
                base_match = True
                base_desc = f"Fibonacci {fib_level:.3f} zone"
            
            # Check EMA pullback
            if (not base_match) and (abs(close - ema34) / ema34 < tolerance or (low <= ema34 * 1.01 and close > ema34)):
                base_match = True
                base_desc = "EMA34 pullback"
            
            if (not base_match) and (abs(close - ema89) / ema89 < tolerance or (low <= ema89 * 1.01 and close > ema89)):
                base_match = True
                base_desc = "EMA89 pullback"
        
        elif trend == TrendDirection.BEARISH:
            # Check Fibonacci zone (price should be between 0.5 and 0.618)
            if fib_50 <= close <= fib_618:
                fib_level = (close - fib_50) / (fib_618 - fib_50) * 0.118 + 0.5
                base_match = True
                base_desc = f"Fibonacci {fib_level:.3f} zone"
            
            # Check EMA rejection
            if (not base_match) and (abs(close - ema34) / ema34 < tolerance or (high >= ema34 * 0.99 and close < ema34)):
                base_match = True
                base_desc = "EMA34 rejection"
            
            if (not base_match) and (abs(close - ema89) / ema89 < tolerance or (high >= ema89 * 0.99 and close < ema89)):
                base_match = True
                base_desc = "EMA89 rejection"

        if not base_match:
            return False, "", None

        # Additional required filter: H1 must also touch strong S/R zone (1.0-1.5%).
        sr_match, sr_desc = self.is_touching_strong_h1_zone(df_h1, trend)
        if not sr_match:
            return False, "", None

        return True, f"{base_desc} + {sr_desc}", fib_level
    
    def detect_pinbar(self, df: pd.DataFrame, trend: TrendDirection) -> Optional[Dict]:
        """
        Detect Pinbar pattern (long wick rejecting a level).
        
        Args:
            df: DataFrame with OHLCV data
            trend: Expected trend direction
            
        Returns:
            Dict with pattern details or None
        """
        if df is None or len(df) < 1:
            return None
        
        candle = df.iloc[-1]
        open_price = candle['open']
        close = candle['close']
        high = candle['high']
        low = candle['low']
        
        body = abs(close - open_price)
        total_range = high - low
        
        if total_range == 0:
            return None
        
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        
        # Bullish Pinbar (long lower wick)
        if trend == TrendDirection.BULLISH:
            lower_wick_ratio = lower_wick / total_range
            
            if lower_wick_ratio >= config.PINBAR_WICK_RATIO and lower_wick > upper_wick * 2:
                return {
                    'pattern': 'Bullish Pinbar',
                    'entry': close,
                    'stop_loss': low,
                    'risk': close - low
                }
        
        # Bearish Pinbar / Shooting Star (long upper wick)
        elif trend == TrendDirection.BEARISH:
            upper_wick_ratio = upper_wick / total_range
            
            if upper_wick_ratio >= config.PINBAR_WICK_RATIO and upper_wick > lower_wick * 2:
                return {
                    'pattern': 'Shooting Star',
                    'entry': close,
                    'stop_loss': high,
                    'risk': high - close
                }
        
        return None
    
    def detect_engulfing(self, df: pd.DataFrame, trend: TrendDirection) -> Optional[Dict]:
        """
        Step 3: Detect Engulfing candle pattern on M15.
        
        Args:
            df: DataFrame with OHLCV data
            trend: Current trend direction
            
        Returns:
            Dict with pattern details or None
        """
        if df is None or len(df) < 2:
            return None
        
        # Get last 2 candles
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        prev_open = prev_candle['open']
        prev_close = prev_candle['close']
        curr_open = curr_candle['open']
        curr_close = curr_candle['close']
        
        # Bullish Engulfing (for LONG entry)
        if trend == TrendDirection.BULLISH:
            # Previous candle is bearish (red)
            prev_bearish = prev_close < prev_open
            # Current candle is bullish (green)
            curr_bullish = curr_close > curr_open
            # Current candle engulfs previous
            engulfs = curr_open <= prev_close and curr_close >= prev_open
            
            if prev_bearish and curr_bullish and engulfs:
                return {
                    'pattern': 'Bullish Engulfing',
                    'entry': curr_close,
                    'stop_loss': curr_candle['low'],
                    'risk': curr_close - curr_candle['low']
                }
        
        # Bearish Engulfing (for SHORT entry)
        elif trend == TrendDirection.BEARISH:
            # Previous candle is bullish (green)
            prev_bullish = prev_close > prev_open
            # Current candle is bearish (red)
            curr_bearish = curr_close < curr_open
            # Current candle engulfs previous
            engulfs = curr_open >= prev_close and curr_close <= prev_open
            
            if prev_bullish and curr_bearish and engulfs:
                return {
                    'pattern': 'Bearish Engulfing',
                    'entry': curr_close,
                    'stop_loss': curr_candle['high'],
                    'risk': curr_candle['high'] - curr_close
                }
        
        return None
    
    def detect_rsi_divergence(self, df: pd.DataFrame, trend: TrendDirection) -> bool:
        """
        Detect RSI divergence (bullish or bearish).
        
        Args:
            df: DataFrame with RSI calculated
            trend: Expected trend direction
            
        Returns:
            True if divergence detected
        """
        if df is None or len(df) < 20 or 'rsi' not in df.columns:
            return False
        
        recent_df = df.tail(20)
        
        # Find swing points in price and RSI
        price_highs, price_lows = self.find_swing_points(recent_df, lookback=2)
        
        if len(price_highs) < 2 and len(price_lows) < 2:
            return False
        
        # Bullish Divergence: Price makes lower low, RSI makes higher low
        if trend == TrendDirection.BULLISH and len(price_lows) >= 2:
            last_two_lows = price_lows[-2:]
            price_low_1 = recent_df['low'].iloc[last_two_lows[0]]
            price_low_2 = recent_df['low'].iloc[last_two_lows[1]]
            rsi_low_1 = recent_df['rsi'].iloc[last_two_lows[0]]
            rsi_low_2 = recent_df['rsi'].iloc[last_two_lows[1]]
            
            if price_low_2 < price_low_1 and rsi_low_2 > rsi_low_1:
                return True  # Bullish divergence
        
        # Bearish Divergence: Price makes higher high, RSI makes lower high
        elif trend == TrendDirection.BEARISH and len(price_highs) >= 2:
            last_two_highs = price_highs[-2:]
            price_high_1 = recent_df['high'].iloc[last_two_highs[0]]
            price_high_2 = recent_df['high'].iloc[last_two_highs[1]]
            rsi_high_1 = recent_df['rsi'].iloc[last_two_highs[0]]
            rsi_high_2 = recent_df['rsi'].iloc[last_two_highs[1]]
            
            if price_high_2 > price_high_1 and rsi_high_2 < rsi_high_1:
                return True  # Bearish divergence
        
        return False
    
    def check_volume_confirmation(self, df: pd.DataFrame) -> Tuple[bool, float]:
        """
        Check if current volume is above average (confirmation).
        
        Args:
            df: DataFrame with volume data
            
        Returns:
            Tuple of (is_confirmed, volume_ratio)
        """
        if df is None or len(df) < 2 or 'volume_ma' not in df.columns:
            return False, 0.0
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume_ma'].iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return False, 0.0
        
        volume_ratio = current_volume / avg_volume
        
        return volume_ratio >= config.VOLUME_MULTIPLIER, volume_ratio
    
    def get_entry_signal(
        self, 
        df_m15: pd.DataFrame, 
        trend: TrendDirection
    ) -> Optional[Dict]:
        """
        Step 3: Get entry signal from M15 with multiple confirmations.
        
        Args:
            df_m15: M15 timeframe DataFrame
            trend: Current trend direction
            
        Returns:
            Dict with signal details or None
        """
        if df_m15 is None or len(df_m15) < 20:
            return None
        
        # Check for candlestick patterns
        engulfing = self.detect_engulfing(df_m15, trend)
        pinbar = self.detect_pinbar(df_m15, trend)
        
        pattern_found = engulfing or pinbar
        
        if not pattern_found:
            return None
        
        # Get the pattern to use
        pattern = engulfing if engulfing else pinbar
        
        # Check RSI divergence (optional but adds confidence)
        has_divergence = self.detect_rsi_divergence(df_m15, trend)
        
        # Check volume confirmation (REQUIRED)
        volume_confirmed, volume_ratio = self.check_volume_confirmation(df_m15)
        
        if not volume_confirmed:
            return None  # Volume confirmation is mandatory
        
        # Add confirmations to pattern
        pattern['has_divergence'] = has_divergence
        pattern['volume_ratio'] = volume_ratio
        pattern['volume_confirmed'] = volume_confirmed
        
        return pattern
    
    def analyze_symbol(
        self,
        symbol: str,
        data_h4: pd.DataFrame,
        data_h1: pd.DataFrame,
        data_m15: pd.DataFrame
    ) -> Optional[Signal]:
        """
        Analyze a symbol across all timeframes using the enhanced 3-step filter.
        
        Args:
            symbol: Trading pair symbol
            data_h4: H4 candle data
            data_h1: H1 candle data
            data_m15: M15 candle data
            
        Returns:
            Signal object if all conditions met, None otherwise
        """
        # Calculate indicators for all timeframes
        df_h4 = self.calculate_indicators(data_h4)
        df_h1 = self.calculate_indicators(data_h1)
        df_m15 = self.calculate_indicators(data_m15)
        
        # Step 1: Check H4 trend with structure
        trend = self.is_trend_aligned(df_h4)
        if not trend or trend == TrendDirection.NEUTRAL:
            return None
        
        # Step 2: Check H1 value zone with Fibonacci
        in_zone, zone_desc, fib_level = self.is_in_value_zone(df_h1, df_h4, trend)
        if not in_zone:
            return None
        
        # Step 3: Check M15 entry signal with volume
        entry_signal = self.get_entry_signal(df_m15, trend)
        if not entry_signal:
            return None
        
        # Áp dụng stop loss min/max (config) — SL từ nến có thể quá ngắn
        entry = entry_signal['entry']
        sl_raw = entry_signal['stop_loss']
        min_pct = config.STOP_LOSS_MIN_PERCENT / 100.0
        max_pct = config.STOP_LOSS_MAX_PERCENT / 100.0
        
        if trend == TrendDirection.BULLISH:
            risk_distance = entry - sl_raw
            min_dist = entry * min_pct
            max_dist = entry * max_pct
            risk_distance = max(min_dist, min(max_dist, risk_distance))
            stop_loss = entry - risk_distance
        else:
            risk_distance = sl_raw - entry
            min_dist = entry * min_pct
            max_dist = entry * max_pct
            risk_distance = max(min_dist, min(max_dist, risk_distance))
            stop_loss = entry + risk_distance
        
        risk = risk_distance
        reward_ratio = 2.0  # 1:2 risk-reward ratio
        
        if trend == TrendDirection.BULLISH:
            take_profit = entry + (risk * reward_ratio)
        else:
            take_profit = entry - (risk * reward_ratio)
        
        # Build reason string
        reason_parts = [
            f"H4 trend {trend.value} with HH/HL structure",
            f"H1 {zone_desc}",
            f"M15 {entry_signal['pattern']}"
        ]
        
        if entry_signal.get('has_divergence'):
            reason_parts.append("RSI Divergence")
        
        reason_parts.append(f"Volume {entry_signal['volume_ratio']:.2f}x")
        
        signal = Signal(
            symbol=symbol,
            direction=trend,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timeframe='M15',
            pattern=entry_signal['pattern'],
            reason=", ".join(reason_parts),
            h4_ema200=df_h4['ema200'].iloc[-1],
            h1_ema34=df_h1['ema34'].iloc[-1],
            h1_ema89=df_h1['ema89'].iloc[-1],
            current_price=df_m15['close'].iloc[-1],
            rsi=df_m15['rsi'].iloc[-1],
            volume_ratio=entry_signal['volume_ratio'],
            fib_level=fib_level
        )
        
        return signal


def test_strategy():
    """Test function for strategy engine."""
    engine = StrategyEngine()
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=300, freq='4h')
    sample_data = pd.DataFrame({
        'open': range(100, 400),
        'high': range(101, 401),
        'low': range(99, 399),
        'close': range(100, 400),
        'volume': [1000] * 300
    }, index=dates)
    
    df = engine.calculate_indicators(sample_data)
    print("✅ Strategy Engine Test:")
    print(f"  Calculated indicators: {list(df.columns)}")
    print(f"  Last EMA200: {df['ema200'].iloc[-1]:.2f}")
    print(f"  Last RSI: {df['rsi'].iloc[-1]:.2f}")
    
    # Test structure detection
    trend = engine.is_trend_aligned(df)
    print(f"  Trend: {trend}")


if __name__ == "__main__":
    test_strategy()
