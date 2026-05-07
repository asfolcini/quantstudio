import json
import os
from typing import Dict, List, Any
from data.metadata import load_metadata

UNIVERSES_FILE = "/Users/alberto.sfolcini/Development/quantstudio/config/universes.json"

def load_universes() -> Dict[str, List[str]]:
    """
    Load universes from JSON file.
    
    Returns:
        Dictionary with universe names as keys and lists of tickers as values
    """
    if not os.path.exists(UNIVERSES_FILE):
        return {}
    
    try:
        with open(UNIVERSES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_universes(universes: Dict[str, List[str]]) -> None:
    """
    Save universes to JSON file.
    
    Args:
        universes: Dictionary with universe names and ticker lists
    """
    os.makedirs(os.path.dirname(UNIVERSES_FILE), exist_ok=True)
    
    with open(UNIVERSES_FILE, 'w') as f:
        json.dump(universes, f, indent=2)


def add_universe(name: str, tickers: List[str]) -> bool:
    """
    Add a new universe.
    
    Args:
        name: Universe name
        tickers: List of ticker symbols
    
    Returns:
        True if added, False if name already exists
    """
    universes = load_universes()
    
    if name in universes:
        return False
    
    universes[name] = tickers
    save_universes(universes)
    return True


def delete_universe(name: str) -> bool:
    """
    Delete a universe.
    
    Args:
        name: Universe name to delete
    
    Returns:
        True if deleted, False if not found
    """
    universes = load_universes()
    
    if name not in universes:
        return False
    
    del universes[name]
    save_universes(universes)
    return True


def add_ticker(universe: str, ticker: str) -> bool:
    """
    Add a ticker to a universe.
    
    Args:
        universe: Universe name
        ticker: Ticker symbol to add
    
    Returns:
        True if added, False if universe doesn't exist or ticker already exists
    """
    universes = load_universes()
    
    if universe not in universes:
        return False
    
    if ticker in universes[universe]:
        return False
    
    universes[universe].append(ticker)
    save_universes(universes)
    return True


def remove_ticker(universe: str, ticker: str) -> bool:
    """
    Remove a ticker from a universe.
    
    Args:
        universe: Universe name
        ticker: Ticker symbol to remove
    
    Returns:
        True if removed, False if universe doesn't exist or ticker not found
    """
    universes = load_universes()
    
    if universe not in universes:
        return False
    
    if ticker not in universes[universe]:
        return False
    
    universes[universe].remove(ticker)
    save_universes(universes)
    return True


def get_ticker_dates(ticker: str) -> dict:
    """
    Get start and end dates from ticker's metadata.
    
    Args:
        ticker: Ticker symbol
    
    Returns:
        Dictionary with 'first_date' and 'last_date', or empty if not available
    """
    metadata = load_metadata(ticker)
    return {
        "first_date": metadata.get("first_date", "N/A"),
        "last_date": metadata.get("last_date", "N/A")
    }


def get_universe_tickers_with_dates(universe_name: str) -> List[dict]:
    """
    Get all tickers in a universe with their date ranges and exchange.
    
    Args:
        universe_name: Name of the universe
    
    Returns:
        List of dicts: [{"ticker": "AAPL", "exchange": "...", "first_date": "...", "last_date": "..."}]
    """
    universes = load_universes()
    if universe_name not in universes:
        return []
    
    tickers = universes[universe_name]
    result = []
    for ticker in sorted(tickers):  # Sort alphabetically
        dates = get_ticker_dates(ticker)
        metadata = load_metadata(ticker)
        result.append({
            "ticker": ticker,
            "exchange": metadata.get("exchange", "N/A"),
            "first_date": dates["first_date"],
            "last_date": dates["last_date"]
        })
    return result
