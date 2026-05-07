import yfinance as yf
import pandas as pd
from typing import Dict, Any
from .base import DataProvider
from core.config_loader import get_config

class YahooProvider(DataProvider):
    """
    Data provider for Yahoo Finance using yfinance.
    """
    
    def download(self, ticker: str) -> pd.DataFrame:
        """
        Download raw Yahoo Finance data.
        
        Returns:
            DataFrame with columns: ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            and DatetimeIndex
        """
        # Use configured data provider (currently only YAHOO supported)
        config = get_config()
        if config["data_provider"] != "YAHOO":
            raise RuntimeError(f"Unsupported data provider: {config['data_provider']}")
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")
        return hist
    
    def get_metadata(self, ticker: str) -> Dict[str, Any]:
        """
        Get metadata for the ticker from Yahoo Finance.
        
        Returns:
            Dictionary with keys: name, exchange, currency
        """
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "name": info.get("longName", ""),
            "exchange": info.get("exchange", ""),
            "currency": info.get("currency", "")
        }
