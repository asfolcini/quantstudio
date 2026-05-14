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
- **News Analysis**: Real-time parsing of global RSS feeds (e.g., Google News) with LLM AI to score macroeconomic/geopolitical events.
- **CLI/TUI Interface**: Command-line tools for daily operations, reporting, and configuration.

### What Each Function Does (And Why It Matters)
#### **1. Run on Single Ticker**
Analyzes a single asset (e.g., `AAPL.MI`) by fetching its price history, detecting whether the market is trending or moving sideways, and calculating key metrics like volatility and momentum.

**Why it’s useful**:
- Quickly assess an asset’s behavior without manual data crunching.
- Spot if a stock is stuck in a range or trending strongly.
- Identify abnormal volatility before entering a trade.

#### **2. Run on Universe**
Processes a group of assets (e.g., all FTSE MIB stocks) in one go, ranking them based on performance, regime (trending/sideways), and other metrics.

**Why it’s useful**:
- Save time: Analyze dozens of assets at once instead of one-by-one.
- Compare opportunities: Instantly see which stocks are strongest/weakest in the current market regime.
- Portfolio insights: Quickly rebalance or adjust positions based on relative strength.

#### **3. Setup Discoverer**
Scans your asset universe to find high-probability trade setups, filtered by market regime and predefined rules (e.g., "only show momentum trades in trending markets").

**Why it’s useful**:
- Focus on what works: Avoid trades that don’t fit the current market environment.
- Reduce guesswork: Let the tool surface the best opportunities.
- Consistency: Apply the same rules across all assets for unbiased comparisons.

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

**Feature-Specific Guides**:
- [Statistical Edge Engine](docs/2.%20Statistical%20Edge%20Engine.md) – Regime detection & ranking.
- [Data Management](docs/1.%20Data%20Management.md) – Fetch, clean, and validate asset data.
- [News Analysis](docs/8.%20NEWS%20ANALYSIS.md) – Real-time news parsing and impact scoring.
