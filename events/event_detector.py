import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any

def detect_events(ticker: str, data_dir: str = "/Users/alberto.sfolcini/Development/quantstudio/historical_data") -> List[Dict[str, Any]]:
    """
    Detect three types of events for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
        data_dir: Base directory for historical data
    
    Returns:
        List of detected events with standardized format
    """
    data_path = os.path.join(data_dir, ticker, "data.csv")
    if not os.path.exists(data_path):
        return []
    
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    df = df.sort_index()
    
    # Normalize column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    # Ensure required columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        return []
    
    # Compute ATR(14)
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )
    df['atr_14'] = df['tr'].rolling(window=14).mean()
    
    # Compute ATR(50) rolling mean
    df['atr_50_mean'] = df['atr_14'].rolling(window=50).mean()
    
    # Compute SMA(50)
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Compute Volume mean (20 days)
    df['volume_mean_20'] = df['volume'].rolling(window=20).mean()
    
    # Compute 20-day high (excluding current day)
    df['high_20d'] = df['close'].shift(1).rolling(window=20).max()
    
    events = []
    
    # Event 1: Breakout (20-day high)
    df['breakout_20d'] = (df['close'] > df['high_20d']) & (df['close'].shift(1) <= df['high_20d'].shift(1))
    breakout_events = df[df['breakout_20d']]
    for date, row in breakout_events.iterrows():
        if pd.isna(row['high_20d']) or pd.isna(row['close']):
            continue
        
        strength = (row['close'] - row['high_20d']) / row['high_20d']
        volatility = "high" if row['atr_14'] > row['atr_50_mean'] else "low"
        trend = "bull" if row['close'] > row['sma_50'] else "bear"
        
        events.append({
            "ticker": ticker,
            "event_type": "breakout",
            "event_subtype": "breakout_20d_high",
            "date": date.strftime("%Y-%m-%d"),
            "strength": float(strength),
            "context": {
                "volatility": volatility,
                "trend": trend
            }
        })
    
    # Event 2: Volatility Compression
    df['volatility_compression'] = (df['atr_14'] < 0.7 * df['atr_50_mean']) & (df['atr_14'].shift(1) >= 0.7 * df['atr_50_mean'].shift(1))
    compression_events = df[df['volatility_compression']]
    for date, row in compression_events.iterrows():
        if pd.isna(row['atr_14']) or pd.isna(row['atr_50_mean']) or row['atr_50_mean'] == 0:
            continue
        
        strength = float(row['atr_14'] / row['atr_50_mean'])
        volatility = "high" if row['atr_14'] > row['atr_50_mean'] else "low"
        trend = "bull" if row['close'] > row['sma_50'] else "bear"
        
        events.append({
            "ticker": ticker,
            "event_type": "volatility",
            "event_subtype": "volatility_compression",
            "date": date.strftime("%Y-%m-%d"),
            "strength": strength,
            "context": {
                "volatility": volatility,
                "trend": trend
            }
        })
    
    # Event 3: Volume Spike
    df['volume_spike'] = (df['volume'] > 2.0 * df['volume_mean_20']) & (df['volume'].shift(1) <= 2.0 * df['volume_mean_20'].shift(1))
    volume_events = df[df['volume_spike']]
    for date, row in volume_events.iterrows():
        if pd.isna(row['volume']) or pd.isna(row['volume_mean_20']) or row['volume_mean_20'] == 0:
            continue
        
        strength = float(row['volume'] / row['volume_mean_20'])
        volatility = "high" if row['atr_14'] > row['atr_50_mean'] else "low"
        trend = "bull" if row['close'] > row['sma_50'] else "bear"
        
        events.append({
            "ticker": ticker,
            "event_type": "volume",
            "event_subtype": "volume_spike",
            "date": date.strftime("%Y-%m-%d"),
            "strength": strength,
            "context": {
                "volatility": volatility,
                "trend": trend
            }
        })
    
    # Sort by date
    events.sort(key=lambda x: x["date"])
    
    # Debug mode: Enable detailed logging for round number events
    DEBUG_ROUND_NUMBERS = True  # Set to True for debugging, False for production
    
    # Event 4: Round Number Reaction
    # Detect price interactions with psychological round numbers
    # For low-priced stocks, use relative rounding (nearest 1%, 5% of price)
    # For higher-priced stocks, use absolute round numbers (100, 500, 1000, etc.)
    
    # For each day, check if price is near a round level
    for i, (date, row) in enumerate(df.iterrows()):
        if pd.isna(row['close']):
            continue
        
        close_price = row['close']
        
        # Find the nearest round level based on price range
        nearest_round = None
        min_distance_pct = float('inf')
        reaction_type = "round_number_support_touch"
        
        # For low-priced stocks (< $10), use relative rounding
        if close_price < 10:
            # Round to nearest 0.1, 0.5, 1.0, 2.0, 5.0
            relative_levels = [0.1, 0.5, 1.0, 2.0, 5.0]
            for level in relative_levels:
                # Round to nearest multiple of level
                rounded_price = round(close_price / level) * level
                distance_pct = abs(close_price - rounded_price) / close_price
                
                if distance_pct < min_distance_pct:
                    min_distance_pct = distance_pct
                    nearest_round = rounded_price
                    # Determine reaction type based on the relative level
                    if level == 0.1:
                        reaction_type = "round_number_support_touch"
                    elif level == 0.5:
                        reaction_type = "round_number_support_touch"
                    elif level == 1.0:
                        reaction_type = "round_number_support_touch"
                    elif level == 2.0:
                        reaction_type = "round_number_support_touch"
                    elif level == 5.0:
                        reaction_type = "round_number_support_touch"
        
        # For higher-priced stocks (>= $10), use absolute round numbers
        else:
            absolute_levels = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
            for level in absolute_levels:
                distance_pct = abs(close_price - level) / level
                
                if distance_pct < min_distance_pct:
                    min_distance_pct = distance_pct
                    nearest_round = level
                    # Determine reaction type based on the absolute level
                    if level == 10:
                        reaction_type = "round_number_support_touch"
                    elif level == 20:
                        reaction_type = "round_number_support_touch"
                    elif level == 50:
                        reaction_type = "round_number_support_touch"
                    elif level == 100:
                        reaction_type = "round_number_support_touch"
                    elif level == 200:
                        reaction_type = "round_number_support_touch"
                    elif level == 500:
                        reaction_type = "round_number_support_touch"
                    elif level == 1000:
                        reaction_type = "round_number_support_touch"
                    elif level == 2000:
                        reaction_type = "round_number_support_touch"
                    elif level == 5000:
                        reaction_type = "round_number_support_touch"
                    elif level == 10000:
                        reaction_type = "round_number_support_touch"
        
        # If close enough to a round level (within 5% for low-priced stocks, 1% for high-priced)
        threshold = 0.05 if close_price < 10 else 0.01
        if min_distance_pct <= threshold:
            # Check if this is a breakout (price crossing up through round level)
            if i > 0 and df.iloc[i-1]['close'] < nearest_round and close_price >= nearest_round:
                reaction_type = "round_number_breakout"
            
            # Check if this is a rejection (price bouncing back from round level)
            if i > 0 and df.iloc[i-1]['close'] > nearest_round and close_price <= nearest_round:
                reaction_type = "round_number_rejection"
            
            # Calculate strength based on proximity and volatility
            # Closer distance = higher strength
            strength = 1.0 - min_distance_pct  # Normalize to 0-1 range
            
            # Adjust strength based on volatility (higher volatility = more significant reaction)
            if row['atr_14'] > row['atr_50_mean']:
                strength *= 1.2  # Boost strength in high volatility
            
            volatility = "high" if row['atr_14'] > row['atr_50_mean'] else "low"
            trend = "bull" if close_price > row['sma_50'] else "bear"
            
            # Debug output - only if DEBUG_ROUND_NUMBERS is True
            if DEBUG_ROUND_NUMBERS:
                print(f"DEBUG: {ticker} - {date.strftime('%Y-%m-%d')}: "
                      f"close={close_price:.4f}, nearest_round={nearest_round}, "
                      f"distance_pct={min_distance_pct:.6f}, reaction_type={reaction_type}, "
                      f"volume={row['volume'] if 'volume' in row else 'MISSING'}")
            
            events.append({
                "ticker": ticker,
                "event_type": "round_number",
                "event_subtype": reaction_type,
                "date": date.strftime("%Y-%m-%d"),
                "strength": float(strength),
                "context": {
                    "round_level": float(nearest_round),
                    "distance_pct": float(min_distance_pct),
                    "reaction_type": reaction_type,
                    "volatility": volatility,
                    "trend": trend,
                    "volume": float(row['volume']) if 'volume' in row and not pd.isna(row['volume']) else 0.0
                }
            })
    
    return events
