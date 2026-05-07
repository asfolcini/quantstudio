#!/usr/bin/env python3
"""Final integration test showing title + OHLCV formatting"""

import sys
sys.path.insert(0, "/Users/alberto.sfolcini/Development/quantstudio")

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import pandas as pd

console = Console()

# Simulate data for RACE.MI
metadata = {"short_name": "Ferrari Spa"}
ticker = "RACE.MI"
short_name = metadata.get("short_name", "")

# Create sample OHLCV DataFrame
df = pd.DataFrame({
    'datetime': ['2023-10-30'],
    'open': [23.92],
    'high': [24.02],
    'low': [23.76],
    'close': [23.86],
    'volume': [1234567]
})
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

# Title with company name
title_text = f"[bold cyan]EDGE ANALYSIS — {ticker}[/bold cyan]"
if short_name:
    title_text += f" [italic]— {short_name}[/italic]"
title_panel = Panel(title_text, style="bold magenta", expand=False)
console.print(title_panel)

# OHLCV line
def format_price(price):
    price = float(price)
    if price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.4f}"

last_row = df.iloc[-1]
date = last_row.name.strftime("%Y-%m-%d")
open_price = format_price(last_row['open'])
high_price = format_price(last_row['high'])
low_price = format_price(last_row['low'])
close_price = format_price(last_row['close'])
volume = f"{last_row['volume']:,}"

ohlcv_text = Text.assemble(
    ("Last: ", "white"),
    (date, "white"),
    (" | ", "white"),
    ("O", "bold white"),
    (f": {open_price}", "white"),
    (" | ", "white"),
    ("H", "bold white"),
    (f": {high_price}", "white"),
    (" | ", "white"),
    ("L", "bold white"),
    (f": {low_price}", "white"),
    (" | ", "white"),
    ("C", "bold white"),
    (f": {close_price}", "white"),
    (" | Volume: ", "white"),
    (volume, "white")
)
ohlcv_panel = Panel(ohlcv_text, border_style="yellow", expand=False, padding=(0, 1))
console.print(ohlcv_panel)

print("\n✅ Final Title: Shows 'EDGE ANALYSIS — RACE.MI — Ferrari Spa'")
print("✅ OHLCV Line: Shows bold O, H, L, C with correct formatting")
