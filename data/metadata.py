import json
from typing import Dict, Any

def save_metadata(ticker: str, provider: str, metadata: Dict[str, Any]) -> None:
    """
    Save metadata to JSON file.
    
    Args:
        ticker: Stock ticker symbol
        provider: Data provider name
        metadata: Dictionary containing metadata fields
    """
    # Create directory if it doesn't exist
    import os
    os.makedirs(f"/Users/alberto.sfolcini/Development/quantstudio/historical_data/{ticker}", exist_ok=True)
    
    # Write metadata
    with open(f"/Users/alberto.sfolcini/Development/quantstudio/historical_data/{ticker}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)


def load_metadata(ticker: str) -> Dict[str, Any]:
    """
    Load metadata from JSON file.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary containing metadata fields
    """
    try:
        with open(f"/Users/alberto.sfolcini/Development/quantstudio/historical_data/{ticker}/metadata.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
