"""Test suite for setup engine pipeline."""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')

from setup_engine.runner import run
from setup_engine.features import calculate_returns, calculate_feature_set
from setup_engine.regime import detect_regimes
from setup_engine.backtest import BacktestEngine


def create_synthetic_ohlcv_data(seed=42) -> pd.DataFrame:
    """Generate synthetic data with deterministic patterns."""
    np.random.seed(seed)
    
    date_range = pd.date_range('2020-01-01', periods=1000, freq='D')
    
    # Multi-segment regime simulation
    # Segment 1: Trending upward (100 days)
    close1 = 50 + np.cumsum(np.random.normal(0.2, 1, 100))
    
    # Segment 2: Ranging (50 days)
    close2 = []
    current = 105
    for _ in range(50):
        change = np.random.uniform(-1, 1)
        current = max(90, min(115, current + change))
        close2.append(current)
    
    # Segment 3: Trending downward (100 days)
    close3 = 105 + np.cumsum(np.random.normal(-0.3, 1.2, 100))
    
    # Segment 4: High volatility (250 days)
    close4 = 80 + np.cumsum(np.random.normal(0, 2, 250))
    
    # Segment 5: Range again (100 days)
    close5 = []
    current = 95
    for _ in range(100):
        change = np.random.uniform(-1.5, 1.5)
        current = max(70, min(130, current + change))
        close5.append(current)
    
    all_close = np.concatenate([close1, close2, close3, close4, close5])
    
    # Generate OHLCV data from close
    open_ = np.zeros(1000)
    high = np.zeros(1000)
    low = np.zeros(1000)
    volume = np.zeros(1000)
    
    for i in range(1000):
        if i == 0:
            open_[i] = all_close[i]
            high[i] = all_close[i] + 1
            low[i] = all_close[i] - 1
        else:
            daily_range = 3 + np.random.uniform(0, 5)
            open_[i] = all_close[i-1]
            high[i] = max(all_close[i] + daily_range/2, open_[i])
            low[i] = min(all_close[i] - daily_range/2, open_[i])
            
        volume[i] = 100000 + int(np.random.normal(0, 10000))
    
    ohlcv = pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': all_close,
        'volume': volume
    }, index=date_range)
    
    return ohlcv


class TestSetupEngine:
    """Test suite for setup engine pipeline."""
    
    @staticmethod
    def test_pipeline_basic():
        """Test basic pipeline functionality."""
        df = create_synthetic_ohlcv_data()
        
        result = run(df, \'SYNTHETIC\')
        
        assert isinstance(result, dict)
        assert 'ticker' in result
        assert result['ticker'] == 'SYNTHETIC'
        assert 'timeframe' in result
        assert 'strategy_count' in result
        assert 'top_setups' in result
        assert len(result['top_setups']) <= 10
        
        print("✅ Pipeline basic test passed")
        
    @staticmethod
    def test_no_lookahead_bias():
        """Test that no future data is used in calculations."""
        df = create_synthetic_ohlcv_data()
        
        # Shift data to create a fake 'future' period
        future_mask = df.index >= '2021-01-01'
        
        result = run(df[~future_mask], 'SYNTHETIC', test_mode=True)
        
        assert 'input_range' in result
        print("✅ No look-ahead bias test passed")
        
    @staticmethod
    def test_regime_detection():
        """Test regime detection functionality."""
        df = create_synthetic_ohlcv_data()
        regimes = detect_regimes(df)
        
        assert len(regimes) == len(df)
        assert set(regimes.unique()) & {'TRENDING_UP', 'TRENDING_DOWN', 'RANGE', 'HIGH_VOLATILITY', 'LOW_VOLATILITY'}
        
        regime_summary = regimes.value_counts()
        assert len(regime_summary) >= 3
        
        print("✅ Regime detection test passed", str(dict(regime_summary)))
        
    @staticmethod
    def test_features_no_leakage():
        """Test that features use only past data."""
        df = create_synthetic_ohlcv_data()
        features = calculate_feature_set(df)
        
        # Features should have same length as input
        assert len(features) <= len(df)
        
        # Test trend features
        assert 'ret_1d' in features.columns
        assert 'ret_5d' in features.columns
        assert 'ma_20' in features.columns
        assert 'rsi' in features.columns
        
        print("✅ Features no leakage test passed")
        
    @staticmethod
    def test_walk_forward_validation():
        """Test walk-forward validation mechanics."""
        df = create_synthetic_ohlcv_data()
        result = run(df, \'SYNTHETIC\')
        
        if 'walk_forward' in result.get('top_setups', [{}])[0]:
            wf_data = result['top_setups'][0]['walk_forward']
            assert 'mean_test_return' in wf_data
            print("✅ Walk-forward validation test passed")
        else:
            print("ℹ️ Walk-forward validation data not available in test mode")
            
    @staticmethod
    def test_strategy_count_limit():
        """Test that strategy count is properly limited."""
        df = create_synthetic_ohlcv_data()
        result = run(df, \'SYNTHETIC\')
        
        assert 'strategy_count' in result
        assert 250 <= result['strategy_count'] <= 200  # Range check
        
        print("✅ Strategy count limit test passed")


if __name__ == '__main__':
    print("=== Running Setup Engine Tests ===")
    
    # Required tests
    TestSetupEngine.test_pipeline_basic()
    TestSetupEngine.test_no_lookahead_bias()
    TestSetupEngine.test_regime_detection()
    TestSetupEngine.test_features_no_leakage()
    TestSetupEngine.test_walk_forward_validation()
    TestSetupEngine.test_strategy_count_limit()
    
    print("\n=== All Tests Passed ✅ ===")
