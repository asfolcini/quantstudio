#!/usr/bin/env python3
"""
Test script to preview the updated report format.
This demonstrates what the new output will look like without running the full application.
"""

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def preview_updated_report():
    """Preview the new report format with ticker name and OHLCV data."""
    console = Console()
    
    # Simulate data
    ticker = "ENI.MI"
    short_name = "ENI S.p.A."
    
    # Create a DataFrame with sample OHLCV data
    df = pd.DataFrame({
        'datetime': ['2023-10-30'],
        'open': [23.4512],
        'high': [23.8023],
        'low': [23.1034],
        'close': [23.5056],
        'volume': [1234567]
    })
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Extract last OHLCV row
    last_row = df.iloc[-1]
    date = last_row.name.strftime("%Y-%m-%d")
    
    def format_price(price):
        price = float(price)
        if price >= 1:
            return f"{price:.2f}"
        elif price >= 0.01:
            return f"{price:.4f}"
        else:
            return f"{price:.6f}"
    
    open_price = format_price(last_row['open'])
    high_price = format_price(last_row['high'])
    low_price = format_price(last_row['low'])
    close_price = format_price(last_row['close'])
    volume = f"{last_row['volume']:,}"
    
    # Build title panel with ticker name
    title_text = f"[bold cyan]EDGE ANALYSIS — {ticker}[/bold cyan]"
    if short_name:
        title_text += f"\n[italic]{short_name}[/italic]"
    title_panel = Panel(title_text, style="bold magenta", expand=False)
    console.print(title_panel)
    
    # Build OHLCV panel
    ohlcv_text = Text(
        f"Last: {date} | [bold]O[/bold]: {open_price} | [bold]H[/bold]: {high_price} | "
        f"[bold]L[/bold]: {low_price} | [bold]C[/bold]: {close_price} | Volume: {volume}",
        style="white"
    )
    ohlcv_panel = Panel(
        ohlcv_text,
        border_style="yellow",
        expand=False,
        padding=(0, 1)
    )
    console.print(ohlcv_panel)
    
    # Show sample of what the rest of the report would look like
    console.print("\nThe rest of the report (Market Regime, Edge Scores, Decision, Key Indicators, AI Summary) would continue below...")
    console.print("For demonstration, here is a portion:")
    
    # Simulate a sample table
    from rich.table import Table
    from rich import box
    
    regime_table = Table(title="Market Regime", box=box.SIMPLE)
    regime_table.add_column("Field", style="green", min_width=16)
    regime_table.add_column("Value", style="yellow")
    regime_table.add_row("Trend", "BULL")
    regime_table.add_row("Volatility", "NORMAL")
    regime_table.add_row("ATR", "0.68")
    
    console.print(regime_table)
    console.print("\n[green]✓ Report format updated successfully![/green]")

if __name__ == "__main__":
    preview_updated_report()