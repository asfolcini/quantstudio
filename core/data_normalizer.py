import pandas as pd

def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize OHLCV DataFrame to consistent lowercase column names.
    
    Args:
        df: DataFrame with potential mixed-case OHLCV columns
    
    Returns:
        DataFrame with standardized columns: open, high, low, close, volume
    """
    # Convert all column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    # Ensure required columns exist (rename if needed)
    column_mapping = {
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }
    
    # Rename columns if they exist with different names
    for standard_name, possible_names in column_mapping.items():
        # If the standard name already exists, skip
        if standard_name in df.columns:
            continue
        
        # Try common variants
        variants = [
            'open', 'high', 'low', 'close', 'volume',
            'Open', 'High', 'Low', 'Close', 'Volume'
        ]
        for variant in variants:
            if variant in df.columns:
                df.rename(columns={variant: standard_name}, inplace=True)
                break
    
    # Ensure all required columns are present
    required_cols = {'open', 'high', 'low', 'close', 'volume'}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns after normalization: {missing}")
    
    return df
