"""Performance metrics and evaluation."""

import pandas as pd
import numpy as np
from typing import Dict, List


class MetricsCalculator:
    """Calculate performance metrics for strategies."""
    
    @staticmethod
    def calculate_trade_metrics(trades: List) -> Dict:
        """Calculate basic trade metrics."""
        if not trades:
            return {}
            
        returns = [t.result for t in trades]
        
        return {
            'total_return': sum(returns),
            'total_trades': len(trades),
            'winning_trades': sum(1 for t in trades if t.result > 0),
            'win_rate': sum(1 for t in trades if t.result > 0) / len(trades),
            'profit_factor': sum(r for r in returns if r > 0) / -sum(r for r in returns if r < 0) if sum(r for r in returns if r < 0) < 0 else 0
        }
        
    @staticmethod
    def calculate_equity_metrics(trades: List, initial_capital: float = 1.0) -> Dict:
        """Calculate equity curve metrics."""
        equity = [initial_capital]
        
        for trade in trades:
            equity.append(equity[-1] * (1 + trade.result))
        
        returns_series = np.diff(equity) / equity[:-1]
        
        return {
            'cagr': (equity[-1] / equity[0]) ** (252/len(trades)) - 1 if trades else 0,
            'max_drawdown': max(1 - e/m for e, m in zip(equity, np.maximum.accumulate(equity))),
            'volatility': np.std(returns_series) * np.sqrt(252),
            'sharpe_ratio': (np.mean(returns_series) * 252) / (np.std(returns_series) * np.sqrt(252)) if np.std(returns_series) > 0 else 0
        }
        
    @staticmethod
    def calculate_regime_breakdown(trades: List, regime_series: pd.Series) -> Dict:
        """Calculate performance by market regime."""
        breakdown = {}
        
        for trade in trades:
            regime = trade.regime
            exit_regime = trade.exit_regime
            
            if regime not in breakdown:
                breakdown[regime] = {
                    'count': 0,
                    'return': 0,
                    'winners': 0
                }
                
            breakdown[regime]['count'] += 1
            breakdown[regime]['return'] += trade.result
            
            if trade.result > 0:
                breakdown[regime]['winners'] += 1
                
        # Calculate averages
        for regime in breakdown:
            count = breakdown[regime]['count']
            breakdown[regime]['avg_return'] = breakdown[regime]['return'] / count if count > 0 else 0
            breakdown[regime]['win_rate'] = breakdown[regime]['winners'] / count if count > 0 else 0
            
        return breakdown
        
    @staticmethod
    def combine_metrics(trade_metrics: Dict, equity_metrics: Dict, regime_metrics: Dict) -> Dict:
        """Combine all metrics into one dictionary."""
        return {
            'performance': trade_metrics,
            'risk': equity_metrics,
            'regime_breakdown': regime_metrics
        }
        
    @staticmethod
    def extract_key_metrics(combined_metrics: Dict) -> Dict:
        """Extract key metrics for scoring."""
        return {
            'total_return': combined_metrics['performance'].get('total_return', 0),
            'win_rate': combined_metrics['performance'].get('win_rate', 0),
            'profit_factor': combined_metrics['performance'].get('profit_factor', 0),
            'max_drawdown': combined_metrics['risk'].get('max_drawdown', 0),
            'sharpe_ratio': combined_metrics['risk'].get('sharpe_ratio', 0),
            'regime_consistency': len(combined_metrics['regime_breakdown'])
        }
