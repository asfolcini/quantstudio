"""
regime_aware_ranking.py

Usage:
  python regime_aware_ranking.py <input_json_path_or_string>

Example input JSON:
```python
{
  "ticker": "BTCUSD",
  "timeframe": "4h",
  "strategies": [
    {
      "name": "Breakout",
      "metrics": {
        "return": 18.3,
        "profit_factor": 1.75,
        "max_drawdown": 0.09,
        "variance": 0.018,
        "n_trades": 112
      }
    },
    {
      "name": "MeanReversal",
      "metrics": {
        "return": 8.1,
        "profit_factor": 1.15,
        "max_drawdown": 0.22,
        "variance": 0.075,
        "n_trades": 65
      }
    }
  ],
  "regime_breakdowns": {
    "Breakout": {"TRENDING_UP":20.1, "LOW_VOLATILITY":16.8, "HIGH_VOLATILITY":14.3, "RANGE":15.2},
    "MeanReversal": {"TRENDING_UP":6.2, "LOW_VOLATILITY":9.5, "HIGH_VOLATILITY":2.3, "RANGE":10.8}
  }
}
```

Output format as specified:
- rank, name, final_score, key_metrics, regime_strengths, regime_weaknesses, short_rationale

Composite scoring is deterministic and stateless.
"""
