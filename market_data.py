"""
Market Data Module - Fetches OHLCV and market data from Binance Futures via ccxt.
Uses BINANCE_API_KEY and BINANCE_SECRET_KEY from config.
"""
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
import config


class MarketDataFetcher:
    """
    Fetches market data from Binance Futures using ccxt with API credentials.
    """

    def __init__(self):
        """Initialize Binance USDT-M Futures (chỉ dùng fapi.binance.com, không dùng dapi)."""
        base_url = (config.BINANCE_FUTURE_API_BASE_URL or 'https://fapi.binance.com/').rstrip('/')

        self.exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY or '',
            'secret': config.BINANCE_SECRET_KEY or '',
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'fapi': base_url,
                }
            }
        })
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        self.request_delay = config.REQUEST_DELAY_SECONDS
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """
        Close ccxt exchange session safely.
        Uses shield so cancellation/reload does not skip closing aiohttp session.
        """
        if self._closed:
            return
        try:
            await asyncio.shield(self.exchange.close())
        except Exception:
            # Avoid crashing shutdown path; we only need best-effort cleanup.
            pass
        finally:
            self._closed = True

    async def get_futures_symbols(self, sort_by: str = 'volume', limit: Optional[int] = None) -> List[str]:
        """Fetch USDT-margined futures symbols. sort_by: 'volume' or 'alphabetical'."""
        try:
            print("📊 Đang lấy danh sách cặp Futures...")
            await self.exchange.load_markets()

            # Lọc USDT-margined futures (ccxt mới dùng future=True, type có thể vẫn 'spot')
            # Symbol perpetual: 'BTC/USDT' hoặc 'BTC/USDT:USDT'; loại bỏ futures theo kỳ hạn (có _)
            futures_symbols = []
            for symbol, market in self.exchange.markets.items():
                if symbol is None or not isinstance(symbol, str):
                    continue
                if market.get('quote') != 'USDT':
                    continue
                if market.get('active', True) is False:
                    continue
                # Bỏ qua futures theo kỳ hạn (symbol dạng BASE/USDT_250328); giữ perpetual (BTC/USDT, BTC/USDT:USDT)
                market_id = (market.get('id') or symbol) or ''
                if '_' in market_id and any(c.isdigit() for c in market_id):
                    continue
                if limit is not None and len(futures_symbols) > limit:
                    break
                futures_symbols.append(symbol)

            print(f"✅ Tìm thấy {len(futures_symbols)} cặp Futures USDT")

            if sort_by == 'volume':
                print("📊 Đang sắp xếp theo volume 24h...")
                try:
                    tickers = await self.exchange.fetch_tickers(futures_symbols)
                    if not tickers:
                        raise ValueError("Empty tickers response")
                    symbols_with_volume = []
                    for symbol in futures_symbols:
                        if symbol is None:
                            continue
                        ticker = tickers.get(symbol) or {}
                        vol = ticker.get('quoteVolume') if isinstance(ticker, dict) else None
                        try:
                            vol = float(vol) if vol is not None else 0.0
                        except (TypeError, ValueError):
                            vol = 0.0
                        symbols_with_volume.append((symbol, vol))
                    symbols_with_volume.sort(key=lambda x: (x[1] or 0), reverse=True)
                    sorted_symbols = [s for s, _ in symbols_with_volume if s is not None]
                    if sorted_symbols:
                        top_5 = [s for s in sorted_symbols[:5] if s]
                        if top_5:
                            print(f"   Top 5 by volume: {', '.join(str(s) for s in top_5)}")
                except Exception as e:
                    print(f"⚠️  Không thể sort by volume: {e}, dùng alphabetical")
                    sorted_symbols = sorted([s for s in futures_symbols if s is not None and isinstance(s, str)])
            else:
                sorted_symbols = sorted([s for s in futures_symbols if s is not None and isinstance(s, str)])

            if limit is not None and limit > 0 and sorted_symbols:
                sorted_symbols = sorted_symbols[:limit]
                print(f"🔍 Giới hạn: {len(sorted_symbols)}/{len(futures_symbols)} cặp")

            return sorted_symbols if sorted_symbols is not None else []

        except Exception as e:
            print(f"❌ Lỗi khi lấy danh sách symbols: {e}")
            return []

    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = config.CANDLE_LIMIT
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLCV for symbol/timeframe. Uses semaphore and delay."""
        async with self.semaphore:
            try:
                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit
                )
                if not ohlcv:
                    return None
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                await asyncio.sleep(self.request_delay)
                return df
            except ccxt.RateLimitExceeded:
                print(f"⚠️  Rate limit exceeded cho {symbol} - đang chờ...")
                await asyncio.sleep(5)
                return None
            except Exception as e:
                print(f"❌ Lỗi khi lấy dữ liệu {symbol} {timeframe}: {e}")
                return None

    async def fetch_multi_timeframe_data(
        self,
        symbol: str,
        timeframes: Dict[str, str]
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """Fetch candles for multiple timeframes for one symbol."""
        tasks = [self.fetch_candles(symbol, tf) for tf in timeframes.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            name: result if not isinstance(result, Exception) else None
            for name, result in zip(timeframes.keys(), results)
        }

    async def scan_market(
        self,
        symbols: List[str],
        timeframe: str,
        limit: int = config.CANDLE_LIMIT
    ) -> Dict[str, pd.DataFrame]:
        """Scan multiple symbols for one timeframe."""
        print(f"🔍 Đang quét {len(symbols)} symbols cho khung {timeframe}...")
        tasks = [self.fetch_candles(symbol, timeframe, limit=limit) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        market_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame) and not result.empty:
                market_data[symbol] = result
        print(f"✅ Lấy thành công dữ liệu cho {len(market_data)}/{len(symbols)} symbols")
        return market_data

    async def fetch_rvol(
        self,
        symbol: str,
        lookback_days: int = 7
    ) -> float:
        """
        Calculate Relative Volume (RVOL):
        24h current volume / average 24h volume of the previous N days (default: 7 days).
        Uses daily candles (1d).
        """
        try:
            limit = max(lookback_days + 3, 10)
            df_1d = await self.fetch_candles(symbol, '1d', limit=limit)
            if df_1d is None or len(df_1d) < lookback_days + 1:
                return 1.0

            # 7 nến ngày hoàn chỉnh trước ngày hôm nay
            past_candles = df_1d.iloc[-(lookback_days + 1):-1]
            avg_7d_vol = float(past_candles['volume'].mean())

            # Lấy 24h rolling volume từ ticker nếu khả dụng
            current_24h_vol = None
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                if ticker and ticker.get('baseVolume') is not None:
                    current_24h_vol = float(ticker['baseVolume'])
            except Exception:
                current_24h_vol = None

            if current_24h_vol is None or current_24h_vol <= 0:
                current_24h_vol = float(df_1d['volume'].iloc[-1])

            if avg_7d_vol and avg_7d_vol > 0:
                return round(float(current_24h_vol / avg_7d_vol), 2)
            return 1.0
        except Exception as e:
            print(f"⚠️  Không thể tính RVOL cho {symbol}: {e}")
            return 1.0

    async def fetch_rvol_batch(
        self,
        symbols: List[str],
        lookback_days: int = 7
    ) -> Dict[str, float]:
        """Fetch RVOL for multiple symbols concurrently."""
        if not symbols:
            return {}
        tasks = [self.fetch_rvol(sym, lookback_days) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        rvol_map = {}
        for sym, res in zip(symbols, results):
            rvol_map[sym] = float(res) if isinstance(res, (int, float)) else 1.0
        return rvol_map


async def test_market_data():
    """Test market data fetching."""
    async with MarketDataFetcher() as fetcher:
        all_symbols = await fetcher.get_futures_symbols(sort_by='alphabetical', limit=None)
        print(f"\nTest: Lấy được {len(all_symbols)} symbols\n")
        top_10 = await fetcher.get_futures_symbols(sort_by='volume', limit=10)
        print(f"Top 10: {', '.join(top_10)}\n")
        if top_10:
            test_symbol = 'BTC/USDT' if 'BTC/USDT' in top_10 else top_10[0]
            data = await fetcher.fetch_multi_timeframe_data(test_symbol, config.TIMEFRAMES)
            for name, df in data.items():
                if df is not None:
                    print(f"  {name}: {len(df)} nến, latest close: {df['close'].iloc[-1]:.2f}")


if __name__ == "__main__":
    asyncio.run(test_market_data())
