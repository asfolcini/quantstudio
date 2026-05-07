"""Regime detection module."""

import pandas as pd
import numpy as np


def detect_regimes(df: pd.DataFrame):
    """Detect market regimes."""
    close = df['close']
    ma_20 = calculate_ma(close, 20)
    ma_50 = calculate_ma(close, 50)
    vol_20 = calculate_rolling_volatility(close, 20)
    
    regimes = []
    
    for i in range(len(df)):
        if i < 50:
            regimes.append("INSUFFICIENT_DATA")
            continue
            
        # Trend slope
        trend_ma_slope_20 = ma_20.iloc[i] - ma_20.iloc[i-1]
        trend_ma_slope_50 = ma_50.iloc[i] - ma_50.iloc[i-1]
        
        # Trend classification
        if trend_ma_slope_20 > 0 and trend_ma_slope_50 > 0:
            trend = "UP"
        elif trend_ma_slope_20 < 0 and trend_ma_slope_50 < 0:
            trend = "DOWN"
        else:
            trend = "FLAT"
            
        # Volatility classification with safe handling
        # Extract quantiles as scalars and handle empty slices
        try:
            if len(vol_20.iloc[i-50:i]) > 0:
                quantile_75 = vol_20.iloc[i-50:i].quantile(0.75).item()
                quantile_25 = vol_20.iloc[i-50:i].quantile(0.25).item()
                if vol_20.iloc[i] > quantile_75:
                    volatility = "HIGH"
                elif vol_20.iloc[i] < quantile_25:
                    volatility = "LOW"
                else:
                    volatility = "NORMAL"
            else:
                volatility = "NORMAL"
        except (ValueError, AttributeError):
            volatility = "NORMAL"
            
        # Composite regime
        if trend == "UP" and volatility != "HIGH":
            regime = "TRENDING_UP"
        elif trend == "DOWN" and volatility != "HIGH":
            regime = "TRENDING_DOWN"
        elif trend == "FLAT" and volatility == "NORMAL":
            regime = "RANGE"
        elif volatility == "HIGH":
            regime = "HIGH_VOLATILITY"
        else:
            regime = "LOW_VOLATILITY"
            
        regimes.append(regime)
        
    return pd.Series(regimes, index=df.index)


def get_regime_features(df: pd.DataFrame):
    """Get all regime features."""
    composite_regimes = detect_regimes(df)
    
    # Extract components
    trend_features = []
    volatility_features = []
    
    for regime in composite_regimes:
        if regime == "TRENDING_UP":
            trend_features.append("UP")
            volatility_features.append("LOW")
        elif regime == "TRENDING_DOWN":
            trend_features.append("DOWN")
            volatility_features.append("LOW")
        elif regime == "RANGE":
            trend_features.append("FLAT")
            volatility_features.append("NORMAL")
        else:
            trend_features.append("FLAT")
            volatility_features.append("LOW")
    
    return {
        'trend': pd.Series(trend_features, index=df.index),
        'volatility': pd.Series(volatility_features, index=df.index),
        'composite': composite_regimes
    }


# Helper functions
def calculate_ma(series: pd.Series, window: int):
    return series.shift(1).rolling(window).mean()


def calculate_rolling_volatility(series: pd.Series, window: int):
    return series.shift(1).rolling(window).std()
