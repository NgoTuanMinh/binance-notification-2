"""
Market Data Module - Fetches public OHLCV data from Binance Futures.
Uses only public API endpoints, no authentication required.
"""
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
import config


class MarketDataFetcher:
    """
    Fetches market data from Binance Futures using public API endpoints.
    Implements rate limiting to avoid IP bans.
    """
    
    def __init__(self):
        """
        Initialize Binance exchange connection.
        NOTE: No API key/secret required - using public endpoints only.
        """
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use Futures market
            }
        })
        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        self.request_delay = config.REQUEST_DELAY_SECONDS
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close exchange connection."""
        await self.exchange.close()
        
    async def get_futures_symbols(self, sort_by: str = 'volume', limit: Optional[int] = None) -> List[str]:
        """
        Fetch all USDT-margined futures trading pairs.
        
        Args:
            sort_by: Sorting method - 'volume' (by 24h volume) or 'alphabetical'
            limit: Maximum number of symbols to return (None for all)
        
        Returns:
            List of trading symbols (e.g., ['BTC/USDT', 'ETH/USDT', ...])
        """
        try:
            print("📊 Đang lấy danh sách cặp Futures...")
            await self.exchange.load_markets()
            
            # Filter for USDT futures pairs that are active (exclude None symbols)
            futures_symbols = [
                symbol for symbol, market in self.exchange.markets.items()
                if symbol is not None
                and isinstance(symbol, str)
                and market.get('quote') == 'USDT' 
                and market.get('type') == 'future'
                and market.get('active', False)
                and ':USDT' not in symbol  # Exclude date-specific futures
            ]
            
            print(f"✅ Tìm thấy {len(futures_symbols)} cặp Futures USDT")
            
            # Sort symbols
            if sort_by == 'volume':
                print("📊 Đang sắp xếp theo volume 24h...")
                # Fetch tickers to get volume data
                try:
                    tickers = await self.exchange.fetch_tickers(futures_symbols)
                    if not tickers:
                        raise ValueError("Empty tickers response")
                    # Sort by 24h volume (descending), handle None safely
                    symbols_with_volume = []
                    for symbol in futures_symbols:
                        if symbol is None:
                            continue
                        ticker = tickers.get(symbol)
                        if ticker is None:
                            ticker = {}
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
                # Sort alphabetically
                sorted_symbols = sorted([s for s in futures_symbols if s is not None and isinstance(s, str)])
            
            # Apply limit if specified
            if limit is not None and limit > 0 and sorted_symbols:
                sorted_symbols = sorted_symbols[:limit]
                total = len(futures_symbols)
                print(f"🔍 Giới hạn: {len(sorted_symbols)}/{total} cặp")
            
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
        """
        Fetch OHLCV candlestick data for a specific symbol and timeframe.
        Uses semaphore to limit concurrent requests.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candlestick timeframe (e.g., '4h', '1h', '15m')
            limit: Number of candles to fetch (default: 500)
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        async with self.semaphore:  # Limit concurrent requests
            try:
                # Fetch OHLCV data from public API
                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit
                )
                
                if not ohlcv:
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(self.request_delay)
                
                return df
                
            except ccxt.RateLimitExceeded:
                print(f"⚠️  Rate limit exceeded cho {symbol} - đang chờ...")
                await asyncio.sleep(5)  # Wait longer if rate limited
                return None
            except Exception as e:
                print(f"❌ Lỗi khi lấy dữ liệu {symbol} {timeframe}: {e}")
                return None
    
    async def fetch_multi_timeframe_data(
        self, 
        symbol: str,
        timeframes: Dict[str, str]
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch candle data for multiple timeframes for a single symbol.
        
        Args:
            symbol: Trading pair
            timeframes: Dict mapping names to timeframe strings
                       e.g., {'trend': '4h', 'value': '1h', 'signal': '15m'}
        
        Returns:
            Dict mapping timeframe names to DataFrames
        """
        tasks = []
        for name, tf in timeframes.items():
            tasks.append(self.fetch_candles(symbol, tf))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            name: result if not isinstance(result, Exception) else None
            for name, result in zip(timeframes.keys(), results)
        }
    
    async def scan_market(
        self, 
        symbols: List[str], 
        timeframe: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Scan multiple symbols for a specific timeframe.
        
        Args:
            symbols: List of trading pairs to scan
            timeframe: Timeframe to fetch
            
        Returns:
            Dict mapping symbols to their DataFrames
        """
        print(f"🔍 Đang quét {len(symbols)} symbols cho khung {timeframe}...")
        
        tasks = [self.fetch_candles(symbol, timeframe) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        market_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame) and not result.empty:
                market_data[symbol] = result
        
        print(f"✅ Lấy thành công dữ liệu cho {len(market_data)}/{len(symbols)} symbols")
        return market_data


async def test_market_data():
    """Test function to verify market data fetching."""
    async with MarketDataFetcher() as fetcher:
        # Get list of symbols (all)
        print("Test 1: Lấy tất cả symbols")
        all_symbols = await fetcher.get_futures_symbols(sort_by='alphabetical', limit=None)
        print(f"  ✅ Lấy được {len(all_symbols)} symbols\n")
        
        # Get top 10 by volume
        print("Test 2: Lấy top 10 symbols by volume")
        top_10 = await fetcher.get_futures_symbols(sort_by='volume', limit=10)
        print(f"  ✅ Top 10: {', '.join(top_10)}\n")
        
        # Test fetching data for BTC/USDT
        if top_10:
            test_symbol = 'BTC/USDT' if 'BTC/USDT' in top_10 else top_10[0]
            print(f"Test 3: Lấy dữ liệu nến cho {test_symbol}...")
            
            data = await fetcher.fetch_multi_timeframe_data(
                test_symbol,
                config.TIMEFRAMES
            )
            
            for name, df in data.items():
                if df is not None:
                    print(f"  {name}: {len(df)} candles, latest close: {df['close'].iloc[-1]:.2f}")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_market_data())
