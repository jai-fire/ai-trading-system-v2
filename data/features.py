# data/features.py
import pandas as pd
import numpy as np
from typing import Dict
from core.logger import logger

class FeatureEngineer:
    """Generate technical indicators and features for ML models."""
    
    def __init__(self):
        logger.info("FeatureEngineer initialized")
    
    def add_sma(self, df: pd.DataFrame, periods: list = [7, 14, 30]) -> pd.DataFrame:
        """Add Simple Moving Averages."""
        for period in periods:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    def add_ema(self, df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """Add Exponential Moving Averages."""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df
    
    def add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Relative Strength Index."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD (Moving Average Convergence Divergence)."""
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        return df
    
    def add_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Add Bollinger Bands."""
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std * 2)
        df['bb_lower'] = df['bb_middle'] - (std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        return df
    
    def add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features."""
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        return df
    
    def add_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price change features."""
        df['price_change'] = df['close'].pct_change()
        df['price_change_1h'] = df['close'].pct_change(periods=1)
        df['price_change_4h'] = df['close'].pct_change(periods=4)
        df['price_change_1d'] = df['close'].pct_change(periods=24)
        return df
    
    def add_momentum(self, df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """Add momentum indicators."""
        df['momentum'] = df['close'] - df['close'].shift(period)
        df['roc'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
        return df
    
    def add_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Add volatility features."""
        df['volatility'] = df['close'].rolling(window=period).std()
        df['atr'] = self._calculate_atr(df, period)
        return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=period).mean()
    
    def add_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with all features added
        """
        logger.info(f"Adding features to dataframe with {len(df)} rows")
        
        df = df.copy()
        
        # Add all indicators
        df = self.add_sma(df)
        df = self.add_ema(df)
        df = self.add_rsi(df)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)
        df = self.add_volume_features(df)
        df = self.add_price_changes(df)
        df = self.add_momentum(df)
        df = self.add_volatility(df)
        
        # Drop NaN values
        initial_len = len(df)
        df = df.dropna()
        final_len = len(df)
        
        logger.info(f"Features added. Dropped {initial_len - final_len} rows with NaN values")
        logger.info(f"Final dataframe shape: {df.shape}")
        
        return df
    
    def prepare_for_ml(self, df: pd.DataFrame, target_column: str = 'close',
                       future_periods: int = 1) -> tuple:
        """
        Prepare features and target for machine learning.
        
        Args:
            df: DataFrame with features
            target_column: Column to predict
            future_periods: How many periods ahead to predict
        
        Returns:
            Tuple of (features_df, target_series)
        """
        # Create target (future price change)
        df['target'] = df[target_column].pct_change(periods=future_periods).shift(-future_periods)
        
        # Remove target from features
        feature_columns = [col for col in df.columns if col not in 
                          ['target', 'open', 'high', 'low', 'close', 'volume']]
        
        X = df[feature_columns].copy()
        y = df['target'].copy()
        
        # Remove rows with NaN target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        logger.info(f"ML data prepared: X shape={X.shape}, y shape={y.shape}")
        
        return X, y

# Convenience function
def engineer_features(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Engineer features for multiple symbols.
    
    Args:
        data: Dictionary mapping symbols to DataFrames
    
    Returns:
        Dictionary mapping symbols to feature-engineered DataFrames
    """
    engineer = FeatureEngineer()
    engineered_data = {}
    
    for symbol, df in data.items():
        logger.info(f"Engineering features for {symbol}")
        engineered_data[symbol] = engineer.add_all_features(df)
    
    return engineered_data
