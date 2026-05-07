import pandas as pd
from typing import Dict, Any

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame follows canonical schema.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if schema is valid, False otherwise
    """
    required_columns = {'datetime', 'open', 'high', 'low', 'close', 'volume'}
    
    # Check all required columns exist
    if not required_columns.issubset(df.columns):
        return False
    
    # Check datetime is datetime type
    if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        return False
    
    # Check numeric columns are float64
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_columns:
        if not pd.api.types.is_float_dtype(df[col]):
            return False
    
    # Check no null values
    if df.isnull().any().any():
        return False
    
    # Check data is sorted by datetime
    if not df['datetime'].is_monotonic_increasing:
        return False
    
    return True
