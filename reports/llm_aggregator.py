# reports/llm_aggregator.py
"""
Aggregated LLM Report Generator for QuantStudio.
Generates a concise but detailed LLM report from multiple ticker results.
"""

import json
import requests
from typing import List, Dict, Optional


def generate_aggregated_llm_report(
    top_results: List[Dict],
    universe_name: str,
    llm_config: Dict,
    timeout: int = 60
) -> str:
    """
    Generate an LLM-based aggregated report for a universe of tickers.
    
    Args:
        top_results: List of ticker metrics (from run_on_universe).
        universe_name: Name of the universe analyzed.
        llm_config: LLM configuration (api_url, api_key).
        timeout: API call timeout in seconds (default: 60).
        
    Returns:
        Formatted LLM report as a string. Falls back to code-generated report on error.
    """
    # Filter operational signals (exclude WAIT and LOW confidence)
    operational_signals = [
        res for res in top_results
        if res['signal'] in ["BUY", "BUY WATCH", "SELL", "SELL WATCH"]
        and res['confidence'] in ["HIGH", "MEDIUM"]
    ]
    
    # Early exit if no operational signals
    if not operational_signals:
        return "Nessuna opportunità operativa rilevata nel report LLM."
    
    # Prepare payload for LLM
    payload = {
        "universe_name": universe_name,
        "statistics": {
            "total_tickers": len(top_results),
            "with_operational_signal": len(operational_signals),
            "dominant_trend": _get_dominant_trend(top_results),
            "volatility_distribution": _get_volatility_distribution(top_results)
        },
        "long_opportunities": _prepare_long_opportunities(operational_signals),
        "short_opportunities": _prepare_short_opportunities(operational_signals)
    }
    
    # Call LLM if configured
    llm_report = _call_llm_api(payload, llm_config, timeout)
    if llm_report:
        return llm_report
    else:
        return _generate_fallback_report(top_results, universe_name)


# --- Internal Helper Functions ---

def _get_dominant_trend(results: List[Dict]) -> str:
    """Calculate dominant trend across all results."""
    trends = [res['trend'] for res in results]
    return max(set(trends), key=trends.count, default="UNKNOWN")


def _get_volatility_distribution(results: List[Dict]) -> Dict[str, int]:
    """Count volatility regimes."""
    dist = {"COMPRESSION": 0, "NORMAL": 0, "EXPANSION": 0}
    for res in results:
        vol = res.get('volatility', 'UNKNOWN')
        if vol in dist:
            dist[vol] += 1
    return dist


def _prepare_long_opportunities(results: List[Dict]) -> List[Dict]:
    """Format long opportunities with calculated levels."""
    longs = [res for res in results if res['signal'] in ["BUY", "BUY WATCH"]]
    opportunities = []
    for res in sorted(longs, key=lambda x: x['confidence'], reverse=True)[:3]:
        entry = res['last_price'] * 0.99  # -1% pullback
        target1 = res['last_price'] * 1.05  # +5%
        target2 = res['last_price'] * 1.10  # +10%
        stop = res['last_price'] * 0.95  # -5%
        
        opportunities.append({
            "ticker": res['ticker'],
            "signal": res['signal'],
            "confidence": res['confidence'],
            "trend": res['trend'],
            "variation_7d": res['variations']['weekly'],
            "last_price": res['last_price'],
            "entry_target": entry,
            "take_profit_1": target1,
            "take_profit_2": target2,
            "stop_loss": stop
        })
    return opportunities


def _prepare_short_opportunities(results: List[Dict]) -> List[Dict]:
    """Format short opportunities with calculated levels."""
    shorts = [res for res in results if res['signal'] in ["SELL", "SELL WATCH"]]
    opportunities = []
    for res in sorted(shorts, key=lambda x: x['confidence'], reverse=True)[:3]:
        entry = res['last_price'] * 1.01  # +1% rejection
        target1 = res['last_price'] * 0.95  # -5%
        target2 = res['last_price'] * 0.90  # -10%
        stop = res['last_price'] * 1.05  # +5%
        
        opportunities.append({
            "ticker": res['ticker'],
            "signal": res['signal'],
            "confidence": res['confidence'],
            "trend": res['trend'],
            "variation_7d": res['variations']['weekly'],
            "last_price": res['last_price'],
            "entry_target": entry,
            "take_profit_1": target1,
            "take_profit_2": target2,
            "stop_loss": stop
        })
    return opportunities


def _call_llm_api(payload: Dict, llm_config: Dict, timeout: int) -> Optional[str]:
    """Call external LLM API for interpretation."""
    # Skip if LLM config is incomplete
    if not llm_config.get('api_url') or not llm_config.get('api_key'):
        return None
    
    try:
        
        headers = {
            'Authorization': f"Bearer {llm_config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "Respond concisely in Italian with trading recommendations."
                },
                {
                    "role": "user",
                    "content": (
                        "Sei un assistente di trading professionale. "
                        "Analizza questo portafoglio di tickers e fornisci una strategia operativa "
                        f"concisa (max 100 parole). JSON: {json.dumps(payload)}"
                    )
                }
            ]
        }
        
        response = requests.post(
            llm_config['api_url'],
            headers=headers,
            json=data,
            timeout=timeout
        )
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            return content.strip() if content else None
        else:
            return None
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


def _generate_fallback_report(top_results: List[Dict], universe_name: str) -> str:
    """Fallback report if LLM fails."""
    operational_signals = [
        res for res in top_results
        if res['signal'] in ["BUY", "BUY WATCH", "SELL", "SELL WATCH"]
        and res['confidence'] in ["HIGH", "MEDIUM"]
    ]
    
    report_lines = [
        f"## 📊 Report Aggregato: {universe_name}",
        "",
        "**Panoramica**",
        f"• {len(operational_signals)} tickers con segnale operativo su {len(top_results)} analizzati.",
        f"• Trend dominante: {_get_dominant_trend(top_results)}.",
        ""
    ]
    
    # Long opportunities
    longs = [res for res in operational_signals if res['signal'] in ["BUY", "BUY WATCH"]]
    if longs:
        report_lines.append("**🟢 Opportunità Long**")
        for res in sorted(longs, key=lambda x: x['confidence'], reverse=True)[:3]:
            entry = res['last_price'] * 0.99
            target = res['last_price'] * 1.10
            stop = res['last_price'] * 0.95
            report_lines.append(
                f"• {res['ticker']}: {res['signal']} (Confidence: {res['confidence']}), "
                f"Trend: {res['trend']}, +{res['variations'].get('weekly', 0):.1f}% 7d | "
                f"Entry: ${entry:.2f}, Target: ${target:.2f}, Stop: ${stop:.2f}"
            )
    
    # Short opportunities
    shorts = [res for res in operational_signals if res['signal'] in ["SELL", "SELL WATCH"]]
    if shorts:
        report_lines.append("**🔴 Opportunità Short**")
        for res in sorted(shorts, key=lambda x: x['confidence'], reverse=True)[:3]:
            entry = res['last_price'] * 1.01
            target = res['last_price'] * 0.90
            stop = res['last_price'] * 1.05
            report_lines.append(
                f"• {res['ticker']}: {res['signal']} (Confidence: {res['confidence']}), "
                f"Trend: {res['trend']}, {res['variations'].get('weekly', 0):.1f}% 7d | "
                f"Entry: ${entry:.2f}, Target: ${target:.2f}, Stop: ${stop:.2f}"
            )
    
    return "\n".join(report_lines)
