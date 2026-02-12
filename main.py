"""
Main Scanner - Orchestrates multi-timeframe market scanning with separate loops.
Implements 3 independent scanning loops:
- H4 Loop: Scans every 1 hour for trend filter
- H1 Loop: Scans every 15 minutes for value zone (on H4 passed symbols)
- M15 Loop: Scans every 1-3 minutes for entry signals (on hot watchlist)
"""
import asyncio
import time
import gc
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional
import pandas as pd

import config
from market_data import MarketDataFetcher
from strategy_engine import StrategyEngine, Signal, TrendDirection
from telegram_bot import TelegramBot


class DiskDataCache:
    """Simple disk-based cache for dataframe persistence between loops."""

    def __init__(self, cache_dir: str = ".runtime_cache"):
        self.base_dir = Path(cache_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_symbol(symbol: str) -> str:
        return symbol.replace("/", "_").replace(":", "_")

    def _file_path(self, timeframe: str, symbol: str) -> Path:
        tf_dir = self.base_dir / timeframe
        tf_dir.mkdir(parents=True, exist_ok=True)
        return tf_dir / f"{self._safe_symbol(symbol)}.pkl"

    def save_df(self, timeframe: str, symbol: str, df: pd.DataFrame) -> None:
        df.to_pickle(self._file_path(timeframe, symbol))

    def load_df(self, timeframe: str, symbol: str) -> Optional[pd.DataFrame]:
        path = self._file_path(timeframe, symbol)
        if not path.exists():
            return None
        try:
            return pd.read_pickle(path)
        except Exception:
            return None

    def clear_timeframe(self, timeframe: str) -> None:
        tf_dir = self.base_dir / timeframe
        if not tf_dir.exists():
            return
        for path in tf_dir.glob("*.pkl"):
            try:
                path.unlink()
            except Exception:
                pass

    def clear_all(self) -> None:
        self.clear_timeframe("h4")
        self.clear_timeframe("h1")


class MultiTimeframeScanner:
    """
    Multi-timeframe scanner with separate scanning loops for each timeframe.
    Implements efficient funnel filtering across timeframes.
    """
    
    def __init__(self):
        """Initialize scanner components and state."""
        self.strategy = StrategyEngine()
        self.telegram = TelegramBot()
        self.disk_cache = DiskDataCache()
        
        # State management for each stage
        self.all_symbols: List[str] = []
        self.candidate_symbols: Dict[str, TrendDirection] = {}  # H4 passed symbols with trend
        self.hot_watchlist: Dict[str, TrendDirection] = {}  # H1 passed symbols with trend
        self.seen_signals: Set[str] = set()  # Track sent signals
        
        # Data cache
        self.h4_data_cache: Dict[str, pd.DataFrame] = {}
        self.h1_data_cache: Dict[str, pd.DataFrame] = {}
        
        # Statistics
        self.stats = {
            'h4_scans': 0,
            'h1_scans': 0,
            'm15_scans': 0,
            'total_signals': 0
        }

    @staticmethod
    def _chunk_symbols(symbols: List[str], batch_size: int):
        """Yield symbols in small batches to reduce peak memory usage."""
        size = max(1, batch_size)
        for i in range(0, len(symbols), size):
            yield symbols[i:i + size]
    
    async def initialize(self):
        """Initialize by fetching all symbols."""
        # Clear stale on-disk cache from previous runs
        self.disk_cache.clear_all()

        async with MarketDataFetcher() as fetcher:
            self.all_symbols = await fetcher.get_futures_symbols(
                sort_by=config.SYMBOL_SORT_METHOD,
                limit=config.MAX_SYMBOLS_TO_SCAN
            )
        
        if self.all_symbols:
            limit_info = ""
            if config.MAX_SYMBOLS_TO_SCAN:
                limit_info = f" (giới hạn {config.MAX_SYMBOLS_TO_SCAN} cặp top {config.SYMBOL_SORT_METHOD})"
            
            print(f"✅ Khởi tạo: {len(self.all_symbols)} cặp Futures{limit_info}")
            
            telegram_msg = f"🤖 *BOT KHỞI ĐỘNG*\n\n"
            telegram_msg += f"Tổng số cặp: {len(self.all_symbols)}"
            if config.MAX_SYMBOLS_TO_SCAN:
                telegram_msg += f" (top {config.MAX_SYMBOLS_TO_SCAN} by {config.SYMBOL_SORT_METHOD})"
            telegram_msg += f"\n⏰ H4 scan: 1 giờ\n"
            telegram_msg += f"⏰ H1 scan: 15 phút\n"
            telegram_msg += f"⏰ M15 scan: 2 phút\n\n"
            telegram_msg += f"🔍 Đang bắt đầu quét..."
            
            await self.telegram.send_message(telegram_msg)
        else:
            print("❌ Không thể lấy danh sách symbols")
    
    async def scan_h4_trend_filter(self):
        """
        H4 LOOP: Scan every 1 hour to identify trending symbols.
        Output: Candidate_Symbols with trend direction.
        """
        while True:
            try:
                print("\n" + "="*70)
                print(f"📊 H4 TREND FILTER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                self.stats['h4_scans'] += 1
                start_time = time.time()
                self.disk_cache.clear_timeframe("h4")
                
                async with MarketDataFetcher() as fetcher:
                    # Filter symbols with clear trend and structure
                    new_candidates = {}

                    for batch_symbols in self._chunk_symbols(self.all_symbols, config.SCAN_BATCH_SIZE):
                        h4_data_batch = await fetcher.scan_market(
                            batch_symbols,
                            config.TIMEFRAMES['trend']
                        )

                        for symbol, df in h4_data_batch.items():
                            df_with_indicators = self.strategy.calculate_indicators(df)
                            trend = self.strategy.is_trend_aligned(df_with_indicators)

                            if trend and trend != TrendDirection.NEUTRAL:
                                new_candidates[symbol] = trend
                                self.disk_cache.save_df("h4", symbol, df)
                                print(f"  ✅ {symbol}: {trend.value}")

                        # Release batch dataframe references ASAP
                        del h4_data_batch
                    
                    # Update candidate list
                    self.candidate_symbols = new_candidates
                    self.h4_data_cache = {}
                    
                    duration = time.time() - start_time
                    
                    print(f"\n📈 Kết quả H4:")
                    print(f"  Candidates: {len(self.candidate_symbols)}/{len(self.all_symbols)}")
                    print(f"  Thời gian: {duration:.1f}s")
                    print(f"  Tiết kiệm: {len(self.all_symbols) - len(self.candidate_symbols)} symbols cho H1")
                
                # Wait 1 hour before next H4 scan
                print(f"⏸  H4: Chờ {config.SCAN_INTERVAL_H4/60:.0f} phút...")
                gc.collect()
                await asyncio.sleep(config.SCAN_INTERVAL_H4)
                
            except Exception as e:
                print(f"❌ Lỗi H4 scan: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def scan_h1_value_zone(self):
        """
        H1 LOOP: Scan every 15 minutes to find value zones.
        Only scans Candidate_Symbols from H4.
        Output: Hot_Watchlist ready for M15 signals.
        """
        # Wait a bit for H4 to complete first scan
        await asyncio.sleep(60)
        
        while True:
            try:
                if not self.candidate_symbols:
                    print("\n⏸  H1: Chờ H4 tạo danh sách candidates...")
                    await asyncio.sleep(config.SCAN_INTERVAL_H1)
                    continue
                
                print("\n" + "="*70)
                print(f"💎 H1 VALUE ZONE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                self.stats['h1_scans'] += 1
                start_time = time.time()
                self.disk_cache.clear_timeframe("h1")
                
                candidates_list = list(self.candidate_symbols.keys())
                
                async with MarketDataFetcher() as fetcher:
                    # Filter symbols in value zone
                    new_watchlist = {}

                    for batch_symbols in self._chunk_symbols(candidates_list, config.SCAN_BATCH_SIZE):
                        h1_data_batch = await fetcher.scan_market(
                            batch_symbols,
                            config.TIMEFRAMES['value']
                        )

                        for symbol in batch_symbols:
                            if symbol not in h1_data_batch:
                                continue

                            trend = self.candidate_symbols[symbol]
                            df_h4 = self.disk_cache.load_df("h4", symbol)
                            if df_h4 is None:
                                continue

                            df_h1 = self.strategy.calculate_indicators(h1_data_batch[symbol])

                            in_zone, zone_desc, fib_level = self.strategy.is_in_value_zone(
                                df_h1, df_h4, trend
                            )

                            if in_zone:
                                new_watchlist[symbol] = trend
                                self.disk_cache.save_df("h1", symbol, h1_data_batch[symbol])
                                print(f"  🎯 {symbol}: {zone_desc}")

                        # Release batch dataframe references ASAP
                        del h1_data_batch
                    
                    # Update hot watchlist
                    self.hot_watchlist = new_watchlist
                    self.h1_data_cache = {}
                    
                    duration = time.time() - start_time
                    
                    print(f"\n💎 Kết quả H1:")
                    print(f"  Hot Watchlist: {len(self.hot_watchlist)}/{len(candidates_list)}")
                    print(f"  Thời gian: {duration:.1f}s")
                    print(f"  Tiết kiệm: {len(candidates_list) - len(self.hot_watchlist)} symbols cho M15")
                
                # Wait 15 minutes before next H1 scan
                print(f"⏸  H1: Chờ {config.SCAN_INTERVAL_H1/60:.0f} phút...")
                gc.collect()
                await asyncio.sleep(config.SCAN_INTERVAL_H1)
                
            except Exception as e:
                print(f"❌ Lỗi H1 scan: {e}")
                await asyncio.sleep(300)
    
    async def scan_m15_entry_signals(self):
        """
        M15 LOOP: Scan every 1-3 minutes for entry signals.
        Only scans Hot_Watchlist from H1.
        Output: Trading signals sent to Telegram.
        """
        # Wait for H1 to complete first scan
        await asyncio.sleep(120)
        
        while True:
            try:
                if not self.hot_watchlist:
                    print("\n⏸  M15: Chờ H1 tạo hot watchlist...")
                    await asyncio.sleep(config.SCAN_INTERVAL_M15)
                    continue
                
                print("\n" + "="*70)
                print(f"🎯 M15 ENTRY SIGNALS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                
                self.stats['m15_scans'] += 1
                start_time = time.time()
                
                watchlist = list(self.hot_watchlist.keys())
                signals_found = []
                
                async with MarketDataFetcher() as fetcher:
                    # Fetch M15 data for hot watchlist only
                    m15_data = await fetcher.scan_market(
                        watchlist,
                        config.TIMEFRAMES['signal']
                    )
                    
                    # Check for entry signals
                    for symbol in watchlist:
                        if symbol not in m15_data:
                            continue
                        
                        df_h4 = self.disk_cache.load_df("h4", symbol)
                        df_h1 = self.disk_cache.load_df("h1", symbol)
                        if df_h4 is None or df_h1 is None:
                            continue
                        
                        df_m15 = m15_data[symbol]
                        
                        # Analyze for signal
                        signal = self.strategy.analyze_symbol(symbol, df_h4, df_h1, df_m15)
                        
                        if signal:
                            # Create unique key for deduplication
                            signal_key = f"{signal.symbol}_{signal.direction.value}_{int(signal.entry_price)}"
                            
                            if signal_key not in self.seen_signals:
                                signals_found.append(signal)
                                self.seen_signals.add(signal_key)
                                print(f"  🔔 SIGNAL: {symbol} - {signal.pattern}")
                    
                    duration = time.time() - start_time
                    
                    print(f"\n🎯 Kết quả M15:")
                    print(f"  Signals: {len(signals_found)}/{len(watchlist)}")
                    print(f"  Thời gian: {duration:.1f}s")
                
                # Send signals to Telegram
                if signals_found:
                    print(f"\n📤 Gửi {len(signals_found)} tín hiệu...")
                    for signal in signals_found:
                        await self.telegram.send_signal(signal)
                        self.stats['total_signals'] += 1
                        await asyncio.sleep(1)  # Avoid Telegram rate limit
                
                # Wait 1-3 minutes before next M15 scan
                print(f"⏸  M15: Chờ {config.SCAN_INTERVAL_M15/60:.1f} phút...")
                gc.collect()
                await asyncio.sleep(config.SCAN_INTERVAL_M15)
                
            except Exception as e:
                print(f"❌ Lỗi M15 scan: {e}")
                await asyncio.sleep(60)
    
    async def statistics_reporter(self):
        """Report statistics every hour."""
        await asyncio.sleep(3600)  # Wait 1 hour before first report
        
        while True:
            try:
                print("\n" + "="*70)
                print(f"📊 THỐNG KÊ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                print(f"  H4 scans: {self.stats['h4_scans']}")
                print(f"  H1 scans: {self.stats['h1_scans']}")
                print(f"  M15 scans: {self.stats['m15_scans']}")
                print(f"  Candidates: {len(self.candidate_symbols)}")
                print(f"  Watchlist: {len(self.hot_watchlist)}")
                print(f"  Total signals: {self.stats['total_signals']}")
                print("="*70)
                
                # Send to Telegram
                await self.telegram.send_message(
                    f"📊 *THỐNG KÊ GIỜ QUA*\n\n"
                    f"H4 scans: {self.stats['h4_scans']}\n"
                    f"H1 scans: {self.stats['h1_scans']}\n"
                    f"M15 scans: {self.stats['m15_scans']}\n"
                    f"Candidates: {len(self.candidate_symbols)}\n"
                    f"Watchlist: {len(self.hot_watchlist)}\n"
                    f"Tín hiệu: {self.stats['total_signals']}"
                )
                
                await asyncio.sleep(3600)  # Report every hour
                
            except Exception as e:
                print(f"❌ Lỗi stats reporter: {e}")
                await asyncio.sleep(3600)
    
    async def run(self):
        """
        Run all scanning loops concurrently.
        Each timeframe has its own independent loop.
        """
        # Validate config
        try:
            config.validate_config()
        except ValueError as e:
            print(f"❌ Lỗi cấu hình: {e}")
            print("💡 Vui lòng tạo file .env và điền thông tin Telegram")
            return
        
        # Initialize
        await self.initialize()
        
        if not self.all_symbols:
            print("❌ Không thể khởi động: Không có symbols")
            return
        
        print("\n🚀 KHỞI ĐỘNG 3 LUỒNG QUÉT SONG SONG")
        print("="*70)
        print("  🔵 H4 Loop: Mỗi 1 giờ - Trend Filter")
        print("  🟢 H1 Loop: Mỗi 15 phút - Value Zone")
        print("  🟡 M15 Loop: Mỗi 2 phút - Entry Signals")
        print("  📊 Stats: Báo cáo mỗi giờ")
        print("="*70 + "\n")
        
        # Run all loops concurrently
        await asyncio.gather(
            self.scan_h4_trend_filter(),
            self.scan_h1_value_zone(),
            self.scan_m15_entry_signals(),
            self.statistics_reporter(),
            return_exceptions=True
        )


async def run_single_scan():
    """Run a single complete scan for testing."""
    print("🧪 Chạy một chu kỳ quét hoàn chỉnh...\n")
    
    if config.MAX_SYMBOLS_TO_SCAN:
        print(f"ℹ️  Chế độ giới hạn: Top {config.MAX_SYMBOLS_TO_SCAN} symbols by {config.SYMBOL_SORT_METHOD}\n")
    
    scanner = MultiTimeframeScanner()
    await scanner.initialize()
    
    if not scanner.all_symbols:
        print("❌ Không thể lấy symbols")
        return
    
    # Run one cycle of each stage
    print("\n1️⃣ Quét H4...")
    async with MarketDataFetcher() as fetcher:
        h4_data = await fetcher.scan_market(
            scanner.all_symbols,
            config.TIMEFRAMES['trend']
        )
        scanner.h4_data_cache = h4_data
        
        for symbol, df in h4_data.items():
            df_ind = scanner.strategy.calculate_indicators(df)
            trend = scanner.strategy.is_trend_aligned(df_ind)
            if trend:
                scanner.candidate_symbols[symbol] = trend
    
    print(f"   ✅ {len(scanner.candidate_symbols)} candidates")
    
    if scanner.candidate_symbols:
        print("\n2️⃣ Quét H1...")
        async with MarketDataFetcher() as fetcher:
            h1_data = await fetcher.scan_market(
                list(scanner.candidate_symbols.keys()), 
                config.TIMEFRAMES['value']
            )
            scanner.h1_data_cache = h1_data
            
            for symbol, trend in scanner.candidate_symbols.items():
                if symbol in h1_data and symbol in scanner.h4_data_cache:
                    df_h1 = scanner.strategy.calculate_indicators(h1_data[symbol])
                    df_h4 = scanner.h4_data_cache[symbol]
                    in_zone, zone_desc, fib = scanner.strategy.is_in_value_zone(
                        df_h1, df_h4, trend
                    )
                    if in_zone:
                        scanner.hot_watchlist[symbol] = trend
        
        print(f"   ✅ {len(scanner.hot_watchlist)} in watchlist")
    
    if scanner.hot_watchlist:
        print("\n3️⃣ Quét M15...")
        signals = []
        async with MarketDataFetcher() as fetcher:
            m15_data = await fetcher.scan_market(
                list(scanner.hot_watchlist.keys()),
                config.TIMEFRAMES['signal']
            )
            
            for symbol in scanner.hot_watchlist.keys():
                if symbol in m15_data and symbol in scanner.h4_data_cache and symbol in scanner.h1_data_cache:
                    signal = scanner.strategy.analyze_symbol(
                        symbol,
                        scanner.h4_data_cache[symbol],
                        scanner.h1_data_cache[symbol],
                        m15_data[symbol]
                    )
                    if signal:
                        signals.append(signal)
                        await scanner.telegram.send_signal(signal)
        
        print(f"   ✅ {len(signals)} signals found")
    
    print("\n✅ Hoàn thành!")


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single scan for testing
        await run_single_scan()
    else:
        # Run continuously with 3 separate loops
        scanner = MultiTimeframeScanner()
        await scanner.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot đã dừng. Tạm biệt!")
