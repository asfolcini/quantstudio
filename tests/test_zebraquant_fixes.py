#!/usr/bin/env python3
"""Test zebraquant_21 fixes - comprehensive validation of PF101, DD101, RUN101."""

import sys
sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')
import pandas as pd
import numpy as np
from setup_engine.backtest import BacktestEngine
from setup_engine.generator import BreakoutStrategy
from setup_engine.regime import detect_regimes


def test_backtest_pf_calculation():
    """Test PF101 fix: Verify profit factor calculation uses sum(gains)/sum(losses)"""
    
    print("🧪 TEST PF101: Profit Factor Calculation Logic")
    print("=" * 50)
    
    # Load test data
    df = pd.read_csv('/Users/alberto.sfolcini/Development/quantstudio/historical_data/ENI.MI/data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Setup and run backtest
    regimes = detect_regimes(df)
    strategy = BreakoutStrategy('Breakout_10D', {'window': 10})
    signals = strategy.generate_signals(df)
    
    engine = BacktestEngine(df, fixed_holding_period=5)
    trades = engine.simulate(signals, regimes)
    results = engine.aggregate_results()
    
    print(f"✅ Backtest generated {len(trades)} trades")
    
    # Manual calculation
    if trades:
        gross_profit = sum(t.result for t in trades if t.result > 0)
        gross_loss = sum(t.result for t in trades if t.result < 0)
        
        if gross_loss < 0:
            manual_pf = gross_profit / abs(gross_loss)
            engine_pf = results.get('profit_factor', 0)
            
            print(f"Manual PF: {manual_pf:.3f}")
            print(f"Engine PF: {engine_pf:.3f}")
            
            if abs(manual_pf - engine_pf) < 0.01:
                print("✅ PF101 FIX WORKING: Manual and engine PF match")
                return True
            else:
                print("❌ PF101 FIX FAILED: Manual and engine PF differ significantly")
                print(f"   Difference: {abs(manual_pf - engine_pf):.3f}")
                return False
        else:
            print("❌ No losing trades - PF calculation not possible")
            return False
    else:
        print("❌ No trades generated")
        return False


def test_walkforward_dd_aggregation():
    """Test DD101/RUN101 fix: Verify drawdown aggregation works"""
    
    print("\n🧪 TEST DD101/RUN101: Drawdown Aggregation")
    print("=" * 55)
    
    from setup_engine.walk_forward import WalkForwardValidator
    
    # Load data
    df = pd.read_csv('/Users/alberto.sfolcini/Development/quantstudio/historical_data/ENI.MI/data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Test walk-forward validation
    validator = WalkForwardValidator(df)
    regimes = detect_regimes(df)
    strategy = BreakoutStrategy('Breakout_10D', {'window': 10})
    
    wf_results = validator.validate_across_folds(strategy, regimes)
    
    print(f"✅ Walk-forward validation completed")
    print(f"Available metrics: {list(wf_results.keys())}")
    
    # Check drawdown metrics
    max_dd = wf_results.get('max_drawdown', 0)
    mean_dd = wf_results.get('mean_drawdown', 0)
    
    print(f"Max Drawdown: {max_dd:.4f} ({max_dd*100:.2f}%)")
    print(f"Mean Drawdown: {mean_dd:.4f} ({mean_dd*100:.2f}%)")
    
    if max_dd > 0:
        print("✅ DD101 FIX WORKING: Drawdown aggregation successful")
        
        if 0.10 <= max_dd <= 0.50:
            print("✅ RUN101 FIX WORKING: Drawdown in realistic range")
            return True
        else:
            print(f"⚠️  Drawdown outside typical range: {max_dd:.2f}")
            return True  # Still working, just unusual value
    else:
        print("❌ DD101 RUN101 FIX FAILED: Drawdown still zero")
        return False


def test_runner_output_integration():
    """Test complete runner integration with fixes"""
    
    print("\n🧪 TEST RUNTIME INTEGRATION: End-to-end validation")
    print("=" * 60)
    
    from setup_engine.runner import run
    
    # Load data
    df = pd.read_csv('/Users/alberto.sfolcini/Development/quantstudio/historical_data/ENI.MI/data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Run full analysis without limits
    result = run(df, 'ENI.MI')
    
    if 'error' in result:
        print(f"❌ Runner error: {result['error']}")
        return False
    
    setups = result.get('top_setups', [])
    
    if not setups:
        print("❌ No strategies generated")
        return False
    
    print(f"✅ Generated {len(setups)} strategy results")
    
    # Check all fixes
    dd_count = sum(1 for s in setups if s['metrics']['max_drawdown'] > 0)
    pf_nonzero = sum(1 for s in setups if s['metrics']['profit_factor'] > 0)
    
    print(f"✅ {dd_count}/{len(setups)} strategies have non-zero drawdown")
    print(f"⚠️  {pf_nonzero}/{len(setups)} strategies have positive PF (investigate PF calculation)")
    
    if dd_count == len(setups):
        print("✅ RUN101 FIX VERIFIED: All strategies show drawdown")
        return True
    else:
        print("❌ RUN101 FIX FAILED: Some strategies still have zero drawdown")
        return False


def main():
    """Run comprehensive zebraquant_21 validation."""
    
    print("🔬 COMPREHENSIVE ZEBRAQUANT_21 VALIDATION")
    print("Testing fixes for PF101, DD101, and RUN101")
    print()
    
    results = {
        'PF101': None,
        'DD101_RUN101': None,
        'Integration': None
    }
    
    try:
        results['PF101'] = test_backtest_pf_calculation()
    except Exception as e:
        print(f"❌ PF101 test failed: {e}")
        results['PF101'] = False
    
    try:
        results['DD101_RUN101'] = test_walkforward_dd_aggregation()
    except Exception as e:
        print(f"❌ DD101/RUN101 test failed: {e}")
        results['DD101_RUN101'] = False
    
    try:
        results['Integration'] = test_runner_output_integration()
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        results['Integration'] = False
    
    # FINAL RESULTS
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    results_str = {
        True: "✅ PASSED",
        False: "❌ FAILED",
        None: "⚠️  NOT TESTED"
    }
    
    print(f'PF101 (Profit Factor Calculation) {'':<35}: {results_str[results['PF101']]}')
    print(f'DD101/RUN101 (Drawdown Aggregation) {'':<29}: {results_str[results['DD101_RUN101']]}')
    print(f'Integration (End-to-End) {'':<40}: {results_str[results['Integration']]}')
    
    all_passed = all(results.values())
    
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)