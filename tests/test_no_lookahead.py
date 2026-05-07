"""Test no-look-ahead bias specifically."""

import sys
import pandas as pd
import numpy as np

sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')

from setup_engine.features import calculate_returns, calculate_ma, calculate_rolling_volatility


class TestNoLookahead:
    """Dedicated tests to ensure no future data leakage."""
    
    @staticmethod
    def create_test_series(segment=0):
        """Create test time series with known behavior."""
        dates = pd.date_range('2020-01-01', periods=200, freq='D')
        
        if segment == 0:
            # Flat series
            values = [100] * 200
        elif segment == 1:
            # Ascending series
            values = list(range(100, 300))
        else:
            # Descending series
            values = list(range(300, 100, -1))
            
        return pd.Series(values, index=dates)
    
    def test_returns_no_future(self):
        """Test returns calculations use only past data."""
        series = self.create_test_series(segment=1)
        returns = calculate_returns(series, periods=[1, 5])
        
        # First value should be NaN (no past data)
        assert pd.isna(returns['ret_1d'].iloc[0])
        assert pd.isna(returns['ret_5d'].iloc[:5]).all()
        
        # Values should be based on previous close only
        for i in range(1, 50):
            expected_return = (series.iloc[i] / series.iloc[i-1]) - 1
            assert abs(returns['ret_1d'].iloc[i] - expected_return) < 1e-6
            
        print("✅ No future returns test passed")
        
    def test_moving_average_no_future(self):
        """Test moving averages don't use future data."""
        series = self.create_test_series(segment=1)
        ma_5 = calculate_ma(series, 5)
        
        # First 4 values should be NaN (insufficient past data)
        assert pd.isna(ma_5.iloc[:5]).all()
        
        # Compute expected MA manually
        for i in range(5, 50):
            expected = series.iloc[i-5:i].mean()
            assert abs(ma_5.iloc[i] - expected) < 1e-6
            
        print("✅ No future moving average test passed")
        
    def test_volatility_no_future(self):
        """Test volatility calculations use only past data."""
        series = self.create_test_series(segment=1)
        vol_10 = calculate_rolling_volatility(series, 10)
        
        # No future data in calculation
        assert pd.isna(vol_10.iloc[:10]).all()  # Minimum period
        
        # Manual verification for first computable value
        serie_value_10_index = series.iloc[9] if len(series) >= 10 else series.iloc[-1]
        expected_std = series.iloc[:10].std()
        assert abs(vol_10.iloc[10] - expected_std) < 1e-6
        
        print("✅ No future volatility test passed")


if __name__ == '__main__':
    print("=== Testing No-Look-Ahead Bias ===")
    
    test_suite = TestNoLookahead()
    test_suite.test_returns_no_future()
    test_suite.test_moving_average_no_future()
    test_suite.test_volatility_no_future()
    
    print("\n=== All No-Look-Ahead Tests Passed ✅ ===")
