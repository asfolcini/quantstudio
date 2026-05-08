import pandas as pd
import numpy as np
import json
import requests
import os


class EdgeEngine:
    """
    Statistical Edge Engine for OHLCV data.
    Computes bidirectional trading edge (LONG and SHORT) using deterministic statistical methods.
    
    Architecture:
    1. Data validation
    2. Technical indicators
    3. Market regime detection
    4. Structural level analysis
    5. Feature engineering (LONG/SHORT)
    6. Edge score computation
    7. Decision engine
    8. Report generation
    """
    
    def __init__(self, df):
        """
        Initialize EdgeEngine with OHLCV dataframe.
        
        Required columns: datetime, open, high, low, close, volume
        """
        self.original_df = df.copy()
        self.df = df.copy()
        self.validate_data()
        
        # Initialize data structures
        self.indicators = {}
        self.market_regime = {}
        self.levels = {}
        self.long_features = {}
        self.short_features = {}
        self.edge_scores = {}
        self.decision = {}
        self.llm_interpretation = None
        
        # Load configuration
        self._load_config()
    
    def generate_quantitative_report(self):
        """Generate only the quantitative table report (backward compatible)."""
        # Ensure all components have been computed
        if not self.indicators:
            self.compute_indicators()
        if not self.market_regime:
            self.compute_market_regime()
        if not self.levels:
            self.compute_levels()
        if not self.long_features:
            self.compute_long_features()
        if not self.short_features:
            self.compute_short_features()
        if not self.edge_scores:
            self.compute_edge_scores()
        if not self.decision:
            self.compute_decision()
        
        # Get current values for report
        indicators_report = {
            'ema20': round(self.indicators['ema20'].iloc[-1], 2),
            'ema50': round(self.indicators['ema50'].iloc[-1], 2),
            'ema200': round(self.indicators['ema200'].iloc[-1], 2),
            'rsi': round(self.indicators['rsi'].iloc[-1], 2),
            'atr': round(self.indicators['atr'].iloc[-1], 2),
            'vwap': round(self.indicators['vwap'].iloc[-1], 2),
            'bb_bandwidth': round((self.indicators['bb_upper'].iloc[-1] - self.indicators['bb_lower'].iloc[-1]) / self.indicators['bb_middle'].iloc[-1] * 100, 2) if self.indicators['bb_middle'].iloc[-1] != 0 else 0
        }
        
        # Return original quantitative report structure
        return {
            'market_regime': {
                'trend': self.market_regime['trend'],
                'volatility': self.market_regime['volatility'],
                'atr': self.market_regime.get('atr', 0)
            },
            'indicators': indicators_report,
            'levels': {
                's1': round(self.levels['s1'], 2),
                's2': round(self.levels['s2'], 2),
                'r1': round(self.levels['r1'], 2),
                'r2': round(self.levels['r2'], 2),
                'vwap': round(self.levels['vwap_proximity'], 2)
            },
            'edge': {
                'long_score': self.edge_scores['long_score'],
                'short_score': self.edge_scores['short_score'],
                'risk_penalty': self.edge_scores['risk_penalty']
            },
            'decision': {
                'bias': self.decision['bias'],
                'confidence': self.decision['confidence']
            }
        }
    
    def _load_config(self):
        """Load configuration from config/config.json."""
        # Get the absolute path to the project root
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        config_path = os.path.join(project_root, 'config', 'config.json')
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Set defaults if config file exists but has missing fields
            self.llm_config = {
                'api_url': config.get('llm', {}).get('api_url', ''),
                'api_key': config.get('llm', {}).get('api_key', ''),
                'model': 'auto'
            }
            self.report_language = config.get('report_language', 'english')
            
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback defaults if config file missing/invalid
            self.llm_config = {
                'api_url': '',
                'api_key': '',
                'model': 'auto'
            }
            self.report_language = 'english'
    
    def _generate_llm_interpretation(self):
        """Generate human-readable interpretation via LLM API."""
        # Skip if LLM is not configured
        if not self.llm_config['api_url'] or not self.llm_config['api_key']:
            return None
        
        try:
            # Ensure all computations are done first
            quantitative_report = self.generate_quantitative_report()
            
            # Prepare the JSON data for LLM from the quantitative report
            report_data = {
                'market_regime': {
                    'trend': quantitative_report['market_regime'].get('trend'),
                    'volatility': quantitative_report['market_regime'].get('volatility'),
                    'atr': quantitative_report['indicators'].get('atr')
                },
                'indicators': {
                    'ema20': quantitative_report['indicators']['ema20'],
                    'ema50': quantitative_report['indicators']['ema50'],
                    'rsi': quantitative_report['indicators']['rsi']
                },
                'edge_scores': {
                    'long_score': quantitative_report['edge']['long_score'],
                    'short_score': quantitative_report['edge']['short_score'],
                    'risk_penalty': quantitative_report['edge']['risk_penalty']
                },
                'levels': {
                    's1': quantitative_report['levels']['s1'],
                    's2': quantitative_report['levels']['s2'],
                    'r1': quantitative_report['levels']['r1'],
                    'r2': quantitative_report['levels']['r2']
                },
                'decision': {
                    'bias': quantitative_report['decision']['bias'],
                    'confidence': quantitative_report['decision']['confidence']
                }
            }
            
            # Call LLM API
            headers = {
                'Authorization': f"Bearer {self.llm_config['api_key']}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                #"model": self.llm_config['model'],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional trading desk assistant. Convert structured market data into simple, actionable trading language."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a clear trading summary in language: {self.report_language}. Keep it simple, actionable, and non-technical. Always include: market summary, bias, confidence, key levels, and action.\n\nJSON:\n{json.dumps(report_data)}"
                    }
                ]
            }
            
            # LLM API call with timeout
            response = requests.post(
                self.llm_config['api_url'],
                headers=headers,
                json=payload,
                timeout=15
            )
            
            # Process response
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    llm_text = result['choices'][0]['message']['content'].strip()
                    
                    # Clean and format the output
                    lines = llm_text.split('\n')
                    cleaned_lines = [line.strip() for line in lines if line.strip()]
                    if len(cleaned_lines) > 12:  # Truncate if too long
                        cleaned_lines = cleaned_lines[:12]
                    
                    return '\n'.join(cleaned_lines)
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            # Log error but don't break the main functionality
            return None
    
    def validate_data(self):
        """Handle missing values, sorting, numeric types, and NaN handling."""
        # Check required columns
        required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(self.df['datetime']):
            self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        
        # Sort by datetime
        self.df = self.df.sort_values('datetime').reset_index(drop=True)
        
        # Ensure numeric types
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Handle missing values - forward fill for OHLC, zero fill for volume
        self.df['open'] = self.df['open'].ffill()
        self.df['high'] = self.df['high'].ffill()
        self.df['low'] = self.df['low'].ffill()
        self.df['close'] = self.df['close'].ffill()
        self.df['volume'] = self.df['volume'].fillna(0)
        
        # Drop any remaining NaN rows
        self.df = self.df.dropna()
        
        # Ensure minimum data requirement (20 observations for indicators)
        if len(self.df) < 20:
            raise ValueError("Insufficient data: minimum 20 observations required")
    
    def compute_indicators(self):
        """Compute technical indicators using vectorized operations."""
        import pandas_ta as ta  # Vectorized technical analysis library
        
        # Price data
        close = self.df['close']
        high = self.df['high']
        low = self.df['low']
        volume = self.df['volume']
        
        # EMA indicators (with safe handling for None returns)
        self.indicators['ema20'] = ta.ema(close, length=20)
        self.indicators['ema50'] = ta.ema(close, length=50)
        self.indicators['ema200'] = ta.ema(close, length=200)
        
        # Ensure we have valid Series objects, not None
        if self.indicators['ema20'] is None:
            self.indicators['ema20'] = pd.Series(index=close.index)
        if self.indicators['ema50'] is None:
            self.indicators['ema50'] = pd.Series(index=close.index)
        if self.indicators['ema200'] is None:
            self.indicators['ema200'] = pd.Series(index=close.index)
        
        # RSI indicator
        self.indicators['rsi'] = ta.rsi(close, length=14)
        if self.indicators['rsi'] is None:
            self.indicators['rsi'] = pd.Series(index=close.index)
        
        # ATR indicator
        atr = ta.atr(high, low, close, length=14)
        if atr is None:
            atr = pd.Series(0, index=close.index)
        self.indicators['atr'] = atr
        self.indicators['atr_pct'] = atr / close * 100  # ATR as percentage
        
        # Bollinger Bands
        bb = ta.bbands(close, length=20, std=2)
        ## Use safer column access for Bollinger Bands
        bb_upper_col = 'BBU_20_2.0_2.0' if 'BBU_20_2.0_2.0' in bb.columns else (bb.columns[2] if len(bb.columns) > 2 else None)
        bb_lower_col = 'BBL_20_2.0_2.0' if 'BBL_20_2.0_2.0' in bb.columns else (bb.columns[0] if len(bb.columns) > 0 else None)
        bb_middle_col = 'BBM_20_2.0_2.0' if 'BBM_20_2.0_2.0' in bb.columns else (bb.columns[1] if len(bb.columns) > 1 else None)
        
        self.indicators['bb_upper'] = bb[bb_upper_col] if bb_upper_col and len(bb.columns) > 3 else close * 1.05
        self.indicators['bb_lower'] = bb[bb_lower_col] if bb_lower_col and len(bb.columns) > 1 else close * 0.95
        self.indicators['bb_middle'] = bb[bb_middle_col] if bb_middle_col and len(bb.columns) > 2 else close
        
        # VWAP computation
        typical_price = (close + high + low) / 3
        cum_typical_volume = (typical_price * volume).cumsum()
        cum_volume = volume.cumsum()
        self.indicators['vwap'] = cum_typical_volume / cum_volume
        
        # Compute EMA slopes (5-period change) - with safe handling
        self.indicators['ema20_slope'] = self.indicators['ema20'].diff(5).fillna(0)
        self.indicators['ema50_slope'] = self.indicators['ema50'].diff(5).fillna(0)
        self.indicators['ema200_slope'] = self.indicators['ema200'].diff(5).fillna(0)
    
    def compute_market_regime(self):
        """Determine trend and volatility regimes."""
        
        # Trend regime: BULL / BEAR / RANGE
        current_close = self.df['close'].iloc[-1]
        emas = {
            'ema20': self.indicators['ema20'].iloc[-1],
            'ema50': self.indicators['ema50'].iloc[-1],
            'ema200': self.indicators['ema200'].iloc[-1]
        }
        
        # Check if price is above key moving averages
        above_ema20 = current_close > emas['ema20']
        above_ema50 = current_close > emas['ema50']
        above_ema200 = current_close > emas['ema200']
        
        # Check EMA slopes (positive = bullish, negative = bearish)
        slope_ema20 = self.indicators['ema20_slope'].iloc[-1] if not pd.isna(self.indicators['ema20_slope'].iloc[-1]) else 0
        slope_ema50 = self.indicators['ema50_slope'].iloc[-1] if not pd.isna(self.indicators['ema50_slope'].iloc[-1]) else 0
        
        # Trend regime logic
        if above_ema20 and above_ema50 and slope_ema20 > 0 and slope_ema50 > 0:
            trend_regime = "BULL"
        elif not above_ema20 and not above_ema50 and slope_ema20 < 0 and slope_ema50 < 0:
            trend_regime = "BEAR"
        else:
            trend_regime = "RANGE"
        
        # Volatility regime: COMPRESSION / NORMAL / EXPANSION
        atr_pct = self.indicators['atr_pct'].iloc[-1]
        atr_mean = self.indicators['atr_pct'].iloc[-20:].mean()
        
        if atr_pct < atr_mean * 0.7:  # 30% below mean = compression
            vol_regime = "COMPRESSION"
        elif atr_pct > atr_mean * 1.3:  # 30% above mean = expansion
            vol_regime = "EXPANSION"
        else:
            vol_regime = "NORMAL"
        
        self.market_regime = {
            'trend': trend_regime,
            'volatility': vol_regime,
            'ema_alignments': {
                'above_ema20': above_ema20,
                'above_ema50': above_ema50,
                'above_ema200': above_ema200
            },
            'atr': atr_pct
        }
    
    def compute_levels(self):
        """Compute structural support/resistance levels."""
        current_close = self.df['close'].iloc[-1]
        
        # Rolling highs and lows
        self.levels['s1'] = self.df['low'].rolling(20).min().iloc[-1]  # Support 1
        self.levels['s2'] = self.df['low'].rolling(50).min().iloc[-1]  # Support 2
        self.levels['r1'] = self.df['high'].rolling(20).max().iloc[-1]  # Resistance 1
        self.levels['r2'] = self.df['high'].rolling(50).max().iloc[-1]  # Resistance 2
        
        # Add recent levels for more precise analysis
        self.levels['recent_high'] = self.df['high'].iloc[-5:].max()
        self.levels['recent_low'] = self.df['low'].iloc[-5:].min()
        
        # Proximity calculations
        self.levels['proximity_to_s1'] = (current_close - self.levels['s1']) / current_close * 100
        self.levels['proximity_to_r1'] = (self.levels['r1'] - current_close) / current_close * 100
        self.levels['vwap_proximity'] = (current_close - self.indicators['vwap'].iloc[-1]) / current_close * 100
    
    def compute_long_features(self):
        """Compute feature scores for LONG edge."""
        current_close = self.df['close'].iloc[-1]
        rsi = self.indicators['rsi'].iloc[-1]
        atr_pct = self.indicators['atr_pct'].iloc[-1]
        vwap = self.indicators['vwap'].iloc[-1]
        
        # Feature components
        current_close = self.df['close'].iloc[-1]
        emas = {
            'ema20': self.indicators['ema20'].iloc[-1],
            'ema50': self.indicators['ema50'].iloc[-1],
            'ema200': self.indicators['ema200'].iloc[-1]
        }
        
        # Price above EMAs
        price_above_ema20 = 1 if current_close > emas['ema20'] else 0
        price_above_ema50 = 1 if current_close > emas['ema50'] else 0
        price_above_ema200 = 1 if current_close > emas['ema200'] else 0
        
        # EMA slopes positive
        emas_positive = 1 if (self.indicators['ema20_slope'].iloc[-1] > 0 and 
                             self.indicators['ema50_slope'].iloc[-1] > 0) else 0
        
        # RSI in optimal zone
        rsi_favorable = 1 if 45 <= rsi <= 65 else 0
        
        # Pullback near support
        near_s1 = 1 if 0 <= self.levels['proximity_to_s1'] <= 2 else 0
        near_s2 = 1 if 0 <= (current_close - self.levels['s2']) / current_close * 100 <= 3 else 0
        
        # Compression breakout setup
        compression_setup = 1 if self.market_regime['volatility'] == 'COMPRESSION' else 0
        
        # Proximity to VWAP
        vwap_favorable = 1 if -2 <= self.levels['vwap_proximity'] <= 2 else 0
        
        self.long_features = {
            'price_above_ema20': price_above_ema20,
            'price_above_ema50': price_above_ema50,
            'price_above_ema200': price_above_ema200,
            'emas_positive': emas_positive,
            'rsi_favorable': rsi_favorable,
            'near_s1': near_s1,
            'near_s2': near_s2,
            'compression_setup': compression_setup,
            'vwap_favorable': vwap_favorable,
            'atr_level': atr_pct
        }
    
    def compute_short_features(self):
        """Compute feature scores for SHORT edge."""
        current_close = self.df['close'].iloc[-1]
        rsi = self.indicators['rsi'].iloc[-1]
        atr_pct = self.indicators['atr_pct'].iloc[-1]
        
        # Feature components
        emas = {
            'ema20': self.indicators['ema20'].iloc[-1],
            'ema50': self.indicators['ema50'].iloc[-1],
            'ema200': self.indicators['ema200'].iloc[-1]
        }
        
        # Price below EMAs
        price_below_ema20 = 1 if current_close < emas['ema20'] else 0
        price_below_ema50 = 1 if current_close < emas['ema50'] else 0
        price_below_ema200 = 1 if current_close < emas['ema200'] else 0
        
        # EMA slopes negative
        emas_negative = 1 if (self.indicators['ema20_slope'].iloc[-1] < 0 and 
                            self.indicators['ema50_slope'].iloc[-1] < 0) else 0
        
        # RSI in optimal short zone
        rsi_favorable = 1 if 35 <= rsi <= 55 else 0
        
        # Rejection near resistance
        near_r1 = 1 if 0 <= self.levels['proximity_to_r1'] <= 2 else 0
        near_r2 = 1 if 0 <= (self.levels['r1'] - current_close) / current_close * 100 <= 3 else 0
        
        # Volatility expansion downward setup
        expansion_setdown = 1 if self.market_regime['volatility'] == 'EXPANSION' else 0
        
        # VWAP rejection
        vwap_rejected = 1 if self.levels['vwap_proximity'] > 3 else 0
        
        self.short_features = {
            'price_below_ema20': price_below_ema20,
            'price_below_ema50': price_below_ema50,
            'price_below_ema200': price_below_ema200,
            'emas_negative': emas_negative,
            'rsi_favorable': rsi_favorable,
            'near_r1': near_r1,
            'near_r2': near_r2,
            'expansion_setdown': expansion_setdown,
            'vwap_rejected': vwap_rejected,
            'atr_level': atr_pct
        }
    
    def compute_edge_scores(self):
        """Compute probabilistic edge scores (0-100) for LONG and SHORT."""
        
        # LONG EDGE SCORE
        long_score_components = {
            'trend_alignment': (
                self.long_features['price_above_ema20'] * 10 + 
                self.long_features['price_above_ema50'] * 10 + 
                self.long_features['price_above_ema200'] * 10 + 
                self.long_features['emas_positive'] * 10
            ),
            'momentum': (
                self.long_features['rsi_favorable'] * 15 + 
                (5 if self.long_features['near_s1'] else 0) + 
                (5 if self.long_features['compression_setup'] else 0)
            ),
            'volatility_regime': (
                10 if self.market_regime['volatility'] == 'COMPRESSION' else 
                15 if self.market_regime['volatility'] == 'NORMAL' else 
                5
            ),
            'location': (
                (8 if self.long_features['vwap_favorable'] else 0) + 
                (7 if self.long_features['near_s2'] else 0)
            )
        }
        
        long_raw_score = sum(long_score_components.values())
        
        # SHORT EDGE SCORE
        short_score_components = {
            'trend_alignment': (
                self.short_features['price_below_ema20'] * 10 + 
                self.short_features['price_below_ema50'] * 10 + 
                self.short_features['price_below_ema200'] * 10 + 
                self.short_features['emas_negative'] * 10
            ),
            'momentum': (
                self.short_features['rsi_favorable'] * 15 + 
                (5 if self.short_features['near_r1'] else 0) + 
                (5 if self.short_features['expansion_setdown'] else 0)
            ),
            'volatility_regime': (
                10 if self.market_regime['volatility'] == 'EXPANSION' else 
                15 if self.market_regime['volatility'] == 'NORMAL' else 
                5
            ),
            'location': (
                (8 if self.short_features['vwap_rejected'] else 0) + 
                (7 if self.short_features['near_r2'] else 0)
            )
        }
        
        short_raw_score = sum(short_score_components.values())
        
        # Risk penalty (applies to both sides)
        risk_penalty = self._compute_risk_penalty()
        
        # Scale to 0-100 range (empirical scaling from testing)
        long_score = min(100, max(0, int(long_raw_score * 1.1)))
        short_score = min(100, max(0, int(short_raw_score * 1.0)))
        
        # Apply risk penalty
        long_score = max(0, long_score - risk_penalty)
        short_score = max(0, short_score - risk_penalty)
        
        self.edge_scores = {
            'long_score': long_score,
            'short_score': short_score,
            'risk_penalty': risk_penalty,
            'components': {
                'long': long_score_components,
                'short': short_score_components
            }
        }
    
    def _compute_risk_penalty(self):
        """Compute risk penalty based on adverse conditions."""
        penalty = 0
        
        # High ATR = higher risk
        atr_pct = self.indicators['atr_pct'].iloc[-1]
        if atr_pct > 5:  # High volatility
            penalty += 5
        elif atr_pct > 10:
            penalty += 10
        
        # Overbought/oversold extremes
        rsi = self.indicators['rsi'].iloc[-1]
        if rsi > 70:
            penalty += 3  # LONG edge risk
        elif rsi < 30:
            penalty += 3  # SHORT edge risk
        
        # Price far from VWAP
        vwap_proximity = abs(self.levels['vwap_proximity'])
        if vwap_proximity > 5:
            penalty += 2
        elif vwap_proximity > 10:
            penalty += 5
        
        return penalty
    
    def compute_decision(self):
        """Make final trading decision based on edge scores."""
        long_score = self.edge_scores['long_score']
        short_score = self.edge_scores['short_score']
        
        # Determine bias
        if long_score > short_score and long_score > 70:
            bias = "BUY WATCH"
        elif short_score > long_score and short_score > 70:
            bias = "SELL WATCH"
        else:
            bias = "WAIT"
        
        # Determine confidence level
        score_diff = abs(long_score - short_score)
        if max(long_score, short_score) > 85 and score_diff > 25:
            confidence = "HIGH"
        elif max(long_score, short_score) > 70 and score_diff > 15:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        self.decision = {
            'bias': bias,
            'confidence': confidence,
            'long_score': long_score,
            'short_score': short_score,
            'score_spread': score_diff
        }
    
    def generate_report(self):
        """Generate structured analysis report."""
        # Ensure all components have been computed
        if not self.indicators:
            self.compute_indicators()
        if not self.market_regime:
            self.compute_market_regime()
        if not self.levels:
            self.compute_levels()
        if not self.long_features:
            self.compute_long_features()
        if not self.short_features:
            self.compute_short_features()
        if not self.edge_scores:
            self.compute_edge_scores()
        if not self.decision:
            self.compute_decision()
        
        # Get current values for report
        indicators_report = {
            'ema20': round(self.indicators['ema20'].iloc[-1], 2),
            'ema50': round(self.indicators['ema50'].iloc[-1], 2),
            'ema200': round(self.indicators['ema200'].iloc[-1], 2),
            'rsi': round(self.indicators['rsi'].iloc[-1], 2),
            'atr': round(self.indicators['atr'].iloc[-1], 2),
            'vwap': round(self.indicators['vwap'].iloc[-1], 2),
            'bb_bandwidth': round((self.indicators['bb_upper'].iloc[-1] - self.indicators['bb_lower'].iloc[-1]) / self.indicators['bb_middle'].iloc[-1] * 100, 2) if self.indicators['bb_middle'].iloc[-1] != 0 else 0
        }
        
        # Generate quantitative report (original format)
        quantitative_report = {
            'market_regime': self.market_regime,
            'indicators': indicators_report,
            'levels': {
                's1': round(self.levels['s1'], 2),
                's2': round(self.levels['s2'], 2),
                'r1': round(self.levels['r1'], 2),
                'r2': round(self.levels['r2'], 2),
                'vwap': round(self.levels['vwap_proximity'], 2)
            },
            'edge': {
                'long_score': self.edge_scores['long_score'],
                'short_score': self.edge_scores['short_score'],
                'risk_penalty': self.edge_scores['risk_penalty']
            },
            'decision': {
                'bias': self.decision['bias'],
                'confidence': self.decision['confidence']
            }
        }
        
        # Generate LLM interpretation
        llm_report = self._generate_llm_interpretation()
        
        # Return combined report
        return {
            'quantitative': quantitative_report,
            'llm_interpretation': llm_report if llm_report else 'LLM REPORT UNAVAILABLE'
        }


# Helper functions for external use

def quick_edge_analysis(df):
    """
    Quick analysis helper function.
    
    Args:
        df: OHLCV dataframe with columns: datetime, open, high, low, close, volume
        
    Returns:
        dict: Analysis report
    """
    engine = EdgeEngine(df)
    return engine.generate_report()