import pandas as pd
from typing import Dict, Any
from data.providers import YahooProvider
from data.standardizer import standardize_yahoo_data
from data.sanitizer import sanitize_data
from data.validation import validate_schema
from data.metadata import load_metadata, save_metadata
import os
import yfinance as yf
from core.config_loader import get_config

def get_historical_data(ticker: str, provider: str = "yahoo", mode: str = "update") -> pd.DataFrame:
    """
    Fetch, standardize, and sanitize historical data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
        provider: Data provider (default: "yahoo")
        mode: "update" (delta sync - append missing data) or "full" (full sync - reload all data)
    
    Returns:
        Cleaned DataFrame with canonical schema: datetime, open, high, low, close, volume
    """
    # Use configured provider
    config = get_config()
    if provider.lower() != config["data_provider"].lower():
        raise NotImplementedError(f"Provider '{provider}' does not match configured provider '{config['data_provider']}'")
    
    try:
        # Step 1: Download raw data
        if config["data_provider"] != "YAHOO":
            raise RuntimeError(f"Unsupported data provider: {config['data_provider']}")
         
        provider_instance = YahooProvider()
        raw_data = provider_instance.download(ticker)
         
        # Step 2: Standardize
        standardized_data = standardize_yahoo_data(raw_data)
         
        # Step 3: Sanitize
        cleaned_data = sanitize_data(standardized_data)
         
        # Validate final output
        if not validate_schema(cleaned_data):
            raise ValueError("Final data does not conform to canonical schema")
         
        # Ensure volume column is numeric and handle any issues
        if 'volume' in cleaned_data.columns:
            # Convert volume to numeric, coerce errors to NaN
            cleaned_data['volume'] = pd.to_numeric(cleaned_data['volume'], errors='coerce')
            # Fill NaN values with 0 (common for some financial instruments)
            cleaned_data['volume'] = cleaned_data['volume'].fillna(0)
        else:
            # If volume column is missing, add it with zeros
            cleaned_data['volume'] = 0
             
        # Step 4: Save to storage
        data_dir = f"/Users/alberto.sfolcini/Development/quantstudio/historical_data/{ticker}"
        os.makedirs(data_dir, exist_ok=True)
         
        # Handle different sync modes
        existing_data = None
        if mode == "full":
            # Full sync: delete existing files first
            import shutil
            for file in ["data.csv", "raw_yahoo.csv", "metadata.json"]:
                file_path = os.path.join(data_dir, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
        elif mode == "update":
            # Delta sync: check if existing data file exists
            existing_data_path = os.path.join(data_dir, "data.csv")
            if os.path.exists(existing_data_path):
                existing_data = pd.read_csv(existing_data_path)
                existing_data['datetime'] = pd.to_datetime(existing_data['datetime'])
                
                # Clean new data to avoid duplicate columns
                cleaned_data['datetime'] = pd.to_datetime(cleaned_data['datetime'])
                
                # Merge: keep existing data, add only new data points
                merged_data = pd.concat([existing_data, cleaned_data])
                merged_data = merged_data.drop_duplicates(subset=['datetime'], keep='last')
                merged_data = merged_data.sort_values('datetime')
                cleaned_data = merged_data
         
        # Save standardized data
        cleaned_data.to_csv(f"{data_dir}/data.csv", index=False)
         
        # Save raw data
        raw_data.to_csv(f"{data_dir}/raw_yahoo.csv")
         
        # Save metadata
        metadata = provider_instance.get_metadata(ticker)
        metadata.update({
            "ticker": ticker,
            "provider": provider,
            "data_points": len(cleaned_data),
            "first_date": str(cleaned_data['datetime'].min()) if len(cleaned_data) > 0 else "",
            "last_date": str(cleaned_data['datetime'].max()) if len(cleaned_data) > 0 else "",
            "last_update": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_metadata(ticker, provider, metadata)
         
        return cleaned_data
        
    except Exception as e:
        # Log error and skip this ticker
        error_msg = str(e)
        if "Not Found" in error_msg or "Quote not found" in error_msg or "delisted" in error_msg.lower():
            console.print(f"[yellow][WARNING] {ticker}: possibly delisted or invalid symbol[/yellow]")
        else:
            console.print(f"[yellow][WARNING] {ticker}: error - {error_msg}[/yellow]")
        return pd.DataFrame()  # Return empty DF to indicate failure
