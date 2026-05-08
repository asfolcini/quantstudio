import pandas as pd
import os
from pathlib import Path
import json
import warnings

# Simple helper functions
def load_ticker_data(ticker):
    """Load OHLCV data for a ticker."""
    from pathlib import Path
    data_dir = Path(__file__).parent.parent / "historical_data"
    ticker_path = os.path.join(data_dir, ticker)
    
    if not os.path.exists(ticker_path):
        raise FileNotFoundError(f"No data found for {ticker}")
    
    # Load data.csv
    data_file = os.path.join(ticker_path, "data.csv")
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime').set_index('datetime')
        df['return'] = df['close'].pct_change()
        return df.reset_index()
    else:
        raise FileNotFoundError(f"Data file missing for {ticker}")


class EventScanner:
    """Scan price events and volatility outliers."""
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = load_ticker_data(ticker)
        if len(self.data) < 30:
            raise ValueError(f"Not enough data for {ticker} (need ≥30 days)")
    
    def scan_price_drops(self, threshold=-0.10, lookforward=3):
        """Identify days with significant price drops."""
        drops = self.data[self.data['return'] <= threshold]
        
        if drops.empty:
            return {"error": "No events found"}
        
        results = []
        for idx, row in drops.iterrows():
            day_plus_1 = self.data.loc[idx + 1, 'return'] if idx + 1 < len(self.data) - 1 else 0
            day_plus_2 = self.data.loc[idx + 2, 'return'] if idx + 2 < len(self.data) - 1 else 0
            day_plus_3 = self.data.loc[idx + 3, 'return'] if idx + 3 < len(self.data) - 1 else 0
            day_plus_4 = self.data.loc[idx + 4, 'return'] if idx + 4 < len(self.data) - 1 else 0
            day_plus_5 = self.data.loc[idx + 5, 'return'] if idx + 5 < len(self.data) - 1 else 0
            
            results.append({
                'date': row['datetime'].strftime('%Y-%m-%d'),
                'day+1': day_plus_1,
                'day+2': day_plus_2,
                'day+3': day_plus_3,
                'day+4': day_plus_4,
                'day+5': day_plus_5,
                'win': 1 if day_plus_1 > 0 else 0
            })
        
        # Calculate aggregated stats for each day
        aggregated_stats = {}
        for day in range(1, 6):
            day_key = f'day+{day}'
            day_returns = [r[day_key] for r in results]
            day_series = pd.Series(day_returns)
            aggregated_stats[f'{day_key}_mean'] = day_series.mean() * 100
            aggregated_stats[f'{day_key}_win_rate'] = (sum(1 for r in day_returns if r > 0) / len(day_returns)) * 100
        
        return {
            'events': len(results),
            'frequency': f"{len(results)}/{len(self.data)} days",
            'win_rate': f"{(sum([r['win'] for r in results]) / len(results) * 100):.1f}%",
            'day+1_mean': f"{(pd.Series([r['day+1'] for r in results]).mean()*100):.2f}%",
            'event_dates': results,
            **aggregated_stats}

    def scan_volatility_spikes(self, sigma=2, window=30, lookforward=3):
        """Identify days with volatility > sigma * rolling sigma."""
        self.data['volatility'] = self.data['return'].rolling(window=window, min_periods=10).std()
        spikes = self.data[abs(self.data['return']) > sigma * self.data['volatility']]
        
        if spikes.empty:
            return {"error": "No events found"}
        
        results = []
        for idx, row in spikes.iterrows():
            day_plus_1 = self.data.loc[idx + 1, 'return'] if idx + 1 < len(self.data) - 1 else 0
            day_plus_2 = self.data.loc[idx + 2, 'return'] if idx + 2 < len(self.data) - 1 else 0
            day_plus_3 = self.data.loc[idx + 3, 'return'] if idx + 3 < len(self.data) - 1 else 0
            day_plus_4 = self.data.loc[idx + 4, 'return'] if idx + 4 < len(self.data) - 1 else 0
            day_plus_5 = self.data.loc[idx + 5, 'return'] if idx + 5 < len(self.data) - 1 else 0
            
            results.append({
                'date': row['datetime'].strftime('%Y-%m-%d'),
                'day+1': day_plus_1,
                'day+2': day_plus_2,
                'day+3': day_plus_3,
                'day+4': day_plus_4,
                'day+5': day_plus_5,
                'win': 1 if day_plus_1 > 0 else 0
            })
        
        # Calculate aggregated stats for each day
        aggregated_stats = {}
        for day in range(1, 6):
            day_key = f'day+{day}'
            day_returns = [r[day_key] for r in results]
            # Filter out NaN values and handle edge cases
            valid_returns = [r for r in day_returns if not pd.isna(r)]
            if not valid_returns:
                aggregated_stats[f'{day_key}_mean'] = 0.0
                aggregated_stats[f'{day_key}_win_rate'] = 0.0
            else:
                day_series = pd.Series(valid_returns)
                aggregated_stats[f'{day_key}_mean'] = day_series.mean() * 100
                aggregated_stats[f'{day_key}_win_rate'] = (sum(1 for r in valid_returns if r > 0) / len(valid_returns)) * 100
        
        return {
            'events': len(results),
            'frequency': f"{len(results)}/{len(self.data)} days",
            'win_rate': f"{(sum([r['win'] for r in results]) / len(results) * 100):.1f}%",
            'day+1_mean': f"{(pd.Series([r['day+1'] for r in results]).mean()*100):.2f}%",
            'event_dates': results,
            **aggregated_stats}

    def scan_price_surges(self, threshold=0.05, lookforward=3):
        """Identify days with significant price surges (opposite of drops)."""
        surges = self.data[self.data['return'] >= threshold]
        
        if surges.empty:
            return {"error": "No events found"}
        
        results = []
        for idx, row in surges.iterrows():
            day_plus_1 = self.data.loc[idx + 1, 'return'] if idx + 1 < len(self.data) - 1 else 0
            day_plus_2 = self.data.loc[idx + 2, 'return'] if idx + 2 < len(self.data) - 1 else 0
            day_plus_3 = self.data.loc[idx + 3, 'return'] if idx + 3 < len(self.data) - 1 else 0
            day_plus_4 = self.data.loc[idx + 4, 'return'] if idx + 4 < len(self.data) - 1 else 0
            day_plus_5 = self.data.loc[idx + 5, 'return'] if idx + 5 < len(self.data) - 1 else 0
            
            results.append({
                'date': row['datetime'].strftime('%Y-%m-%d'),
                'day+1': day_plus_1,
                'day+2': day_plus_2,
                'day+3': day_plus_3,
                'day+4': day_plus_4,
                'day+5': day_plus_5,
                'win': 1 if day_plus_1 > 0 else 0
            })
        
        # Calculate aggregated stats for each day
        aggregated_stats = {}
        for day in range(1, 6):
            day_key = f'day+{day}'
            day_returns = [r[day_key] for r in results]
            valid_returns = [r for r in day_returns if not pd.isna(r)]
            if not valid_returns:
                aggregated_stats[f'{day_key}_mean'] = 0.0
                aggregated_stats[f'{day_key}_win_rate'] = 0.0
            else:
                day_series = pd.Series(valid_returns)
                aggregated_stats[f'{day_key}_mean'] = day_series.mean() * 100
                aggregated_stats[f'{day_key}_win_rate'] = (sum(1 for r in valid_returns if r > 0) / len(valid_returns)) * 100
        
        return {
            'events': len(results),
            'frequency': f"{len(results)}/{len(self.data)} days",
            'win_rate': f"{(sum([r['win'] for r in results]) / len(results) * 100):.1f}%",
            'day+1_mean': f"{(pd.Series([r['day+1'] for r in results]).mean()*100):.2f}%",
            'event_dates': results,
            **aggregated_stats
        }

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
