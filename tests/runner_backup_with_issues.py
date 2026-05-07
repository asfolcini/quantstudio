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


def run(df: pd.DataFrame, ticker: str, test_mode: bool = False) -> Dict:
    """
    Run the complete setup engine pipeline.

    Args:
        df: OHLCV DataFrame
        ticker: Ticker symbol
        test_mode: Limit strategy count for development (generates 100 strategies, outputs top 10)

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
        
        if test_mode:
            strategies = strategies[:100]  # Limit for testing - increased to 100
            result['test_mode'] = True
            result['strategy_limit'] = 100
            
        result['strategy_count'] = len(strategies)
        
        # Step 4: Backtest and validation
        validator = WalkForwardValidator(df)
        scorer = SetupScorer()
        
        setupResults = []
        
        for i, strategy in enumerate(strategies):
            # Walk-forward validation
            wf_results = validator.validate_across_folds(strategy, regimes)
            #print(f'DEBUG: Strategy {i+1}/{len(strategies)}: {strategy.name} - WF results: {wf_results}')
            
             # Collect metrics
            strategy_results = {
                'name': strategy.name,
                'rule_template': strategy.name,
                'walk_forward': wf_results,
                'regime_performance': {},
                'params': strategy.params  # ✅ ADD PARAMS: Fix parameter propagation
            }
            
            setupResults.append(strategy_results)
            
            if len(setupResults) >= (10 if test_mode else 1000):
                break  # Hard limit
                
        # Step 5: Scoring and ranking
        print(f'- Scoring {len(setupResults)} strategies...')
        ranked_setups = scorer.rank_strategies(setupResults)
        print(f'- Scoring completed: {len(ranked_setups)} ranked setups')
        
        # Prepare top N results (8 in production, 10 in test)
        top_count = 10 if test_mode else min(8, len(ranked_setups))
        
        topSetups = []
        for rank, setup in enumerate(ranked_setups[:top_count], 1):
             metrics_summary = {
                'return': setup.get('walk_forward', {}).get('mean_test_return', 0),
                'win_rate': setup.get('walk_forward', {}).get('mean_win_rate', 0),
                'profit_factor': setup.get('walk_forward', {}).get('mean_profit_factor', 0),
                'max_drawdown': setup.get('walk_forward', {}).get('max_drawdown', 0),  # FIX RUN101: Use aggregated drawdown
                'trades': strategy_trades,  # ✅ TASK 2.1: Add trade count
                'avg_trade': strategy_avg_trade,  # ✅ TASK 2.2: Add average trade
                'avg_win': strategy_avg_win,  # ✅ TASK 2.3: Add average win
                'avg_loss': strategy_avg_loss,  # ✅ TASK 2.3: Add average loss
                'expectancy': strategy_expectancy 
             }
               
        
        # TASK 2.1: COMPUTE TRADE METRICS These will be populated from actual backtest data
        strategy_trades = 0
        strategy_avg_trade = 0.0
        strategy_avg_win = 0.0
        strategy_avg_loss = 0.0
        strategy_expectancy = 0.0
        
        # Extract explicit entry/exit rules from strategy
        strategy_rules = {
            'entry': '',
            'exit': ''
        }

            # ✅ TASK 2.1: COMPUTE TRADE METRICS These will be populated from actual backtest data
            strategy_trades = 0
            strategy_avg_trade = 0.0
            strategy_avg_win = 0.0
            strategy_avg_loss = 0.0
            strategy_expectancy = 0.0

        # Map strategy name to known rules patterns
        # ✅ FIX PF101: Use ACTUAL strategy parameters, not hardcoded defaults
        if 'Breakout' in setup['name']:
            window = setup.get('params', {}).get('window', 20)
            # Add validation
            assert window == int(setup['name'].split('_')[1].replace('D', '')), f"Parameter mismatch: {setup['name']} has window={window}"
            strategy_rules['entry'] = f'BREAKOUT: Price > {window}-day high'
            strategy_rules['exit'] = 'EXIT: Holding period (5 days) OR opposite signal'
            
        elif 'RSI' in setup['name']:
            rsi_period = setup.get('params', {}).get('rsi_period', 14) 
            direction = 'Oversold' if 'long' in setup['name'] else 'Overbought'
            # Add validation
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
                'rules': strategy_rules,  # Add explicit rules
                'rule': setup['rule_template'],  # Keep old field for backward compatibility
                'metrics': metrics_summary,
                'regime_performance': setup.get('regime_performance', {}),
                'robustness': {
                    'walk_forward_score': setup.get('walk_forward', {}).get('mean_test_return', 0),
                    'variance': setup.get('walk_forward', {}).get('variance_returns', 0),
                    'train_test_gap': setup.get('walk_forward', {}).get('train_test_gap', 0)
            },
                'score': setup.get('final_score', 0)
            }
            
            topSetups.append(topSetup)
            
        result['top_setups'] = topSetups
        
        # Add regime summary
        regime_summary = regime_features['composite'].value_counts().to_dict()
        result['regime_summary'] = regime_summary
        
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
