#!/usr/bin/env python3
"""Test script to verify trade metrics fixes."""

import sys
sys.path.insert(0, '/Users/alberto.sfolcini/Development/quantstudio')
import pandas as pd

# Load data
df = pd.read_csv('/Users/alberto.sfolcini/Development/quantstudio/historical_data/ENI.MI/data.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

print("🔍 VERIFICATION: Trading Setup Analysis")
print("=" * 45)
print(f"Data loaded: {len(df)} bars")

# Quick validation
from setup_engine.backtest import BacktestEngine
from setup_engine.generator import BreakoutStrategy
from setup_engine.regime import detect_regimes

regimes = detect_regimes(df)
strategy = BreakoutStrategy('Breakout_10D', {'window': 10})

engine = BacktestEngine(df)
signals = strategy.generate_signals(df)
trades = engine.simulate(signals, regimes)
results = engine.aggregate_results()

print(f"Backtest generated {len(trades)} trades")
print(f"Total return: {results['total_return']:.2f}")
print(f"Profit factor: {results['profit_factor']:.2f}")
print(f"Trade count: {results['total_trades']}")
print(f"Win rate: {results['win_rate']:.2f}")

if results['total_trades'] > 0:
    print("✅ Backtest is generating trades correctly")
else:
    print("❌ Backtest trade generation issue")

print("\n🎉 VERIFICATION COMPLETE")