"""Test suite for setup finder fixes."""

import sys
import pandas as pd
import numpy as np
import json
import os

# Add the quantstudio directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup_engine.backtest import BacktestEngine, Trade
from setup_engine.walk_forward import WalkForwardValidator
from setup_engine.runner import run

class TestBacktestEngine:
    """Test backtest engine fixes."""
    
    def test_empty_trades(self):
        """Test empty trades handling."""
        df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'volume': [1000, 1200, 1100]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        signals = pd.DataFrame(index=df.index)
        signals['entry'] = False
        signals['exit'] = False
        
        regime_series = pd.Series(['UP' for _ in range(len(df))], index=df.index)
        
        engine = BacktestEngine(df)
        trades = engine.simulate(signals, regime_series)
        metrics = engine.aggregate_results()
        
        # Should return safe defaults, not NaN or errors
        assert 'total_trades' in metrics
        assert metrics['total_trades'] == 0
        assert metrics['profit_factor'] == 0.0
        assert 'max_drawdown' in metrics
        assert not np.isnan(metrics['max_drawdown'])
        
    def test_profit_factor_with_wins_only(self):
        """Test profit factor calculation when only wins exist."""
        df = pd.DataFrame({
            'open': [100, 105, 110],
            'high': [105, 110, 115],
            'low': [95, 100, 105],
            'close': [100, 105, 110],
            'volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        # Create entry signal for first bar only
        signals = pd.DataFrame(index=df.index)
        signals['entry'] = [True] + [False] * (len(df) - 1)
        signals['exit'] = [False, True, False]
        
        regime_series = pd.Series(['UP' for _ in range(len(df))], index=df.index)
        
        engine = BacktestEngine(df)
        trades = engine.simulate(signals, regime_series)
        metrics = engine.aggregate_results()
        
        # Should not crash or return inf
        assert 'profit_factor' in metrics
        assert not np.isinf(metrics['profit_factor'])
        # Should be capped at 10.0
        assert metrics['profit_factor'] <= 10.0

class TestWalkForwardValidator:
    """Test walk-forward validation fixes."""
    
    def test_minimum_folds(self):
        """Test that walk-forward generates minimum of 3 folds."""
        # Create synthetic data with 100 bars (enough for multiple folds)
        np.random.seed(42)
        df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.normal(0, 1, 100)),
            'high': 100 + np.cumsum(np.random.normal(0, 1, 100)) + 1,
            'low': 100 + np.cumsum(np.random.normal(0, 1, 100)) - 1,
            'close': 100 + np.cumsum(np.random.normal(0, 1, 100)),
            'volume': 1000 + np.random.normal(0, 100, 100)
        }, index=pd.date_range('2023-01-01', periods=100))
        
        validator = WalkForwardValidator(df)
        splits = validator.create_splits()
        
        # Should have at least 3 folds
        assert len(splits) >= 3, f"Expected at least 3 folds, got {len(splits)}"
        
        # Check that folds are non-overlapping and chronological
        for i, (train, test) in enumerate(splits):
            assert len(train) > 0 and len(test) > 0, f"Fold {i} has empty train or test"
            train_end = train.index[-1]
            test_start = test.index[0]
            assert train_end < test_start, f"Fold {i} has overlapping train/test"
        
    def test_small_data_fallback(self):
        """Test fallback behavior with small datasets."""
        # Create small dataset
        df = pd.DataFrame({
            'open': [100, 102, 101, 103],
            'high': [102, 103, 103, 104],
            'low': [99, 101, 100, 102],
            'close': [100, 102, 101, 103],
            'volume': [1000, 1200, 1100, 1300]
        }, index=pd.date_range('2023-01-01', periods=4))
        
        validator = WalkForwardValidator(df)
        splits = validator.create_splits()
        
        # With very small data, falls back gracefully
        assert len(splits) == 0, "Should return empty for very small datasets"

class TestSetupRunner:
    """Test full setup runner."""
    
    def test_top_setups_count(self):
        """Test that runner returns top 8 setups in production mode."""
        # Create synthetic data
        np.random.seed(42)
        df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
            'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
            'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
            'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
            'volume': 1000 + np.random.normal(0, 100, 300)
        }, index=pd.date_range('2023-01-01', periods=300))
        
        # Run in production mode (test_mode=False)
        result = run(df, \'TEST\')
        
        assert 'top_setups' in result
        top_setups = result['top_setups']
        
        # Should return top 8 setups
        assert len(top_setups) == 8, f"Expected 8 setups in production mode, got {len(top_setups)}"
        
        # Verify each setup has required metrics
        for setup in top_setups:
            assert 'metrics' in setup
            assert 'trades' in setup['metrics']
            assert 'avg_trade' in setup['metrics']
            assert 'avg_win' in setup['metrics']
            assert 'avg_loss' in setup['metrics']
            assert 'expectancy' in setup['metrics']

    def test_no_nan_in_output(self):
        """Test that final JSON contains no NaN values."""
        np.random.seed(42)
        df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
            'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
            'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
            'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
            'volume': 1000 + np.random.normal(0, 100, 300)
        }, index=pd.date_range('2023-01-01', periods=300))
        
        result = run(df, \'TEST\')
        
        # Convert to JSON to check for NaN
        json_str = json.dumps(result)
        assert json_str is not None
        
        # Check specific numeric fields
        for setup in result.get('top_setups', []):
            for key, value in setup.get('metrics', {}).items():
                if isinstance(value, (int, float)):
                    assert not np.isnan(value), f"Found NaN in {key} for setup {setup.get('name')}"
                    assert not np.isinf(value), f"Found Inf in {key} for setup {setup.get('name')}"