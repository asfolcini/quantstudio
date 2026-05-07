# QuantStudio
*Author: Alberto Sfolcini <a.sfolcini@gmail.com>*

## What is QuantStudio?
QuantStudio is a financial data analysis tool for collecting, processing, and analyzing market data. It automates repetitive workflows (e.g., data fetching, validation, regime detection) to ensure consistency and efficiency.

## Key Features
- **Universe Management**: Define and update asset baskets (e.g., tickers, indices) with built-in validation.
- **Data Pipeline**: Fetch, sanitize, and standardize OHLCV data from sources like Yahoo Finance.
- **Regime Detection**: Identify market regimes (trending, mean-reverting) using statistical models.
- **Strategy Ranking**: Rank assets based on metrics like momentum, volatility, or custom scores.
- **Historical Data**: Store and access cleaned datasets for backtesting and research.
- **CLI/TUI Interface**: Command-line tools for daily operations, reporting, and configuration.

### **Run on Single Ticker**
Analyze a single asset (e.g., `AAPL.MI`) by fetching its price history, detecting market regimes (trending/sideways), and calculating key metrics like volatility and momentum. This helps you quickly assess if a stock is range-bound or trending, and identify opportunities based on its current behavior.

### **Run on Universe**
Process an entire group of assets (e.g., all FTSE MIB stocks) at once, ranking them by performance, regime, and other metrics. This saves time and lets you compare opportunities across multiple assets, helping you spot the strongest or weakest performers in the current market environment.

### **Setup Discoverer**
Find high-probability trade setups by filtering for specific conditions (e.g., only momentum trades in trending markets). This reduces guesswork by highlighting opportunities that fit the current market regime, ensuring you focus on strategies with the highest chance of success.

## Installation
1. **Prerequisites**
   - Python 3.11+ (verify with `python --version`).
   - Git.

2. **Clone & Setup**
   ```bash
   git clone https://github.com/asfolcini/quantstudio.git
   cd quantstudio
   ```

3. **Dependencies**
   Install required packages:
   ```bash
   pip install pandas numpy yfinance python-dotenv
   ```

4. **Configure `config.json`**
   - Launch the TUI:
     ```bash
     python quantstudio.py
     ```
   - Navigate to **Settings** → **Configure Universe/Data** to edit:
     - Asset universe (e.g., tickers like `AAPL.MI`, `^FTSE%).
     - Data source settings (e.g., Yahoo Finance timeframes).
     - Regime detection parameters.
   - The `config.json` file is generated/updated automatically.

5. **Run**
   ```bash
   python quantstudio.py
   ```

## Documentation
For details, visit [surprisalx.com/qstudio](https://surprisalx.com/qstudio).