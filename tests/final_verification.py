"""Simple verification test for setup_engine."""

import sys
sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')

import pandas as pd
import numpy as np
from setup_engine.runner import run

# Create test data
dates = pd.date_range('2020-01-01', periods=100, freq='D')

# Generate realistic OHLC prices
close_prices = [100] * 100
for i in range(1, 100):
    close_prices[i] = close_prices[i-1] + np.random.normal(0, 1.5)

df = pd.DataFrame({
    'open': [c - np.random.uniform(0, 0.5) for c in close_prices],
    'high': [c + np.random.uniform(0, 1.5) for c in close_prices],
    'low': [c - np.random.uniform(0, 1.0) for c in close_prices],
    'close': close_prices,
    'volume': [1000000 + int(np.random.normal(0, 100000)) for _ in range(100)]
}, index=dates)

print('Testing setup_engine with synthetic OHLCV data...')
print(f'DataFrame: {len(df)} bars')

try:
    # Run with test_mode for faster execution
    result = run(df, \'TEST\')
    
    if 'error' in result:
        print(f'❌ Error: {result["error"]}')
        print(f'Status: {result.get("status", "unknown")}')
    else:
        print('✅ Setup engine ran successfully!')
        print(f'Top setups generated: {len(result.get("top_setups", []))}')
        
        # Basic structure validation
        expected_keys = ['ticker', 'timeframe', 'regime_model', 'strategy_count']
        for key in expected_keys:
            if key in result:
                print(f'  ✅ {key}: {result[key]}')
            else:
                print(f'  ❌ Missing: {key}')
        
        # Show regime summary
        if 'regime_summary' in result:
            print(f'  ✅ Regime Summary: {dict(result["regime_summary"])}')
        
        # Show a sample setup if available
        if result.get('top_setups') and len(result['top_setups']) > 0:
            setup = result['top_setups'][0]
            print(f'  ✅ Sample Setup: {setup.get("name")} - Score: {setup.get("score", 0):.3f}')
            
    print('\n=== Test Complete ===')
    
except Exception as e:
    print(f'❌ Exception in setup_engine: {str(e)}')
    import traceback
    traceback.print_exc()
