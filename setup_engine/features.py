"""Feature engineering module."""

import pandas as pd
import numpy as np


def calculate_returns(series: pd.Series, periods: list = [1, 5, 20]):
    """Calculate returns using only past data."""
    returns = {}
    for period in periods:
        returns[f'ret_{period}d'] = series.pct_change(period)
    return returns


def calculate_ma(series: pd.Series, window: int):
    """Calculate moving average using only past data."""
    return series.shift(1).rolling(window).mean()


def calculate_rolling_volatility(series: pd.Series, window: int):
    """Calculate rolling volatility using only past data."""
    return series.shift(1).rolling(window).std()


def calculate_rsi(series: pd.Series, window: int = 14):
    """Calculate RSI using only past data."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_volume_z_score(volume: pd.Series, window: int = 30) -> pd.Series:
    """Calculate rolling z-score of volume."""
    mean_volume = volume.shift(1).rolling(window).mean()
    std_volume = volume.shift(1).rolling(window).std()
    return (volume - mean_volume) / std_volume


def calculate_feature_set(df: pd.DataFrame, min_rows: int = 50):
    """Calculate full feature set with data preservation."""
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['volume']
    
    features = pd.DataFrame(index=df.index)
    
    # Returns
    returns = calculate_returns(close, [1, 5, 20])
    features = pd.concat([features, pd.DataFrame(returns)], axis=1)
    
    # MAs
    features['ma_20'] = calculate_ma(close, 20)
    features['ma_50'] = calculate_ma(close, 50)
    if len(df) >= 200:
        features['ma_200'] = calculate_ma(close, 200)
    
    # Volatility
    features['vol_10'] = calculate_rolling_volatility(close, 10)
    features['vol_20'] = calculate_rolling_volatility(close, 20)
    
    # RSI
    features['rsi'] = calculate_rsi(close)
    
    # Volume
    features['vol_z'] = calculate_volume_z_score(volume)
    
    # Preserve as much data as possible for testing
    # Drop only rows with ALL NaN values, not just any NaN
    result = features.dropna(how='all')
    
    # Ensure minimum usable rows for setup engine
    if len(result) < min_rows and len(df) >= 30:  # Minimum for basic features
        # If we have too few rows with all features, try with just the most essential ones
        fallback = features[['ret_1d', 'ret_5d', 'rsi']].dropna()
        if len(fallback) > len(result):
            return fallback
    
    return result
