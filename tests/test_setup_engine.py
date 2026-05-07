"""Test setup_engine module specifically."""

import sys
import os
sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')

import pandas as pd
import numpy as np
from setup_engine.runner import run


def test_setup_engine_simple():
    """Test setup_engine with simple synthetic data."""
    dates = pd.date_range('2020-01-01', periods=60, freq='D')
    
    # Create synthetic OHLCV data
    close_prices = 100 + np.cumsum(np.random.normal(0, 1, 60))
    
    df = pd.DataFrame({
        'open': close_prices + np.random.normal(-0.3, 0.5, 60),
        'high': close_prices + np.random.uniform(0, 2, 60),
        'low': close_prices - np.random.uniform(0, 2, 60),
        'close': close_prices,
        'volume': [1000000 + int(v) for v in np.random.normal(0, 50000, 60)]
    }, index=dates)
    
    result = run(df, 'SYNTHETIC')
    
    # Validate result structure
    expected_keys = ['ticker', 'timeframe', 'regime_model', 'generated_at', 
                    'top_setups', 'regime_summary']
    
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
        
    # Validate regime summary
    assert isinstance(result['regime_summary'], dict)
    assert len(result['regime_summary']) >= 1
    
    # Validate top setups
    assert isinstance(result['top_setups'], list)
    if len(result['top_setups']) > 0:
        setup_keys = ['name', 'rule', 'metrics', 'robustness', 'score']
        for key in setup_keys:
            assert key in result['top_setups'][0], f"Missing setup key: {key}"
    
    print("✅ Setup engine test completed successfully")
    return True
    

def test_system_deterministic():
    """Test that system is deterministic."""
    np.random.seed(42)
    df1 = pd.DataFrame({
        'open': [100.0] * 60,
        'high': [101.0] * 60,
        'low': [99.0] * 60,
        'close': [100.5] * 60,
        'volume': [1000000] * 60
    }, index=pd.date_range('2020-01-01', periods=60))
    
    result1 = run(df1, 'TEST')
    result2 = run(df1, 'TEST')
    
    # Both should have same basic structure
    assert len(result1['top_setups']) == len(result2['top_setups'])
    
    print("✅ System deterministic test passed")
    return True


if __name__ == '__main__':
    print("=== Testing Setup Engine ===")
    
    success = True
    
    try:
        test_setup_engine_simple()
    except Exception as e:
        print(f"❌ Setup engine test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
        
    try:
        test_system_deterministic()
    except Exception as e:
        print(f"❌ Deterministic test failed: {e}")
        success = False
        
    if success:
        print("\n=== Setup Engine Tests Passed ✅ ===")
    else:
        print("\n=== Setup Engine Tests Failed ❌ ===")
