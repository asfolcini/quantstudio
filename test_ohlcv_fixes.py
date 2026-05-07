#!/usr/bin/env python3

import pandas as pd
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
import sys
sys.path.insert(0, "/Users/alberto.sfolcini/Development/quantstudio")

def testDateExtraction():
    df = pd.DataFrame({
        'datetime': ['2023-10-30'],
        'open': [23.4512],
        'high': [23.8023],
        'low': [23.1034],
        'close': [23.5056],
        'volume': [1234567]
    })
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    
    last_row = df.iloc[-1]
    if isinstance(last_row.name, pd.Timestamp):
        date = last_row.name.strftime("%Y-%m-%d")
    elif isinstance(last_row.name, str):
        date = pd.to_datetime(last_row.name).strftime("%Y-%m-%d")
    else:
        date = df['datetime'].iloc[-1].strftime("%Y-%m-%d")
    
    print(f"Date: {date} (Expected: 2023-10-30)")
    return date

def testBoldFormatting(date):
    console = Console()
    ohlcv_text = Text.assemble(
        ("Last: ", "white"),
        (date, "white"),
        (" | ", "white"),
        ("O", "bold white"),
        (": 23.45", "white"),
        (" | ", "white"),
        ("H", "bold white"),
        (": 23.80", "white"),
        (" | ", "white"),
        ("L", "bold white"),
        (": 23.10", "white"),
        (" | ", "white"),
        ("C", "bold white"),
        (": 23.51", "white"),
        (" | Volume: ", "white"),
        ("1,234,567", "white")
    )
    console.print(ohlcv_text)

if __name__ == "__main__":
    date = testDateExtraction()
    testBoldFormatting(date)
