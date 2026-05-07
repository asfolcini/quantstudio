from typing import Dict, List
import os
import pandas as pd
from core.universe_manager import load_universes, add_universe, delete_universe, add_ticker, remove_ticker, get_universe_tickers_with_dates
from data.pipeline import get_historical_data

def list_universes() -> Dict[str, List[str]]:
    """
    Load and return all universes.
    
    Returns:
        Dictionary of universes with ticker lists
    """
    return load_universes()


def create_universe(name: str, tickers_str: str) -> bool:
    """
    Create a new universe from comma-separated tickers.
    
    Args:
        name: Universe name
        tickers_str: Comma-separated ticker symbols
    
    Returns:
        True if created successfully
    """
    tickers = [t.strip().upper() for t in tickers_str.split(',') if t.strip()]
    return add_universe(name, tickers)


def update_all_data(mode: str = "update") -> None:
    """
    Update data for all unique tickers across all universes.
    
    Args:
        mode: "update" (delta) or "full" (reload)
    """
    universes = load_universes()
    all_tickers = set()
    
    for tickers in universes.values():
        all_tickers.update(tickers)
    
    for ticker in sorted(all_tickers):
        config = get_config()
        get_historical_data(ticker, provider=config["data_provider"], mode=mode)


def update_universe(universe_name: str, mode: str = "update") -> None:
    """
    Update data for all tickers in a specific universe.
    
    Args:
        universe_name: Name of the universe to update
        mode: "update" (delta) or "full" (reload)
    """
    universes = load_universes()
    
    if universe_name not in universes:
        return
    
    for ticker in universes[universe_name]:
        config = get_config()
        get_historical_data(ticker, provider=config["data_provider"], mode=mode)
