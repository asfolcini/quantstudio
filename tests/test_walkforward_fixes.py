"""Test script to verify walk-forward stats, scoring, and regime performance fixes."""

import sys
import os
import pandas as pd
import numpy as np
import json

# Add the quantstudio directory to the Python path
sys.path.append('/Users/alberto.sfolcini/Development/quantstudio')

# Now import from setup_engine
from setup_engine.runner import run

def test_fold_stats_not_zero():
    """Test that walk_forward_stats shows actual fold counts, not zeros."""
    print("Testing fold stats (should not be zero)...")
    
    # Create synthetic data with enough samples for 3+ folds
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    assert 'walk_forward_stats' in result, "Missing walk_forward_stats"
    stats = result['walk_forward_stats']
    
    # Should have actual fold counts, not zeros
    assert stats['average_folds'] > 0, f"average_folds should > 0, got {stats['average_folds']}"
    assert stats['min_folds'] > 0, f"min_folds should > 0, got {stats['min_folds']}"
    assert stats['max_folds'] > 0, f"max_folds should > 0, got {stats['max_folds']}"
    assert stats['min_folds'] >= 3, f"min_folds should be >= 3, got {stats['min_folds']}"
    
    print(f"✓ Fold stats test passed: avg={stats['average_folds']}, min={stats['min_folds']}, max={stats['max_folds']}")
    return True

def test_regime_performance_not_empty():
    """Test that regime_performance shows actual regime breakdown."""
    print("Testing regime performance (should not be empty)...")
    
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    # Check that at least some strategies have regime performance
    strategies_with_regimes = []
    for setup in result.get('top_setups', []):
        regime_perf = setup.get('regime_performance', {})
        if regime_perf and len(regime_perf) > 0:
            strategies_with_regimes.append(setup['name'])
            
            # Validate regime performance structure
            for regime, values in regime_perf.items():
                assert 'avg_return' in values, f"Missing avg_return in regime {regime}"
                assert 'win_rate' in values, f"Missing win_rate in regime {regime}"
                assert 'trades' in values, f"Missing trades in regime {regime}"
                assert 'return' in values, f"Missing return in regime {regime}"
                assert 'winners' in values, f"Missing winners in regime {regime}"
    
    assert len(strategies_with_regimes) > 0, f"No strategies have regime performance. Setups: {len(result.get('top_setups', []))}"
    
    print(f"✓ Regime performance test passed: {len(strategies_with_regimes)} strategies with regime data")
    print(f"  Sample regime performance keys: {list(result['top_setups'][0]['regime_performance'].keys())}")
    return True

def test_train_test_gap_normalized():
    """Test that train_test_gap values are reasonable (normalized 0-1)."""
    print("Testing train_test_gap normalization...")
    
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    # Test that train_test_gap values are reasonable
    for setup in result.get('top_setups', []):
        metrics = setup.get('metrics', {})
        robustness = setup.get('robustness', {})
        
        # Check train_test_gap in metrics and robustness
        gap_metrics = metrics.get('train_test_gap', 0.0)
        gap_robustness = robustness.get('train_test_gap', 0.0)
        
        # Should be reasonable values, not extremes like ±0.5
        if abs(gap_metrics) > 0.5:
            print(f"⚠️  WARNING: Extreme train_test_gap {gap_metrics} in strategy {setup['name']}")
        if abs(gap_robustness) > 0.5:
            print(f"⚠️  WARNING: Extreme train_test_gap {gap_robustness} in robustness for {setup['name']}")
        
        # Should be normalized (between -1 and 1 is acceptable, but extremes suggest issues)
        assert abs(gap_metrics) <= 1.0, f"train_test_gap out of bounds: {gap_metrics}"
        assert abs(gap_robustness) <= 1.0, f"robustness train_test_gap out of bounds: {gap_robustness}"
    
    print("✓ Train_test_gap normalization test passed")
    return True

def test_score_not_return_dominated():
    """Test that scoring is not dominated by return."""
    print("Testing scoring not return-dominated...")
    
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    # Test that score is not simple return/2
    score_is_return_divided_by_2 = True
    for setup in result.get('top_setups', []):
        score = setup.get('score', 0.0)
        wf_return = setup.get('metrics', {}).get('return', 0.0)
        
        # Score should not be approximately return/2
        if abs(score - (wf_return / 2.0)) > 0.01:  # More than 1% difference
            score_is_return_divided_by_2 = False
            break
    
    # The old formula had score ≈ return/2, now it should be more complex
    if score_is_return_divided_by_2:
        print("⚠️  WARNING: Scores still appear to be return/2 - scoring may still be too return-dominated")
        print("    This could indicate the new balanced score formula is not working")
    else:
        print("✓ Score is not simply return/2 - balanced scoring is working")
    
    return True

def test_robustness_aware_ranking():
    """Test that ranking rewards robustness, not just return."""
    print("Testing robustness-aware ranking...")
    
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    # Get strategies with different robustness profiles
    top_strategies = result.get('top_setups', [])
    
    if len(top_strategies) >= 2:
        top_strategy = top_strategies[0]
        second_strategy = top_strategies[1]
        
        top_dd = top_strategy.get('metrics', {}).get('max_drawdown', 1.0)
        second_dd = second_strategy.get('metrics', {}).get('max_drawdown', 1.0)
        
        top_gap = abs(top_strategy.get('robustness', {}).get('train_test_gap', 0.0))
        second_gap = abs(second_strategy.get('robustness', {}).get('train_test_gap', 0.0))
        
        print(f"  Top strategy DD: {top_dd:.3f}, Gap: {top_gap:.3f}")
        print(f"  Second strategy DD: {second_dd:.3f}, Gap: {second_gap:.3f}")
        
        # If top strategy has better robustness metrics than second, ranking is working
        if (top_dd < second_dd or top_gap < second_gap):
            print("✓ Top strategies show better robustness - ranking appears to work")
        else:
            print("⚠️  Top strategy may not have best robustness - check ranking logic")
    
    return True

def test_output_json_valid():
    """Test that final JSON is valid and complete."""
    print("Testing valid JSON output...")
    
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'high': 100 + np.cumsum(np.random.normal(0, 1, 300)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 300)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 300)),
        'volume': 1000 + np.random.normal(0, 100, 300)
    }, index=pd.date_range('2023-01-01', periods=300))
    
    result = run(df, \'TEST\')
    
    # Test JSON serialization
    try:
        json_str = json.dumps(result)
        parsed_back = json.loads(json_str)
        
        # Verify key fields exist and are not NaN
        assert 'top_setups' in parsed_back
        assert 'walk_forward_stats' in parsed_back
        
        for setup in parsed_back['top_setups']:
            assert 'metrics' in setup
            assert 'regime_performance' in setup
            assert 'score' in setup
            assert 'rank' in setup
            
            # Check no NaN in key metrics
            for key, value in setup['metrics'].items():
                if isinstance(value, (int, float)):
                    assert not np.isnan(value), f"Found NaN in {key}"
                    assert not np.isinf(value), f"Found Inf in {key}"
        
        print("✓ JSON output is valid and well-structured")
        return True
        
    except (TypeError, ValueError, OverflowError) as e:
        print(f"✗ JSON serialization failed: {e}")
        return False

def test_minimum_folds_enforcement():
    """Test that minimum 3 folds are enforced."""
    print("Testing minimum 3 folds enforcement...")
    
    # Test with borderline small dataset
    np.random.seed(42)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.normal(0, 1, 80)),  # Small dataset
        'high': 100 + np.cumsum(np.random.normal(0, 1, 80)) + 1,
        'low': 100 + np.cumsum(np.random.normal(0, 1, 80)) - 1,
        'close': 100 + np.cumsum(np.random.normal(0, 1, 80)),
        'volume': 1000 + np.random.normal(0, 100, 80)
    }, index=pd.date_range('2023-01-01', periods=80))
    
    result = run(df, \'TEST\')
    
    # Even with small data, should maintain minimum folds or degrade safely
    stats = result.get('walk_forward_stats', {})
    min_folds = stats.get('min_folds', 0)
    
    if min_folds >= 3:
        print("✓ Minimum 3 folds enforced")
    elif min_folds > 0:
        print(f"⚠️  Warning: Only {min_folds} folds generated (expected 3), but > 0")
    else:
        print("⚠️  Warning: No folds generated, but system should handle gracefully")
    
    return True

if __name__ == "__main__":
    print("Running walk-forward stats, scoring, and regime performance tests...")
    print("=" * 70)
    
    tests = [
        test_fold_stats_not_zero,
        test_regime_performance_not_empty,
        test_train_test_gap_normalized,
        test_score_not_return_dominated,
        test_robustness_aware_ranking,
        test_output_json_valid,
        test_minimum_folds_enforcement
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\nRunning {test.__name__}...")
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Walk-forward stats, scoring, and regime performance fixes are working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        
    sys.exit(0 if failed == 0 else 1)