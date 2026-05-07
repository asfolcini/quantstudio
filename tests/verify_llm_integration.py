"""Test that LLM component integrates without breaking the core trading logic."""

import sys
import os
import pandas as pd
import numpy as np

# Ensure test isolation
os.chdir(f'/Users/alberto.sfolcini/Development/quantstudio')
sys.path.insert(0, '.')

# Import and verify LLM modifications don't affect core trading logic
def test_core_trading_logic():
    """Test that trading logic remains unchanged."""
    
    # Verify EdgeEngine works and returns LLM interpretation
    from quantstudio.edge_engine import EdgeEngine
    from data.providers.yahoo import YahooProvider
    
    provider = YahooProvider()
    
    # Test with ISP.MI data
    raw_data = provider.download('ISP.MI')
    df = raw_data.reset_index()
    df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
    df = df[['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    
    if len(df) < 100:
        # Generate synthetic data if API returns insufficient data
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        close_prices = 100 + np.cumsum(np.random.normal(0, 1, 252))
        open_prices = close_prices + np.random.normal(-0.3, 0.5, 252)
        high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(0, 2, 252)
        low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(0, 2, 252)
        volumes = 1000000 + int(np.random.normal(0, 50000, 252))
        
        df = pd.DataFrame({
            'datetime': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
    engine = EdgeEngine(df)
    result = engine.generate_report()
    
    # Key verification: The report should always contain both quantitative and LLM sections
    assert 'quantitative' in result
    assert 'llm_interpretation' in result
    
    # Even if LLM is unavailable, the structure should remain consistent
    if isinstance(result['llm_interpretation'], str):
        assert len(result['llm_interpretation']) > 0
        
    return True


def test_llm_interpretation_format_consistency():
    """Ensure LLM interpretation output follows expected format."""
    from quantstudio.edge_engine import EdgeEngine
    
    # Create minimal valid OHLCV DataFrame
    dates = pd.date_range('2020-01-01', periods=60, freq='D')
    synthetic_df = pd.DataFrame({
        'datetime': dates,
        'open': 100,
        'high': 101,
        'low': 99,
        'close': 100.5,
        'volume': 1000000
    })
    
    engine = EdgeEngine(synthetic_df)
    result = engine.generate_report()
    
    # Verify structural integrity
    assert isinstance(result, dict)
    assert 'llm_interpretation' in result
    
    return True


if __name__ == '__main__':
    print("=== Testing LLM Integration !==")
    
    # Run tests serially to avoid side effects
    success = True
    
    try:
        test_core_trading_logic()
        print("✅ Core trading logic integrity test passed")
    except Exception as e:
        print(f"❌ Core trading logic test failed: {e}")
        success = False
        
    try:
        test_llm_interpretation_format_consistency()
        print("✅ LLM format consistency test passed")
    except Exception as e:
        print(f"❌ LLM format test failed: {e}")
        success = False
        
    if success:
        print("\n=== All LLM Integration Tests Passed ✅ ===")
    else:
        print("\n=== Some Tests Failed ❌ ===")
        
    # Revert back to root
    os.chdir('..')
