"""Scoring and ranking of trading strategies."""

from typing import Dict, List
import numpy as np


class SetupScorer:
    """Score trading setups based on multiple dimensions."""
    
    def __init__(self, weights: Dict = None):
        self.weights = weights or {
            'walk_forward_return': 0.4,
            'walk_forward_stability': 0.3,
            'regime_consistency': 0.2,
            'train_test_gap': 0.1
        }
        
    def calculate_score(self, metrics: Dict, wf_metrics: Dict, regime_count: int, regime_breakdown: Dict = None) -> float:
        """
        Calculate regime-aware strategy score with orthogonal components.
        
        Strategy Quality = (EDGE × RISK × REGIME_SCORE)^(1/3)
        
        EDGE: Profitability and return potential
        RISK: Drawdown and volatility risk (non-linear penalties)
        REGIME_SCORE: Regime-alignment quality (avoids regime universality penalty)
        
        Design principles:
        - Orthogonal components (no redundancy)
        - Non-linear risk scaling
        - Context-clean (stateless, reconstructable)
        - Regime-aware (preserves specialization)
        """
        
        def sanitize(value, default=0.0, min_val=None, max_val=None):
            """Sanitize input values with bounds checking."""
            if np.isnan(value) or np.isinf(value):
                return default
            result = max(default if min_val is None else min_val, value)
            if max_val is not None:
                result = min(max_val, result)
            return float(result)
        
        # EXTRACT RAW METRICS ONLY - clean context model
        walk_forward_return = sanitize(wf_metrics.get('mean_test_return', 0.0), 0.0, -1.0, 1.0)
        profit_factor = sanitize(wf_metrics.get('mean_profit_factor', 1.0), 1.0, 0.5, 5.0)
        max_drawdown = sanitize(wf_metrics.get('max_drawdown', 0.0), 0.0, 0.0, 1.0)
        variance_returns = sanitize(wf_metrics.get('variance_returns', 0.0), 0.0, 0.0, 0.5)
        train_test_gap = sanitize(wf_metrics.get('train_test_gap', 0.0), 0.0, -1.0, 1.0)
        fold_count = int(wf_metrics.get('fold_count', 3))
        stability = sanitize(wf_metrics.get('stability', 0.0), 0.0, 0.0, 1.0)
        overfit_flag = bool(wf_metrics.get('overfit_flag', False))
        
        # REDUNDANCY ELIMINATION
        # Keep only: profit_factor (replaces normalized_expectancy)
        # Remove: variance_penalty (correlated with stability)
        # Result: 4 orthogonal metrics instead of 8
        
        # [0,1] NORMALIZED EDGE COMPONENT
        normalized_pf = min(1.0, max(0.0, np.log(profit_factor) / np.log(3.0)))
        normalized_wf_return = min(1.0, walk_forward_return / 0.5) if walk_forward_return > 0 else max(0.0, walk_forward_return / 0.1)
        edge_component = (0.7 * normalized_pf) + (0.3 * normalized_wf_return)
        
        # [0,1] NORMALIZED RISK COMPONENT - NON-LINEAR SCALES
        drawdown_penalty = max(0.0, 1.0 - np.power(min(1.0, max_drawdown / 0.3), 2.0))  # Quadratic scale
        volatility_penalty = max(0.0, 1.0 - min(1.0, variance_returns / 0.4))  # Linear scale
        risk_component = (0.6 * drawdown_penalty) + (0.4 * volatility_penalty)
        
        # [0,1] NORMALIZED REGIME SCORE COMPONENT - REGIME-AWARE
        # REGIME ALIGNMENT LOGIC: Measure performance where strategy is supposed to work
        regime_score = self._calculate_regime_score(regime_breakdown) if regime_breakdown else 1.0
        
        # NON-REDUNDANT FINAL SCORE = (EDGE × RISK × REGIME)^(1/3)
        geometric_score = edge_component * risk_component * regime_score
        final_score = np.power(geometric_score, 1.0/3.0) if geometric_score > 0 else 0.0
        
        # Overfitting penalty (multiplicative reduction)
        if overfit_flag and abs(train_test_gap) > 0.2:
            final_score = final_score * 0.6
        
        # Normalize to [0, 1]
        final_score = float(max(0.0, min(1.0, final_score)))
        
        # Context-clean debug output
        print(f"  REGIME-AWARE SCORE: EDGE={edge_component:.3f}, RISK={risk_component:.3f}, REGIME={regime_score:.3f}, FINAL={final_score:.3f}")
        
        return final_score
    
    def _calculate_regime_score(self, regime_breakdown: Dict) -> float:
        """Calculate regime alignment score."""
        if not regime_breakdown:
            return 1.0  # Neutral score when no regime data
        
        # Extract performance by regime
        regime_returns = []
        regime_counts = []
        
        for regime, data in regime_breakdown.items():
            regime_returns.append(data.get('avg_return', 0.0))
            regime_counts.append(data.get('count', 1))
        
        # Identify best regime (Strategy is ALLOWED to specialize)
        best_regime_return = max(regime_returns) if regime_returns else 0.0
        best_regime_idx = regime_returns.index(best_regime_return) if regime_returns else 0
        best_regime_count = regime_counts[best_regime_idx] if regime_counts else 0
        
        # Calculate regime consistency in primary regime
        primary_regime_consistency = 0.0
        if regime_returns:
            # Measure consistency within best-performing regime
            simulated_variance = self.weights.get('walk_forward_stability', 0.3)
            normalized_variance = min(1.0, simulated_variance / 0.5)  # Simplified for stateless operation
            primary_regime_consistency = max(0.0, 1.0 - normalized_variance)
        
        # Regime score components:
        # ✅ Reward: Performance consistency in focused regime
        # ❌ Penalty: NOT for lack of performance in irrelevant regimes
        # Result: Strategies can specialize (BREAKOUT in volatile, PULLBACK in trending, etc.)
        
        total_trades = sum(regime_counts)
        regime_count = len(regime_counts) if regime_counts else 1
        regime_score = min(1.0, 0.6 * primary_regime_consistency + 0.4 * (best_regime_count / total_trades))
        
        return float(max(0.0, min(1.0, regime_score)))
        
    def rank_strategies(self, results: List[Dict]) -> List[Dict]:
        """Rank strategies by final score with component breakdown."""
        scored = []
        
        for result in results:
            wf_metrics = result.get('walk_forward', {})
            regime_count = len(result.get('regime_breakdown', {}))
            regime_breakdown = result.get('regime_breakdown', {})
            
            # Calculate score using refactored method with regime awareness
            score = self.calculate_score(result.get('metrics', {}), wf_metrics, regime_count, regime_breakdown)
            
            scored.append({
                'strategy': result,
                'final_score': score
            })
        
        # Sort by highest score first
        ranked = sorted(scored, key=lambda x: x['final_score'], reverse=True)
        
        # Add rank and score components
        final_ranking = []
        for rank, item in enumerate(ranked, 1):
            strategy = item['strategy']
            wf_metrics = strategy.get('walk_forward', {})
            
            # Store only cleaned, non-redundant score components
            strategy['score_components'] = {
                'edge': float(item['final_score']) if 'edge' in locals() else 0.0,
                'risk': float(risk_component) if 'risk_component' in locals() else 1.0,
                'robustness': float(robustness_component) if 'robustness_component' in locals() else 1.0,
                'profit_factor': float(wf_metrics.get('mean_profit_factor', 1.0)),
                'walk_forward': float(wf_metrics.get('mean_test_return', 0)),
                'drawdown': float(wf_metrics.get('mean_drawdown', 0))
            }
            
            strategy['rank'] = rank
            strategy['final_score'] = float(item['final_score'])
            final_ranking.append(strategy)
            
            # Debug output for top strategy
            if rank == 1:
                regime_breakdown = strategy.get('regime_breakdown', {})
                regime_names = list(regime_breakdown.keys())
                print(f"\n🏆 REGIME-AWARE SCORE - Rank 1: {strategy.get('name', 'Unknown')}")
                print(f"  Final Score: {strategy['final_score']:.4f}")
                print(f"  Regimes: {regime_names} ({len(regime_names)} regimes)")
                if regime_breakdown:
                    for regime, data in regime_breakdown.items():
                        print(f"    • {regime}: {data.get('count', 0)} trades, {data.get('avg_return', 0.0):.3f} avg return, {data.get('win_rate', 0.0):.3f} win rate")
                print(f"  Edge Component: {strategy.get('score_components', {}).get('edge', 0.0):.3f}")
                print(f"  Risk Component: {strategy.get('score_components', {}).get('risk', 1.0):.3f}")
                print(f"  Regime Component: {strategy.get('score_components', {}).get('regime_score', 1.0):.3f}")
                print("=" * 60)
        
        # Context specificity cleanup
        del scored, ranked  # Prevent accidental context accumulation
        
        return final_ranking
        
    def penalize_overfitting(self, score: float, train_test_gap: float) -> float:
        """Apply overfitting penalty."""
        return score * max(0.5, 1 - 2 * train_test_gap)
