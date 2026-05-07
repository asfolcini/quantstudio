import pandas as pd
from typing import Dict, Any

def sanitize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean standardized data by removing duplicates, nulls, and invalid prices.
    
    Args:
        df: DataFrame with canonical schema: datetime, open, high, low, close, volume
    
    Returns:
        Cleaned DataFrame with valid data only
    """
    # Remove rows with null values
    df_clean = df.dropna()
    
    # Remove duplicates based on datetime
    df_clean = df_clean.drop_duplicates(subset=['datetime'], keep='first')
    
    # Remove invalid prices (<= 0)
    price_columns = ['open', 'high', 'low', 'close']
    df_clean = df_clean[(df_clean[price_columns] > 0).all(axis=1)]
    
    # Remove rows with negative or null volume
    df_clean = df_clean[df_clean['volume'] >= 0]
    
    # Ensure ascending sort by datetime
    df_clean = df_clean.sort_values('datetime').reset_index(drop=True)
    
    return df_clean
