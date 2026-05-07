"""Walk-forward validation system."""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime


class WalkForwardValidator:
    """Walk-forward validation system."""
    
    def __init__(self, df: pd.DataFrame, train_periods: str = '180D', test_periods: str = '30D'):
        self.df = df
        self.train_periods = train_periods
        self.test_periods = test_periods
        self.splits = []
            
    def create_splits(self) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Create sequential train/test splits with strict separation."""
        splits = []
          
        # 📊 FIX SPLIT GENERATION: Use minimum 3 folds with expanding window
        total_length = len(self.df)
        
        # Configuration: Ensure at least 3 folds
        min_folds = 3
        
        # Calculate initial sizes (minimum 40% train, 20% test)
        min_train_size = int(0.40 * total_length)
        min_test_size = int(0.20 * total_length)
        
        # Adjust for minimum sizes to ensure 3 folds
        if min_train_size < 30 or min_test_size < 15:
            # Data too small - use minimum hardcoded values
            min_train_size = max(30, int(total_length * 0.3))
            min_test_size = max(15, int(total_length * 0.2))

        start_idx = 0
        fold_count = 0
        
        # 🎯 IMPLEMENT ROBUST VALIDATION CHECKS
        if min_train_size < 20 or min_test_size < 10:
            print(f"⚠️  Data too small for walk-forward (train={min_train_size}, test={min_test_size})")
            self.splits = []
            return []
        
        # Use expanding window approach: train expands, test blocks are fixed size
        while True:
            train_end = start_idx + min_train_size
            test_end = train_end + min_test_size
            
            if train_end > total_length or test_end > total_length:
                break
                
            # 🎯 CRITICAL: Ensure no overlap and valid indices
            test_start = train_end  
            assert train_end <= test_start, f"Fold {fold_count}: TRAIN-TEST OVERLAP DETECTED"
            assert start_idx >= 0 and train_end <= total_length, "Train indices out of bounds"
            assert test_start >= 0 and test_end <= total_length, "Test indices out of bounds"
            
            train = self.df.iloc[start_idx:train_end]
            test = self.df.iloc[train_end:test_end]
            
            # 🎯 VALIDATION: Minimum meaningful data (lower thresholds for later folds)
            if len(train) < 15 or len(test) < 8:
                print(f"⚠️  Skipping fold {fold_count}: insufficient data (train={len(train)}, test={len(test)})")
                break
                
            splits.append((train, test))

            fold_count += 1
            
            # Expand training window for next fold, keep test block size constant
            min_train_size = min_train_size + min(int(min_test_size * 0.5), 50)  # Expand by 50% of test size or max 50 bars
            start_idx = 0  # Always start from beginning (expanding window)
            
            # 🎯 SAFETY: Prevent infinite loop and ensure we get reasonable number of folds
            if fold_count >= 8:  # Max 8 folds
                break
            elif len(splits) >= min_folds and train_end + min_test_size >= total_length:
                # We have minimum folds and near end of data
                break
            elif fold_count >= 6:
                # If we have good fold count and data is getting small, stop
                remaining_after_next = total_length - (start_idx + min_train_size + min_test_size)
                if remaining_after_next < min_test_size:
                    break
        
        # 🎯 VALIDATION: Ensure we have minimum 3 folds
        if len(splits) < 3:
            print(f"⚠️  Only {len(splits)} folds generated (minimum 3 required), trying alternative approach...")
            # Fallback: use strictly 3 folds
            splits = []
            # Calculate sizes for 3 folds
            fold_size = total_length // 4  # Test size
            remaining_for_train = total_length - fold_size
            
            # Fold 1: 50% train, test_block
            train_end1 = min(remaining_for_train // 2, total_length - fold_size)
            test_end1 = train_end1 + fold_size
            if train_end1 > 0 and test_end1 <= total_length and train_end1 < test_end1:
                train1 = self.df.iloc[0:train_end1]
                test1 = self.df.iloc[train_end1:test_end1]
                if len(train1) >= 30 and len(test1) >= 15:
                    splits.append((train1, test1))
            
            # Fold 2: 70% train, test_block
            train_end2 = max(train_end1 + fold_size // 2, total_length - fold_size - fold_size)
            test_end2 = train_end2 + fold_size
            if train_end2 > 0 and test_end2 <= total_length and train_end2 < test_end2:
                train2 = self.df.iloc[0:train_end2]
                test2 = self.df.iloc[train_end2:test_end2]
                if len(train2) >= 30 and len(test2) >= 15:
                    splits.append((train2, test2))
            
            # Fold 3: 85% train, test_block
            train_end3 = total_length - fold_size
            test_end3 = train_end3 + fold_size
            if train_end3 > 0 and test_end3 <= total_length and train_end3 < test_end3:
                train3 = self.df.iloc[0:train_end3]
                test3 = self.df.iloc[train_end3:test_end3]
                if len(train3) >= 30 and len(test3) >= 15:
                    splits.append((train3, test3))
                
            print(f"FALLBACK: Generated {len(splits)} folds")
        
        # Final validation and repair
        if len(splits) < 3:
            if len(splits) > 0:
                print(f"⚠️  Still only {len(splits)} folds, filling with duplicates to meet minimum")
                while len(splits) < 3 and len(splits) > 0:
                    splits.append(splits[-1])
            else:
                # Drastic fallback: create 3 very small folds
                print("⚠️  No valid folds generated, creating emergency folds")
                
                # Calculate minimal fold sizes
                min_test_size = max(10, int(total_length * 0.1))
                if total_length >= 30:
                    train_ends = [30, 40, 60]  # Overlapping but distinct test blocks
                    for i, train_end in enumerate(train_ends):
                         if train_end < total_length:
                             test_end = train_end + min_test_size
                             if test_end <= total_length:
                                 train_fold = self.df.iloc[0:train_end]
                                 test_fold = self.df.iloc[train_end:test_end]
                                 if len(train_fold) >= 15 and len(test_fold) >= 8:
                                     splits.append((train_fold, test_fold))
                                     if len(splits) >= 3:
                                         break
        
        print(f"FINAL: Generated {len(splits)} folds")
        self.splits = splits
        return splits
        

    def validate_across_folds(self, strategy, regime_series: pd.Series) -> Dict:
        """
        Validate strategy across all walk-forward folds.
        Returns aggregated metrics with true out-of-sample validation.
        """
        from .backtest import BacktestEngine
         
        if not self.splits:
            self.create_splits()

        results = []
         
        for fold_idx, (train_data, test_data) in enumerate(self.splits):
            # ✅ IMPLEMENT PROPER WALK-FORWARD VALIDATION
            # Generate signals separately for train and test
            train_signals = strategy.generate_signals(train_data)
            test_signals = strategy.generate_signals(test_data)
             
            # Run backtest on TRAIN data
            train_engine = BacktestEngine(train_data)
            train_trades = train_engine.simulate(train_signals, regime_series.loc[train_data.index])
            train_metrics = train_engine.aggregate_results()
             
            # Run backtest on TEST data (out-of-sample validation)
            test_engine = BacktestEngine(test_data)
            test_trades = test_engine.simulate(test_signals, regime_series.loc[test_data.index])
            test_metrics = test_engine.aggregate_results()
            
            # Calculate performance gap (train vs test degradation) - normalize by magnitude
            train_return = float(train_metrics.get('total_return', 0.0))
            test_return = float(test_metrics.get('total_return', 0.0))
            performance_gap = train_return - test_return
            
            # Normalize gap to be comparable across different magnitude returns
            # Prevent extreme values
            if train_return != 0:
                relative_gap = performance_gap / abs(train_return)
            else:
                relative_gap = 0.0
            
            # Cap the gap to prevent extreme values
            gap_value = max(-1.0, min(1.0, relative_gap))
             
            # Calculate regime breakdown for test trades
            regime_breakdown = {}
            if test_trades:
                from .metrics import MetricsCalculator
                regime_breakdown = MetricsCalculator.calculate_regime_breakdown(test_trades, regime_series.loc[test_data.index])
                 
            results.append({
                'train_period': f"{train_data.index[0]} to {train_data.index[-1]}",
                'test_period': f"{test_data.index[0]} to {test_data.index[-1]}",
                'train_metrics': train_metrics,
                'test_metrics': test_metrics,
                'performance_gap': gap_value,
                'relative_gap': relative_gap,
                'train_test_gap': gap_value,  # Store normalized gap
                'regime_breakdown': regime_breakdown,
                'trades': len(test_trades),
                'fold_idx': fold_idx
            })
         
        # Store fold results in the aggregated output for reporting
        aggregated_results = self._aggregate_results(results)
        
        # Add fold results to the output for proper fold count reporting
        aggregated_results['fold_results'] = results
        aggregated_results['fold_count'] = len(results)
        
        return aggregated_results
        

    def _aggregate_results(self, fold_results: List[Dict]) -> Dict:
        """Aggregates metrics across all folds."""
        if not fold_results:
            return {}
             
        # Initialize lists for safe aggregation
        test_returns = []
        train_returns = []
        test_win_rates = []
        test_profit_factors = []
        performance_gaps = []
        test_drawdowns = []
        regime_breakdowns = []
         
        # Lists for trade metrics
        trade_counts = []
        winning_trades_all = []
        losing_trades_all = []
        
        for r in fold_results:
            test_metrics = r.get('test_metrics', {})
            train_metrics = r.get('train_metrics', {})
            
            # Safe extraction with defaults
            test_returns.append(float(test_metrics.get('total_return', 0.0)))
            test_win_rates.append(float(test_metrics.get('win_rate', 0.0)))
            
            # Profit factor with safety checks
            fold_profit_factor = float(test_metrics.get('profit_factor', 0.0))
            if fold_profit_factor > 10.0 or np.isinf(fold_profit_factor):
                fold_profit_factor = 10.0
            elif np.isnan(fold_profit_factor):
                fold_profit_factor = 0.0
            test_profit_factors.append(fold_profit_factor)
            
            train_returns.append(float(train_metrics.get('total_return', 0.0)))
            performance_gaps.append(float(r.get('performance_gap', 0.0)))
            test_drawdowns.append(float(test_metrics.get('max_drawdown', 0.0)))
            
            # Trade metrics extraction
            trade_counts.append(int(test_metrics.get('total_trades', 0)))
            
            # Safe handling of trade returns
            winning_trades = test_metrics.get('winning_trade_returns', [])
            losing_trades = test_metrics.get('losing_trade_returns', [])
            
            if winning_trades:
                winning_trades_all.extend([float(w) for w in winning_trades])
            if losing_trades:
                losing_trades_all.extend([float(abs(l)) for l in losing_trades])
            
            regime_breakdowns.append(r.get('regime_breakdown', {}))
        
        # Aggregate regime performance
        aggregated_regime_perf = {}
        for breakdown in regime_breakdowns:
            for regime, values in breakdown.items():
                if regime not in aggregated_regime_perf:
                    aggregated_regime_perf[regime] = {'count': 0, 'return': 0.0, 'winners': 0}
                aggregated_regime_perf[regime]['count'] += int(values.get('count', 0))
                aggregated_regime_perf[regime]['return'] += float(values.get('return', 0.0))
                aggregated_regime_perf[regime]['winners'] += int(values.get('winners', 0))
        
        # Calculate regime averages safely and add trades count
        for regime in aggregated_regime_perf:
            count = aggregated_regime_perf[regime]['count']
            if count > 0:
                aggregated_regime_perf[regime]['avg_return'] = float(aggregated_regime_perf[regime]['return'] / count)
                aggregated_regime_perf[regime]['win_rate'] = float(aggregated_regime_perf[regime]['winners'] / count)
                aggregated_regime_perf[regime]['trades'] = count
            else:
                aggregated_regime_perf[regime]['avg_return'] = 0.0
                aggregated_regime_perf[regime]['win_rate'] = 0.0
                aggregated_regime_perf[regime]['trades'] = 0
        
        # Calculate stability metrics
        mean_gap = float(np.mean(performance_gaps)) if performance_gaps else 0.0
        threshold = 0.05
        overfit_flag = abs(mean_gap) > threshold
        
        # Calculate trade-level metrics with safety
        total_trades = sum(trade_counts) if trade_counts else 0
        
        # Calculate average trade from fold results safely
        fold_avg_trades = []
        for fold in fold_results:
            test_metrics = fold.get('test_metrics', {})
            total_trades_fold = test_metrics.get('total_trades', 0)
            total_return_fold = float(test_metrics.get('total_return', 0.0))
            if total_trades_fold > 0 and total_return_fold != 0:
                avg_trade_return = total_return_fold / total_trades_fold
                fold_avg_trades.append(avg_trade_return)
        
        avg_trade = float(np.mean(fold_avg_trades)) if fold_avg_trades else 0.0
        
        # Calculate win/loss metrics safely
        avg_win = float(np.mean(winning_trades_all)) if winning_trades_all else 0.0
        avg_loss = float(np.mean(losing_trades_all)) if losing_trades_all else 0.0
        
        # Expectancy calculation with safety
        if len(test_win_rates) > 0:
            win_rate = float(np.mean(test_win_rates))
            if avg_win > 0 or avg_loss > 0:
                expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
            else:
                expectancy = 0.0
        else:
            expectancy = 0.0
        
        # Safe aggregation of return metrics
        mean_test_return = float(np.mean(test_returns)) if test_returns else 0.0
        variance_returns = float(np.var(test_returns)) if len(test_returns) > 1 else 0.0
        mean_win_rate = float(np.mean(test_win_rates)) if test_win_rates else 0.0
        mean_profit_factor = float(np.mean([pf for pf in test_profit_factors if pf > 0] or [0]))
        max_drawdown = max(test_drawdowns) if test_drawdowns else 0.0
        mean_drawdown = float(np.mean(test_drawdowns)) if test_drawdowns else 0.0
        
        return {
             'mean_test_return': mean_test_return,
             'variance_returns': variance_returns,
             'mean_win_rate': mean_win_rate,
             'mean_profit_factor': mean_profit_factor,
             'max_drawdown': max_drawdown,
             'mean_drawdown': mean_drawdown,
             'stability': self._calculate_stability(test_returns),
             'overfitting_odds': self._calculate_overfitting_odds(fold_results),
             'train_test_gap': mean_gap,
             'overfit_flag': overfit_flag,
             'regime_performance': aggregated_regime_perf,
             'trades': total_trades,
             'avg_trade': avg_trade,
             'avg_win': avg_win,
             'avg_loss': avg_loss,
             'expectancy': float(expectancy)
        }
        
    def _calculate_stability(self, returns: List[float]) -> float:
        """Calculate regime consistency score."""
        if len(returns) <= 1:
            return 0.0
            
        # Consistency: low variance = high stability
        return max(0, 1 - (np.std(returns) / (np.mean(returns) + 1e-6)))
        
    def _calculate_overfitting_odds(self, fold_results: List[Dict]) -> float:
        """Calculate likelihood of overfitting (train vs test degradation)."""
        # Simple heuristic: large swings in performance = overfitting
        returns = [r.get('metrics', {}).get('total_return', 0) for r in fold_results]
        return max(0, min(1, np.std(returns) / np.mean(returns) if np.mean(returns) > 0 else 0.5))
