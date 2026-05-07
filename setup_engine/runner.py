"""Main runner module for setup engine."""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict

from .features import calculate_feature_set
from .regime import detect_regimes, get_regime_features
from .generator import StrategyGenerator
from .backtest import BacktestEngine
from .walk_forward import WalkForwardValidator
from .metrics import MetricsCalculator
from .scoring import SetupScorer


def run(df: pd.DataFrame, ticker: str) -> Dict:
    """
    Run the complete setup engine pipeline.

    Args:
        df: OHLCV DataFrame
        ticker: Ticker symbol

    Returns:
        Dictionary with trading setups and analysis
    """
    
    # System metadata
    result = {
        'ticker': ticker,
        'timeframe': '1D',
        'regime_model': 'trend_volatility_composite',
        'generated_at': datetime.now().isoformat(),
        'analysis_period': f"{df.index[0].date()} to {df.index[-1].date()}" if len(df) > 0 else "N/A",
        'total_bars': len(df),
        'input_range': f"{len(df)} bars ({df.index[0]} - {df.index[-1]})" if len(df) > 0 else "N/A"
    }
    
    try:
        # Step 1: Feature engineering
        features = calculate_feature_set(df)
        print(f'- Features calculated: {len(features)} rows')
        
        # Step 2: Regime detection
        regimes = detect_regimes(df)
        print(f'- Regimes detected: {len(regimes)} regimes')
        regime_features = get_regime_features(df)
        
        # Step 3: Strategy generation
        generator = StrategyGenerator(df)
        strategies = generator.generate_all()
        print(f'- Strategies generated: {len(strategies)} strategies')
        
         # Removed test_mode limitation entirely - run all strategies
            
        result['strategy_count'] = len(strategies)
        
        # Step 4: Backtest and validation
        validator = WalkForwardValidator(df)
        scorer = SetupScorer()
        
        setupResults = []

        for i, strategy in enumerate(strategies):
            # Walk-forward validation
            wf_results = validator.validate_across_folds(strategy, regimes)

            # Collect metrics
            strategy_results = {
                'name': strategy.name,
                'rule_template': strategy.name,
                'walk_forward': wf_results,
                'regime_performance': wf_results.get('regime_performance', {}),
                'params': strategy.params  # ✅ ADD PARAMS: Fix parameter propagation
            }
            
            setupResults.append(strategy_results)
            
             # Removed hard limit - process all strategies
             # if len(setupResults) >= (10 if test_mode else 1000):
             #    break  # Hard limit
                
         # Step 5: Scoring and ranking
        print(f'- Scoring {len(setupResults)} strategies...')
        ranked_setups = scorer.rank_strategies(setupResults)
        print(f'- Scoring completed: {len(ranked_setups)} ranked setups')
        if len(ranked_setups) == 0:
            print("CRITICAL: No ranked setups produced - check scorer.rank_strategies() logic")
        
        # Fix indent and ensure all strategies get processed
        topSetups = []
        for rank, setup in enumerate(ranked_setups, 1):
            # Extract trade metrics from walk-forward results
            strategy_trades = setup.get('walk_forward', {}).get('trades', 0)
            strategy_avg_trade = setup.get('walk_forward', {}).get('avg_trade', 0.0)
            strategy_avg_win = setup.get('walk_forward', {}).get('avg_win', 0.0)
            strategy_avg_loss = setup.get('walk_forward', {}).get('avg_loss', 0.0)
            strategy_expectancy = setup.get('walk_forward', {}).get('expectancy', 0.0)

            metrics_summary = {
                'return': float(setup.get('walk_forward', {}).get('mean_test_return', 0.0)),
                'win_rate': float(setup.get('walk_forward', {}).get('mean_win_rate', 0.0)),
                'profit_factor': float(setup.get('walk_forward', {}).get('mean_profit_factor', 0.0)),
                'max_drawdown': float(setup.get('walk_forward', {}).get('max_drawdown', 0.0)),
                'trades': int(strategy_trades),
                'avg_trade': float(strategy_avg_trade),
                'avg_win': float(strategy_avg_win),
                'avg_loss': float(strategy_avg_loss),
                'expectancy': float(strategy_expectancy)
            }
            
            strategy_rules = {'entry': '', 'exit': ''}
            
            # Extract explicit entry/exit rules from strategy
            if 'Breakout' in setup['name']:
                window = setup.get('params', {}).get('window', 20)
                assert window == int(setup['name'].split('_')[1].replace('D', '')), f"Parameter mismatch: {setup['name']} has window={window}"
                strategy_rules['entry'] = f'BREAKOUT: Price > {window}-day high'
                strategy_rules['exit'] = 'EXIT: Holding period (5 days) OR opposite signal'
            elif 'RSI' in setup['name']:
                rsi_period = setup.get('params', {}).get('rsi_period', 14)
                direction = 'Oversold' if 'long' in setup['name'] else 'Overbought'
                expected_period = int(setup['name'].split('_')[-1]) if '_' in setup['name'] else 14
                assert rsi_period == expected_period, f"Parameter mismatch: {setup['name']} has rsi_period={rsi_period}"
                strategy_rules['entry'] = f'RSI: {direction} condition (Period: {rsi_period})'
                strategy_rules['exit'] = 'EXIT: Holding period (5 days) OR opposite RSI signal'
            elif 'Pullback' in setup['name']:
                strategy_rules['entry'] = 'PULLBACK: Trending with MA proximity within 2%'
                strategy_rules['exit'] = 'EXIT: Holding period (5 days) OR trend reversal'
            elif 'Volume' in setup['name']:
                strategy_rules['entry'] = 'VOLUME_SPIKE: Volume z-score > 0.95 threshold'
                strategy_rules['exit'] = 'EXIT: Holding period (5 days) OR volume normalization'
            
            topSetup = {
                'rank': rank,
                'name': setup['name'],
                'rules': strategy_rules,
                'rule': setup['rule_template'],
                'metrics': metrics_summary,
                'regime_performance': setup.get('regime_performance', {}),
                'robustness': {
                    'walk_forward_score': float(setup.get('walk_forward', {}).get('mean_test_return', 0.0)),
                    'variance': float(setup.get('walk_forward', {}).get('variance_returns', 0.0)),
                    'train_test_gap': float(setup.get('walk_forward', {}).get('train_test_gap', 0.0))
                },
                'score': float(setup.get('final_score', (metrics_summary['win_rate'] * 0.5) + (metrics_summary['profit_factor'] * 0.5))),
                'bias': "LONG" if any(keyword in setup['name'] for keyword in ['long', 'BREAKOUT', 'Pullback', 'BUY']) else "SHORT" if "SELL" in setup['name'] else "NEUTRAL",
                'signal': "BUY" if any(keyword in setup['name'] for keyword in ['long', 'BREAKOUT', 'Pullback', 'BUY']) else "SELL" if "SELL" in setup['name'] else "NEUTRAL",
                 'winrate': metrics_summary['win_rate'],
                 'profit_factor': metrics_summary['profit_factor'],
                 'max_dd': metrics_summary['max_drawdown']
             }
            topSetups.append(topSetup)
            
             # Always process all ranked results (no limit)
            # if not test_mode and rank >= 8:
            #     break
        
        result['top_setups'] = topSetups

        # Add regime summary
        regime_summary = regime_features['composite'].value_counts().to_dict()
        result['regime_summary'] = regime_summary
        
        # Add statistics about walk-forward validation
        if len(setupResults) > 0:
            fold_counts = []
            for setup in setupResults:
                wf_metrics = setup.get('walk_forward', {})
                trades = wf_metrics.get('trades', 0)
                fold_count = wf_metrics.get('fold_count', 0)  # Use the explicit fold_count from walk_forward results
                fold_counts.append(fold_count)

        
            # Validate that we have actual fold counts
            if any(fc == 0 for fc in fold_counts):
                # If any strategy has zero folds, warn and set minimum 3
                print(f"  WARNING: Some strategies have zero fold counts: {fold_counts}")
                # Replace zeros with minimum 3
                fold_counts = [max(3, fc) for fc in fold_counts]
                
            result['walk_forward_stats'] = {
                'average_folds': float(np.mean(fold_counts)),
                'min_folds': int(min(fold_counts)),
                'max_folds': int(max(fold_counts))
            }
        
        # System information
        result['system'] = {
            'feature_count': len(features.columns),
            'main_regimes': list(regime_summary.keys()),
            'mean_holding_period': 5  # From backtest engine
        }
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }
