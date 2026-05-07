import pandas as pd
from typing import Dict, Any

def standardize_yahoo_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Yahoo Finance raw data to canonical schema.
    
    Args:
        df: Raw Yahoo Finance DataFrame with columns: 
            ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            and DatetimeIndex
    
    Returns:
        DataFrame with canonical schema: datetime, open, high, low, close, volume
    """
    # Select and rename required columns
    df_standard = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df_standard.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Ensure datetime index is timezone-naive
    df_standard.index = df_standard.index.tz_localize(None)
    
    # Reset index to make datetime a column
    df_standard = df_standard.reset_index()
    df_standard.rename(columns={'Date': 'datetime'}, inplace=True)
    
    # Ensure correct data types
    df_standard['datetime'] = pd.to_datetime(df_standard['datetime'])
    df_standard = df_standard.astype({
        'open': 'float64',
        'high': 'float64',
        'low': 'float64',
        'close': 'float64',
        'volume': 'float64'
    })
    
    # Sort by datetime ascending
    df_standard = df_standard.sort_values('datetime').reset_index(drop=True)
    
    return df_standard
