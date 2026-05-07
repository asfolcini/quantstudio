# ui/components.py
# ─────────────────────────────────────────────────────────────
# Centralized Rich UI components for QStudio TUI
# All dynamic content MUST pass through these helpers.
# Never use console.print() with raw exceptions outside this file.
# ─────────────────────────────────────────────────────────────

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from rich.text import Text
from rich.columns import Columns
import pandas as pd
from datetime import datetime

console = Console()

# ── Helper Functions ────────────────────────────────────────────

def format_signal(bias: str) -> str:
    """Format bias with emoji + label"""
    return f"🟢 {bias}" if bias == "BUY" else f"🔴 {bias}" if bias == "SELL" else f"🟡 {bias}"

def format_trend(trend: str) -> str:
    """Colorize trend text"""
    return f"[green]{trend}[/green]" if trend == "BULL" else f"[red]{trend}[/red]" if trend == "BEAR" else trend

def format_volatility(vol: str) -> str:
    """Bold volatility if HIGH"""
    return f"[bold]{vol}[/bold]" if vol == "HIGH" else vol

def format_confidence(score: float) -> str:
    """Format confidence level based on score."""
    if score >= 0.8:
        return "HIGH"
    elif score >= 0.6:
        return "MED"
    else:
        return "LOW"

def get_confidence_color(confidence: str) -> str:
    """Get color for confidence level."""
    if confidence == "HIGH":
        return "bold green"
    elif confidence == "MED":
        return "yellow"
    return "red"

def get_levels_display(s1: float, r1: float, last_price: float) -> str:
    """Format S/R levels with proximity emojis"""
    s_distance = abs(last_price - s1) / last_price
    r_distance = abs(last_price - r1) / last_price
    
    if s_distance < 0.02:
        return f"{s1:.1f}⚠️ / {r1:.1f}"
    elif r_distance < 0.02:
        return f"{s1:.1f} / {r1:.1f}⚠️"
    else:
        return f"{s1:.1f} ✅ / {r1:.1f}"


# ── Layout helpers ────────────────────────────────────────────

def print_header(title: str, subtitle: str = None):
    """Top-level screen header."""
    content = f"[bold cyan]{escape(title)}[/bold cyan]"
    if subtitle:
        content += f"\n[dim]{escape(subtitle)}[/dim]"
    console.print(Panel(content, expand=False))


def print_section(title: str):
    """Sub-section separator."""
    console.rule(f"[bold yellow]{escape(title)}[/bold yellow]")


def clear():
    console.clear()


# ── Feedback helpers ──────────────────────────────────────────

def print_error(msg: str, exc: Exception = None):
    """Always use this for exceptions — never console.print(str(e)) directly."""
    text = f"[red]{escape(msg)}"
    if exc:
        text += f": {escape(str(exc))}"
    text += "[/red]"
    console.print(text)


def print_success(msg: str):
    console.print(f"[green]{escape(msg)}[/green]")


def print_warning(msg: str):
    console.print(f"[yellow]{escape(msg)}[/yellow]")


def print_info(msg: str):
    console.print(f"[dim]{escape(msg)}[/dim]")


def pause(msg: str = "Press Enter to continue..."):
    console.input(f"\n[dim]{msg}[/dim]")


# ── Menu builder ──────────────────────────────────────────────

def show_menu(title: str, options: dict[str, str], default: str = "0") -> str:
    """
    Generic menu renderer.

    options = {"0": "Back", "1": "Run analysis", "2": "Settings"}
    Returns the selected key as string.
    """
    table = Table(title=escape(title), box=box.SIMPLE)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Option", style="green")

    for key, label in options.items():
        table.add_row(escape(key), escape(label))

    console.print(table)
    choices = list(options.keys())
    return Prompt.ask("\nSelect option", choices=choices, default=default)


# ── Table builders ────────────────────────────────────────────

def build_kv_table(title: str, rows: list[tuple[str, str]]) -> Table:
    """
    Key-value table.

    rows = [("Trend", "BULLISH"), ("RSI", "67.4")]
    """
    table = Table(title=escape(title), box=box.SIMPLE)
    table.add_column("Field", style="green", min_width=16)
    table.add_column("Value", style="yellow")

    for key, value in rows:
        table.add_row(escape(str(key)), escape(str(value)))

    return table


def build_data_table(title: str, columns: list[str], rows: list[list]) -> Table:
    """
    Generic multi-column data table.

    columns = ["Ticker", "Bias", "Confidence"]
    rows    = [["AAPL", "LONG", "HIGH"], ...]
    """
    table = Table(title=escape(title), box=box.SIMPLE_HEAVY)
    for col in columns:
        table.add_column(escape(col), style="cyan")

    for row in rows:
        table.add_row(*[escape(str(cell)) for cell in row])

    return table


def print_table(table: Table):
    console.print(table)


# ── Edge analysis specific ────────────────────────────────────

def print_edge_report(ticker: str, report: dict):
    """
    Renders a full EdgeEngine report safely.
    All values are escaped — safe even if they contain brackets.
    """
    clear()
    print_header(f"EDGE ANALYSIS — {ticker}")

    q = report.get("quantitative", {})
    regime = q.get("market_regime", {})
    indicators = q.get("indicators", {})
    levels = q.get("levels", {})
    edge = q.get("edge", {})
    decision = q.get("decision", {})

    # Market regime
    print_table(build_kv_table("Market Regime", [
        ("Trend",      regime.get("trend", "N/A")),
        ("Volatility", regime.get("volatility", "N/A")),
        ("ATR",        f"{indicators.get('atr', 0):.2f}"),
    ]))

    # Edge scores
    print_table(build_kv_table("Edge Scores", [
        ("LONG",         edge.get("long_score", "N/A")),
        ("SHORT",        edge.get("short_score", "N/A")),
        ("Risk Penalty", edge.get("risk_penalty", "N/A")),
    ]))

    # Decision
    print_table(build_kv_table("Decision", [
        ("Bias",       decision.get("bias", "N/A")),
        ("Confidence", decision.get("confidence", "N/A")),
    ]))

    # Key indicators
    print_section("Key Indicators")
    console.print(
        f"  EMA20: [cyan]{indicators.get('ema20', 0):.2f}[/cyan]  "
        f"EMA50: [cyan]{indicators.get('ema50', 0):.2f}[/cyan]  "
        f"RSI: [cyan]{indicators.get('rsi', 0):.1f}[/cyan]  "
        f"VWAP: [cyan]{indicators.get('vwap', 0):.2f}[/cyan]"
    )
    console.print(
        f"  Support:    [green]{levels.get('s1', 0):.2f}[/green] / "
        f"[green]{levels.get('s2', 0):.2f}[/green]"
    )
    console.print(
        f"  Resistance: [red]{levels.get('r1', 0):.2f}[/red] / "
        f"[red]{levels.get('r2', 0):.2f}[/red]"
    )

def print_edge_report_horizontal(ticker: str, report: dict, df: pd.DataFrame):
    """Horizontal three-table layout + LLM summary below. Safe from inline markup."""
    clear()
    
    # Load metadata for ticker
    from data.metadata import load_metadata
    metadata = load_metadata(ticker)
    short_name = metadata.get("short_name", "")
    
    # Build title panel with ticker name and company name inline
    title_text = f"[bold cyan]EDGE ANALYSIS — {ticker}[/bold cyan]"
    if short_name:
        title_text += f" [italic]— {short_name}[/italic]"  # Italics on same line with em dash separator
    title_panel = Panel(title_text, style="bold magenta", expand=False)
    console.print(title_panel)
    
    # Extract last OHLCV row
    if df is not None and not df.empty:
        last_row = df.iloc[-1]
        
        # --- FIX: Robust date extraction ---
        if isinstance(last_row.name, pd.Timestamp):
            date = last_row.name.strftime("%Y-%m-%d")
        elif isinstance(last_row.name, str):
            date = pd.to_datetime(last_row.name).strftime("%Y-%m-%d")
        else:
            # Fallback: Use the 'datetime' column if index is not a timestamp
            date = df['datetime'].iloc[-1].strftime("%Y-%m-%d")
        
        def format_price(price):
            try:
                price = float(price)
                if price >= 1:
                    return f"{price:.2f}"
                elif price >= 0.01:
                    return f"{price:.4f}"
                else:
                    return f"{price:.6f}"
            except:
                return "N/A"
        
        open_price = format_price(last_row['open'])
        high_price = format_price(last_row['high'])
        low_price = format_price(last_row['low'])
        close_price = format_price(last_row['close'])
        volume = f"{last_row['volume']:,}" if not pd.isna(last_row.get('volume')) else "N/A"
        
        # --- FIX: Use Text.assemble for proper styling ---
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
        ohlcv_panel = Panel(
            ohlcv_text,
            border_style="yellow",
            expand=False,
            padding=(0, 1)
         )
        console.print(ohlcv_panel)

    from ui.format_llm_output import format_llm_output_rich

    q = report.get('quantitative', {})
    regime = q.get('market_regime', {})
    indicators = q.get('indicators', {})
    levels = q.get('levels', {})
    edge = q.get('edge', {})
    decision = q.get('decision', {})

    # Three focused tables arranged horizontally
    regime_tbl = build_kv_table("Market Regime", [
        ("Trend", regime.get("trend", "N/A")),
        ("Volatility", regime.get("volatility", "N/A")),
        ("ATR", f"{indicators.get('atr', 0):.2f}")
    ])

    edge_tbl = build_kv_table("Edge Scores", [
        ("LONG", edge.get("long_score", "N/A")),
        ("SHORT", edge.get("short_score", "N/A")),
        ("Risk Penalty", edge.get("risk_penalty", "N/A"))
    ])

    dec_tbl = build_kv_table("Decision", [
        ("Bias", decision.get("bias", "N/A")),
        ("Confidence", decision.get("confidence", "N/A"))
    ])

    key_tbl = build_kv_table("Key Indicators", [
        ("EMA20", indicators.get("ema20", 0)),
        ("EMA50", indicators.get("ema50", 0)),
        ("RSI", indicators.get("rsi", 0)),
    ])

    # Horizontal layout
    console.print(Columns([regime_tbl, edge_tbl, dec_tbl, key_tbl]))

    # LLM summary below tables
    llm_summary = report.get('llm_interpretation')
    if llm_summary and llm_summary != 'LLM REPORT UNAVAILABLE':
        console.print(Panel(format_llm_output_rich(llm_summary), title="AI Summary", border_style="blue", expand=True))
    else:
        console.print(Panel("(No AI interpretation)", style="dim"))


def print_universe_screener(universe_name: str, sorted_reports: pd.DataFrame, top_n=10):
    """Display universe screener with all requested fields"""
    # Sort: Confidence > Bias > Trend > RSI > Edge
    sort_level = {"HIGH": 0, "MED": 1, "Low": 2}
    sorted_reports["confidence_rank"] = sorted_reports["confidence"].map(sort_level)
    sorted_reports["bias_rank"] = sorted_reports["bias"].map({"BUY": 0, "SELL": 1, "WAIT": 2})
    sorted_reports["vol_rank"] = pd.Series(sorted_reports.get("volatility", "MED")).map({"HIGH": 0, "MED": 1, "LOW": 2})
    sorted_reports = sorted_reports.sort_values(["confidence_rank", "bias_rank", "vol_rank"])
    
    # Main table: Signals, Bias, Conf, Ticker, Trend, Volatility, RSI
    table = Table(title=f"📊 UNIVERSE SCREENER — {universe_name} (Top {min(top_n, len(sorted_reports))}/{len(sorted_reports)})")
    table.add_column("#", style="grey", width=3)
    table.add_column("SIGNAL", style="bold", width=9)
    table.add_column("BIAS", width=6)
    table.add_column("CONF", width=6)
    table.add_column("TICKER", style="bold cyan", width=8)
    table.add_column("TREND", width=7)
    table.add_column("VOL", width=5)
    table.add_column("RSI", width=6)
    
    for idx, (idx_sm, row) in enumerate(sorted_reports.head(top_n).iterrows()):
        table.add_row(
            str(idx + 1),
            format_signal(row["bias"]),
            row["bias"],
            row["confidence"],
            row["ticker"],
            format_trend(row.get("trend", "NONE")),
            format_volatility(row.get("volatility", "MED")),
            f"[red]{row['rsi']:.1f}[/]" if row["rsi"] > 70 else
                f"[green]{row['rsi']:.1f}[/]" if row["rsi"] < 30 else
                f"{row['rsi']:.1f}"
        )
    
    console.print(table)
    
    # Secondary table: Last Price, Close Price, Last Date
    detail_table = Table(show_header=False)
    detail_table.add_column("Last Price", min_width=15)
    detail_table.add_column("Close Price", min_width=15)
    detail_table.add_column("Last Date", min_width=12)
    
    for _, row in sorted_reports.head(10).iterrows():
        detail_table.add_row(
            f"{row['last_price']:.2f}" if pd.notna(row.get('last_price')) else "N/A",
            f"{row['close_price']:.2f}" if pd.notna(row.get('close_price')) else "N/A",
            row.get('last_date', 'N/A')
        )
    
    console.print(detail_table)
    
    # Footer: S/R Levels
    s_r_summaries = []
    for _, row in sorted_reports.head(10).iterrows():
        if pd.notna(row.get('s1')) and pd.notna(row.get('r1')) and pd.notna(row.get('last_price')):
            s_r_summaries.append(
                f"{row['ticker']}: {get_levels_display(row['s1'], row['r1'], row['last_price'])}"
            )
    
    console.print(Panel("² S/R Levels: " + " | ".join(s_r_summaries), border_style="dim", expand=False))
