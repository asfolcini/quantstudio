import pandas as pd
from pathlib import Path
import json
import warnings

# Simple helper functions
def load_ticker_data(ticker):
    """Load OHLCV data for a ticker."""
    data_path = Path(f"historical_data/{ticker}/data.csv")
    try:
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime').set_index('datetime')
        df['return'] = df['close'].pct_change()
        return df.reset_index()
    except FileNotFoundError:
        raise FileNotFoundError(f"No data found for {ticker}")


class EventScanner:
    """Scan price events and volatility outliers."""
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = load_ticker_data(ticker)
    
    def scan_price_drops(self, threshold=-0.10, lookforward=3):
        """Identify days with significant price drops."""
        drops = self.data[self.data['return'] <= threshold]
        
        if drops.empty:
            return {"error": "No events found"}
        
        results = []
        for idx, row in drops.iterrows():
            day_plus_1 = self.data.loc[idx + 1, 'return'] if idx + 1 < len(self.data) - 1 else 0
            results.append({
                'date': row['datetime'].strftime('%Y-%m-%d'),
                'day+1': day_plus_1,
                'win': 1 if day_plus_1 > 0 else 0
            })
        
        return {
            'events': len(results),
            'frequency': f"{len(results)}/{len(self.data)} days",
            'win_rate': f"{(sum([r['win'] for r in results]) / len(results) * 100):.1f}%",
            'day+1_median': f"{(pd.Series([r['day+1'] for r in results]).median()*100):.2f}%"}

    def scan_volatility_spikes(self, sigma=2, window=30, lookforward=3):
        """Identify days with volatility > sigma * rolling sigma."""
        self.data['volatility'] = self.data['return'].rolling(window=window, min_periods=10).std()
        spikes = self.data[abs(self.data['return']) > sigma * self.data['volatility']]
        
        if spikes.empty:
            return {"error": "No events found"}
        
        results = []
        for idx, row in spikes.iterrows():
            day_plus_1 = self.data.loc[idx + 1, 'return'] if idx + 1 < len(self.data) - 1 else 0
            results.append({
                'date': row['datetime'].strftime('%Y-%m-%d'),
                'day+1': day_plus_1,
                'win': 1 if day_plus_1 > 0 else 0
            })
        
        return {
            'events': len(results),
            'frequency': f"{len(results)}/{len(self.data)} days",
            'win_rate': f"{(sum([r['win'] for r in results]) / len(results) * 100):.1f}%",
            'day+1_median': f"{(pd.Series([r['day+1'] for r in results]).median()*100):.2f}%"}

    def run_on_universe(self, universe_file="config/universes.json"):
        """Scan all tickers in a universe."""
        with open(universe_file) as f:
            universes = json.load(f)
        
        records = []
        for universe_name, tickers in universes.items():
            for ticker in tickers:
                try:
                    results = self.scan_price_drops(threshold=-0.10)
                    if 'error' not in results:
                        results['ticker'] = ticker
                        results['universe'] = universe_name
                        records.append(results)
                except:
                    pass
        return pd.DataFrame(records)


# Example usage
if __name__ == "__main__":
    scanner = EventScanner("AAPL.MI")
    print(scanner.scan_price_drops())
