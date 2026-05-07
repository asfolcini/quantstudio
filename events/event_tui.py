from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from events.event_engine import EventScanner

console = Console()


def run_event_study():
    """Minimalistic event study UI."""
    from ui.console import console
    
    console.print("🔍 Event Study", style="bold cyan")
    
    ticker = Prompt.ask("Enter ticker symbol")
    
    # Event type selection
    console.print("\n[1] Price Drop Event (-10% default)")
    console.print("[2] Volatility Spike (>2σ default)")
    event_type = Prompt.ask("Choose event type", default="1")
    
    scanner = EventScanner(ticker)
    
    # Run selected scan
    try:
        if event_type == "1":
            threshold = -0.10  # -10%
            results = scanner.scan_price_drops(threshold=threshold)
            event_title = f"{int(-100*threshold)}% Price Drop Events"
        else:
            sigma = 2.0
            results = scanner.scan_volatility_spikes(sigma=sigma)
            event_title = f">{sigma}σ Volatility Events"
    except FileNotFoundError as e:
        console.print(f"[red]✗ No data found for {ticker}[/red]")
        console.print("Use [blue]Data Management → Update All Data[/blue] to fetch data first.")
        return
    
    if "error" in results:
        console.print(f"[red]✗ {results['error']}[/red]")
        if results.get("frequency") == 0:
            console.print(f"Tip: Try adjusting thresholds or checking data for {ticker}.")
        return
    
    # Display results
    console.print(f"\n📊 {ticker} Event Study: {event_title}", style="bold green")
    table = Table(title="Event Study Results")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="green")
    table.add_row("Frequency", results.get("frequency", "N/A"))
    table.add_row("Day+1 Median", results.get("day+1_median", "N/A"))
    table.add_row("Win Rate", results.get("win_rate", "N/A"))
    console.print(table)
