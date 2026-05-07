"""Event-driven backtesting engine."""

import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Trade:
    entry_index: int
    entry_time: pd.Timestamp
    entry_price: float
    regime: str
    exit_index: int = None
    exit_time: pd.Timestamp = None
    exit_price: float = None
    exit_regime: str = None
    
    @property
    def result(self) -> float:
        """Calculate holdings period return."""
        if self.exit_price:
            return (self.exit_price / self.entry_price) - 1
        return 0
        
    @property
    def is_winner(self) -> bool:
        return self.result > 0


class BacktestEngine:
    """Event-driven backtesting with regime tracking."""
    
    def __init__(self, df: pd.DataFrame, fixed_holding_period: int = 5):
        self.df = df
        self.holding_period = fixed_holding_period
        self.trades = []
        self.open_position = None
        
    def simulate(self, strategy_signals: pd.DataFrame, regime_series: pd.Series) -> List[Trade]:
        """
        Run event-driven simulation.
        Entry on current bar only, Exit on future bars.
        """
        close = self.df['close']
        
        for i in range(len(self.df)):
            current_regime = regime_series.iloc[i] if i < len(regime_series) else "UNKNOWN"
            
            # Entry condition: Must be True on current bar only
            if strategy_signals['entry'].iloc[i]:
                if self.open_position is None:  # No position already open
                    # Enter at close of current bar (no look-ahead)
                    trade = Trade(
                        entry_index=i,
                        entry_time=self.df.index[i],
                        entry_price=close.iloc[i],
                        regime=current_regime
                    )
                    self.open_position = trade
            
            # Exit condition: Only check if position is open
            if self.open_position:
                exit_condition = strategy_signals['exit'].iloc[i]
                age = i - self.open_position.entry_index
                
                # Exit if condition met or holding period reached
                if exit_condition or age >= self.holding_period:
                    self.open_position.exit_index = i
                    self.open_position.exit_time = self.df.index[i]
                    self.open_position.exit_price = close.iloc[i]
                    self.open_position.exit_regime = regime_series.iloc[i] if i < len(regime_series) else "UNKNOWN"
                    
                    self.trades.append(self.open_position)
                    self.open_position = None
        
        # Close any remaining position at end of data
        if self.open_position:
            self.open_position.exit_index = len(self.df) - 1
            self.open_position.exit_time = self.df.index[-1]
            self.open_position.exit_price = close.iloc[-1]
            self.open_position.exit_regime = regime_series.iloc[-1] if len(regime_series) > 0 else "UNKNOWN"
            self.trades.append(self.open_position)
            self.open_position = None
        
        return self.trades
    
    def aggregate_results(self) -> Dict:
        """Aggregate trade results for analysis."""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'total_return': 0.0,
                'average_trade_return': 0.0,
                'win_rate': 0.0,
                'max_return': 0.0,
                'max_loss': 0.0,
                'profit_factor': 0.0,
                'final_equity': 1.0,
                'max_drawdown': 0.0,
                'winning_trade_returns': [],
                'losing_trade_returns': []
            }
          
        # Calculate basic metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.is_winner]
        losing_trades = [t for t in self.trades if not t.is_winner and t.result != 0]
        
        winning_returns = [t.result for t in self.trades if t.result > 0]
        losing_returns = [t.result for t in self.trades if t.result < 0]
        
        results = {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'loosing_trades': len(losing_trades),
            'total_return': float(sum(t.result for t in self.trades)),
            'average_trade_return': float(np.mean([t.result for t in self.trades]) if total_trades > 0 else 0.0),
            'win_rate': len(winning_trades) / total_trades if total_trades > 0 else 0.0,
            'max_return': max(t.result for t in self.trades) if total_trades > 0 else 0.0,
            'max_loss': min(t.result for t in self.trades) if total_trades > 0 else 0.0,
            'winning_trade_returns': winning_returns,
            'losing_trade_returns': losing_returns
        }
          
        # Calculate profit factor: sum(gains) / abs(sum(losses))
        gains = winning_returns
        losses = losing_returns
        
        if losses:
            sum_losses = sum(losses)
            profit_factor = sum(gains) / abs(sum_losses) if sum_losses != 0 else 10.0
        else:
            profit_factor = 10.0 if gains else 0.0
             
        # Cap profit factor at 10.0 to avoid extreme values
        profit_factor = min(profit_factor, 10.0)
        
        results['profit_factor'] = float(profit_factor)
          
        # Calculate drawdown from equity curve
        equity = [1.0]
        for trade in self.trades:
            equity.append(equity[-1] * (1 + trade.result))
        
        results['final_equity'] = float(equity[-1])
        # Calculate drawdown from rolling maximum
        if len(equity) > 1:
            rolling_max = np.maximum.accumulate(equity)
            drawdown_values = 1 - np.array(equity[1:]) / rolling_max[1:]  # Skip first value (1.0)
            results['max_drawdown'] = float(max(0, max(drawdown_values)) if len(drawdown_values) > 0 else 0.0)
        else:
            results['max_drawdown'] = 0.0
          
        return results
