from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd

class DataProvider(ABC):
    """
    Abstract base class for data providers.
    
    All providers must implement download() and get_metadata() methods.
    """
    
    @abstractmethod
    def download(self, ticker: str) -> pd.DataFrame:
        """
        Download raw data for the given ticker.
        
        Returns:
            DataFrame in provider-specific format (raw)
        """
        pass
    
    @abstractmethod
    def get_metadata(self, ticker: str) -> Dict[str, Any]:
        """
        Get metadata for the given ticker.
        
        Returns:
            Dictionary with keys: name, exchange, currency
        """
        pass
