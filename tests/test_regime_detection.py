"""Test regime detection specifically."""

import sys
import pandas as pd
import numpy as np

sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')

from setup_engine.regime import detect_regimes


class TestRegimeDetection:
    """Dedicated tests for regime detection."""
    
    @staticmethod
    def create_trend_data():
        dates = pd.date_range('2020-01-01', periods=300, freq='D')
        
        # Trend 1: Strong upward (first 100 days)
        price1 = 50 + np.cumsum(np.random.normal(0.5, 0.8, 100))
        
        # Trend 2: Range bound (next 50 days)
        price2 = []
        current = price1[-1]
        for _ in range(50):
            current = current + np.random.normal(0, 0.5)
            price2.append(current)
        
        # Trend 3: Downward (last 50 days)
        price3 = [p for p in range(int(price2[-1]), int(price2[-1]) - 40, -1)]
        
        ohlc = pd.DataFrame({
            'open': [p - 1 for p in price1] + [p - 0.5 for p in price2] + [p - 0.5 for p in price3],
            'high': [p + 1.5 for p in price1] + [p + 1 for p in price2] + [p + 1 for p in price3],
            'low': [p - 1.5 for p in price1] + [p - 1 for p in price2] + [p - 1 for p in price3],
            'close': list(price1) + price2 + price3,
            'volume': [1e6] * 300
        }, index=dates)
        
        return ohlc
    
    def test_regime_classification(self):
        """Test regime classification for trend and range."""
        df = self.create_trend_data()
        regimes = detect_regimes(df)
        
        # Validate regime distribution
        regime_counts = regimes.value_counts()
        assert len(regime_counts) >= 2  # At least some regimes should be detected
        
        # Test specific regime logic
        assert all(regime in ['TRENDING_UP', 'TRENDING_DOWN', 'RANGE', 'HIGH_VOLATILITY', 'LOW_VOLATILITY'] for regime in regimes)
        
        print("✅ Regime classification test passed")
        
    def test_regime_timestamps(self):
        """Test regime timestamps align with input data."""
        df = self.create_trend_data()
        regimes = detect_regimes(df)
        
        assert len(regimes) == len(df)
        assert regimes.index.equals(df.index)
        
        print("✅ Regime timestamp alignment test passed")
        
    def test_composite_regimes(self):
        """Test that composite regimes combine trend and volatility correctly."""
        df = self.create_trend_data()
        from setup_engine.regime import get_regime_features
        regime_features = get_regime_features(df)
        
        assert 'trend' in regime_features
        assert 'volatility' in regime_features
        assert 'composite' in regime_features
        
        print("✅ Composite regime test passed")


if __name__ == '__main__':
    print("=== Testing Regime Detection ===")
    
    test_suite = TestRegimeDetection()
    test_suite.test_regime_classification()
    test_suite.test_regime_timestamps()
    test_suite.test_composite_regimes()
    
    print("\n=== All Regime Detection Tests Passed ✅ ===")
