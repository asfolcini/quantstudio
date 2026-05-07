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