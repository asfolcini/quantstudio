from typing import List, Dict, Any
import os
import json
import pandas as pd
from data.pipeline import get_historical_data
from data.metadata import load_metadata, save_metadata

def list_tickers() -> List[str]:
    """
    Discover all tickers by scanning /historical_data directory.
    
    Returns:
        List of ticker names
    """
    data_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
    if not os.path.exists(data_dir):
        return []
    
    tickers = [d for d in os.listdir(data_dir) 
               if os.path.isdir(os.path.join(data_dir, d))]
    return sorted(tickers)


def add_ticker(ticker: str) -> bool:
    """
    Add a new ticker by creating its data directory.
    
    Returns:
        True if created successfully, False if already exists
    """
    data_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
    ticker_path = os.path.join(data_dir, ticker)
    
    if os.path.exists(ticker_path):
        return False
    
    os.makedirs(ticker_path, exist_ok=True)
    return True


def remove_ticker(ticker: str) -> bool:
    """
    Remove a ticker by deleting its data directory.
    
    Returns:
        True if removed successfully, False if doesn't exist
    """
    data_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
    ticker_path = os.path.join(data_dir, ticker)
    
    if not os.path.exists(ticker_path):
        return False
    
    import shutil
    shutil.rmtree(ticker_path)
    return True


def get_provider_files(ticker: str) -> List[str]:
    """
    List all raw provider files for a ticker.
    
    Returns:
        List of file names (e.g., ['raw_yahoo.csv'])
    """
    data_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
    ticker_path = os.path.join(data_dir, ticker)
    
    if not os.path.exists(ticker_path):
        return []
    
    files = [f for f in os.listdir(ticker_path) if f.startswith("raw_")]
    return sorted(files)


def run_pipeline(ticker: str, provider: str = "yahoo", mode: str = "update") -> Dict[str, Any]:
    """
    Execute the data pipeline for a ticker.
    
    Returns:
        Summary dict with rows, date_range, gaps
    """
    # For now, just call the pipeline and return basic summary
    # Storage logic will be added later
    df = get_historical_data(ticker, provider, mode)
    
    if len(df) == 0:
        return {"rows": 0, "date_range": "", "gaps": []}
    
    date_range = f"{df['datetime'].min()} to {df['datetime'].max()}"
    
    # Simple gap detection: check for daily gaps
    df_sorted = df.sort_values('datetime')
    daily_diff = df_sorted['datetime'].diff().dt.days
    gaps = df_sorted[daily_diff > 1]['datetime'].tolist()
    
    return {
        "rows": len(df),
        "date_range": date_range,
        "gaps": [str(d) for d in gaps]
    }


def inspect_data(ticker: str) -> Dict[str, Any]:
    """
    Inspect data for a ticker.
    
    Returns:
        Dict with last_10_rows and metadata
    """
    data_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
    ticker_path = os.path.join(data_dir, ticker)
    
    if not os.path.exists(ticker_path):
        return {"last_10_rows": [], "metadata": {}}
    
    # Load data.csv
    data_file = os.path.join(ticker_path, "data.csv")
    last_10_rows = []
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df['datetime'] = pd.to_datetime(df['datetime'])
        last_10_rows = df.tail(10).to_dict('records')
    
    # Load metadata.json
    metadata_file = os.path.join(ticker_path, "metadata.json")
    metadata = load_metadata(ticker)
    
    return {
        "last_10_rows": last_10_rows,
        "metadata": metadata
    }


def update_all_data(mode: str = "update") -> Dict[str, Any]:
    """
    Update all data for all tickers in the system.
    
    Args:
        mode: "update" (delta sync) or "full" (full sync)
    
    Returns:
        Summary dict with ticker updates and statistics
    """
    from core.universe_logic import update_all_data as core_update_all_data
    
    # Get all tickers
    tickers = list_tickers()
    
    if not tickers:
        return {"processed": 0, "success": 0, "failed": 0, "tickers": []}
    
    results = {}
    success_count = 0
    failed_count = 0
    
    for ticker in tickers:
        try:
            # Run pipeline for this ticker
            result = run_pipeline(ticker, "yahoo", mode)
            results[ticker] = result
            if result["rows"] > 0:
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            results[ticker] = {"error": str(e)}
            failed_count += 1
    
    return {
        "processed": len(tickers),
        "success": success_count,
        "failed": failed_count,
        "tickers": results
    }


def get_ticker_summary() -> List[Dict[str, Any]]:
    """
    Get summary information for all tickers (name, exchange, first date, last date).
    
    Returns:
        List of dicts with ticker, name, exchange, first_date, last_date
    """
    tickers = list_tickers()
    summary = []
    
    for ticker in sorted(tickers):
        metadata = load_metadata(ticker)
        
        ticker_info = {
            "ticker": ticker,
            "name": metadata.get("name", ""),
            "exchange": metadata.get("exchange", ""),
            "first_date": metadata.get("first_date", ""),
            "last_date": metadata.get("last_date", "")
        }
        summary.append(ticker_info)
    
    return summary
