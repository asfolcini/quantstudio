"""
Strategy generator for trading setups.
Implements template-based and combinatorial strategy generation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from .features import calculate_feature_set


def calculate_threshold(series: pd.Series, quantile: float) -> float:
    """Calculate threshold from historical data (no look-ahead)."""
    past_values = series.iloc[:-1]  # Exclude current value to avoid bias
    return past_values.quantile(quantile)


class StrategyTemplate:
    """Base class for strategy templates."""
    
    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params
        self.features = None
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate entry/exit signals using only past data."""
        self.features = calculate_feature_set(df)
        signals = pd.DataFrame(index=df.index)
        signals['entry'] = False
        signals['exit'] = False
        return signals
        
    def validate(self) -> bool:
        """Validate strategy parameters."""
        return True


class BreakoutStrategy(StrategyTemplate):
    """Breakout strategy: Buy on new highs."""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = super().generate_signals(df)
        high = df['high']
        
        # Calculate rolling high (only past data)
        rolling_high = high.shift(1).rolling(self.params.get('window', 20)).max()
        
        # Entry: Current high > rolling high
        signals['entry'] = high > rolling_high
        
        # Exit: Fixed holding period or opposite signal
        if self.params.get('exit_type') == 'holding_period':
            signals['exit'] = False  # Handled in backtest
        else:
            signals['exit'] = False  # Handled in backtest
            
        return signals


class RSIMeanReversion(StrategyTemplate):
    """RSI mean reversion strategy."""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = super().generate_signals(df)
        close = df['close']
        
        # Calculate RSI using strategy-specific period
        rsi_window = self.params.get('rsi_period', 14)
        if rsi_window != 14:  # Only recalculate if different from base features
            from .features import calculate_rsi
            rsi = calculate_rsi(close, rsi_window)
        else:
            rsi = self.features['rsi']  # Use pre-calculated RSI for period 14
        
        # Determine thresholds from past data
        overbought = calculate_threshold(rsi, 0.85)
        oversold = calculate_threshold(rsi, 0.15)
        
        # Entry signals
        if self.params.get('direction') == 'short':
            signals['entry'] = rsi > overbought
        else:  # long
            signals['entry'] = rsi < oversold
            
        return signals


class PullbackInTrend(StrategyTemplate):
    """Buy pullbacks in established uptrends."""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = super().generate_signals(df)
        close = df['close']
        
        # Trend definition (using past data) - ensure Series alignment
        ma_20 = self.features['ma_20']
        ma_50 = self.features['ma_50']
        
        # Ensure all Series have the same index for comparison
        close_aligned = close.reindex(ma_20.index)
        ma_20_aligned = ma_20.reindex(close_aligned.index)
        ma_50_aligned = ma_50.reindex(close_aligned.index)
        
        # Price above key MAs + positive slope = trend
        is_uptrend = (close_aligned > ma_20_aligned) & (close_aligned > ma_50_aligned) & (ma_20_aligned > ma_50_aligned)
        
        # Pullback definition: Price near MA support - ensure Series alignment
        pullback = (close_aligned - ma_20_aligned) / close_aligned < 0.02  # Within 2% of MA
        
        signals['entry'] = is_uptrend & pullback
        
        return signals


class VolumeSpikeTrendFilter(StrategyTemplate):
    """Volume spike confirmation of trend."""
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = super().generate_signals(df)
        
        vol_z = self.features['vol_z']
        
        # Volume spike detection
        spike_threshold = calculate_threshold(vol_z, 0.95)
        signals['entry'] = (vol_z > spike_threshold)  # Varies by direction
        
        return signals


class StrategyGenerator:
    """Generate and manage trading strategies."""
    
    STRATEGY_CLASSES = {
        'breakout': BreakoutStrategy,
        'rsi_mean_reversion': RSIMeanReversion,
        'pullback_in_trend': PullbackInTrend,
        'volume_spike': VolumeSpikeTrendFilter
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.strategies = []
        self.flat_strategy = None
        
    def generate_combinatorial_strategies(self) -> List[StrategyTemplate]:
        """
        Generate strategies combinatorially with different parameters.
        Limit total to prevent explosion.
        """
        strategies = []
        
        # Breakout variations
        for window in [10, 20, 50]:
            strategy = BreakoutStrategy(
                f"Breakout_{window}D",
                {"window": window, "exit_type": "holding_period"}
            )
            strategies.append(strategy)
            
        if len(strategies) >= 1000:
            return strategies[:1000]  # Safety limit
            
        # RSI Mean Reversion variations
        for rsi_period in [7, 14, 21]:
            for direction in ['long', 'short']:
                strategy = RSIMeanReversion(
                    f"RSI_{direction}_{rsi_period}",
                    {"direction": direction, "rsi_period": rsi_period}
                )
                strategies.append(strategy)
                
        if len(strategies) >= 1000:
            return strategies[:1000]
            
        # Pullback in trend
        strategy = PullbackInTrend("PullbackInTrend", {})
        strategies.append(strategy)
        
        # Volume spike filtration
        strategy = VolumeSpikeTrendFilter("VolumeSpikeFilter", {})
        strategies.append(strategy)
        
        return strategies

    def prune_strategies(self, strategies: List[StrategyTemplate]) -> List[StrategyTemplate]:
        """Remove redundant strategies."""
        if len(strategies) <= 1000:
            return strategies
        
        # Simple strategy name-based deduplication
        seen_names = set()
        pruned = []
        
        for strategy in strategies:
            if strategy.name not in seen_names:
                pruned.append(strategy)
                seen_names.add(strategy.name)
                
            if len(pruned) >= 1000:
                break
                
        return pruned

    def generate_all(self) -> List[StrategyTemplate]:
        """Generate all strategies with constraints."""
        combinatorial = self.generate_combinatorial_strategies()
        pruned = self.prune_strategies(combinatorial)
        return pruned
