#!/usr/bin/env python3
"""
QuantStudio - Terminal User Interface for Historical Market Data Management

This is the main entry point for the QuantStudio application.
It launches the TUI and delegates all logic to core modules.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.tui import run_ui

if __name__ == "__main__":
    run_ui()
