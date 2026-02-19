# data/ingestion.py
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
from core.config import config
from core.logger import logger

class BinanceDataFetcher:
    """Fetch cryptocurrency data from Binance (offline mode)."""
    
    def __init__(self, exchange_id: str = 'binance'):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.data_dir = config.DATA_DIR
        logger.info(f"BinanceDataFetcher initialized with exchange: {exchange_id}")
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', 
                    days_back: int = 365) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            days_back: Number of days of historical data
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Calculate since timestamp
            since = self.exchange.parse8601(
                (datetime.now() - timedelta(days=days_back)).isoformat()
            )
            
            logger.info(f"Fetching {timeframe} data for {symbol} ({days_back} days)...")
            
            # Fetch all data
            all_candles = []
            while since < self.exchange.milliseconds():
                candles = self.exchange.fetch_ohlcv(
                    symbol, timeframe, since=since, limit=1000
                )
                
                if not candles:
                    break
                
                all_candles.extend(candles)
                since = candles[-1][0] + 1
                
                logger.debug(f"Fetched {len(candles)} candles, total: {len(all_candles)}")
            
            # Convert to DataFrame
            df = pd.DataFrame(
                all_candles,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Fetched {len(df)} candles for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
    def fetch_multiple_symbols(self, symbols: List[str], 
                              timeframe: str = '1h',
                              days_back: int = 365) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple symbols.
        
        Args:
            symbols: List of trading pairs
            timeframe: Candle timeframe
            days_back: Number of days of historical data
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data = {}
        for symbol in symbols:
            try:
                df = self.fetch_ohlcv(symbol, timeframe, days_back)
                data[symbol] = df
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
        
        return data
    
    def save_to_csv(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save DataFrame to CSV file."""
        filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
        filepath = self.data_dir / filename
        df.to_csv(filepath)
        logger.info(f"Saved data to {filepath}")
    
    def load_from_csv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Load DataFrame from CSV file."""
        filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
        filepath = self.data_dir / filename
        
        if filepath.exists():
            df = pd.read_csv(filepath, index_col='timestamp', parse_dates=True)
            logger.info(f"Loaded data from {filepath}")
            return df
        else:
            logger.warning(f"File not found: {filepath}")
            return None
    
    def get_or_fetch(self, symbol: str, timeframe: str = '1h',
                     days_back: int = 365, force_refresh: bool = False) -> pd.DataFrame:
        """
        Get data from cache or fetch if not available.
        
        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            days_back: Number of days of historical data
            force_refresh: If True, fetch fresh data regardless of cache
        
        Returns:
            DataFrame with OHLCV data
        """
        if not force_refresh:
            cached_data = self.load_from_csv(symbol, timeframe)
            if cached_data is not None:
                logger.info(f"Using cached data for {symbol}")
                return cached_data
        
        # Fetch fresh data
        df = self.fetch_ohlcv(symbol, timeframe, days_back)
        self.save_to_csv(df, symbol, timeframe)
        return df

# Convenience function
def fetch_binance_data(symbols: List[str] = None, 
                       timeframe: str = '1h',
                       days_back: int = 365) -> Dict[str, pd.DataFrame]:
    """Fetch data for default or specified symbols."""
    if symbols is None:
        symbols = config.SYMBOLS
    
    fetcher = BinanceDataFetcher()
    return fetcher.fetch_multiple_symbols(symbols, timeframe, days_back)
