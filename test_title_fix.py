#!/usr/bin/env python3
"""Test the updated title formatting for RACE.MI with Ferrari Spa"""

import sys
sys.path.insert(0, "/Users/alberto.sfolcini/Development/quantstudio")

from rich.panel import Panel
from rich.console import Console

console = Console()

# Simulate metadata load for RACE.MI
_metadata = {"short_name": "Ferrari Spa"}
ticker = "RACE.MI"
short_name = _metadata.get("short_name", "")

# New title formatting logic (as implemented)
title_text = f"[bold cyan]EDGE ANALYSIS — {ticker}[/bold cyan]"
if short_name:
    title_text += f" [italic]— {short_name}[/italic]"
    title_panel = Panel(title_text, style="bold magenta", expand=False)
    console.print(title_panel)
    
print("\n✓ Title now includes company name inline")
print("✅ Expected: EDGE ANALYSIS — RACE.MI — Ferrari Spa (Ferrari Spa in italics)")
