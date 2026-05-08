from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.panel import Panel
from events.event_engine import EventScanner

console = Console()


def run_event_study():
    """Minimalistic event study UI."""
    from ui.console import console
    
    # Helper functions for formatting values (defined at the top for scope access)
    def format_value(value, suffix="%"):
        if isinstance(value, (int, float)):
            return f"{value:.1f}{suffix}"
        return "N/A"
    
    def format_win_rate(value):
        if isinstance(value, (int, float)):
            return f"{int(value)}%"
        return "N/A"
    
    console.print("🔍 Event Study", style="bold cyan")
    
    # Input ticker with validation to prevent empty/blank entries
    while True:
        ticker = Prompt.ask("Enter ticker symbol").strip().upper()  # Normalize to uppercase & remove spaces
        if ticker and len(ticker) >= 2:  # Ensure non-empty and at least 2 characters
            break
        console.print("[red]Error: Ticker must be at least 2 characters.[/red]")
    
    # Event type selection
    console.print("\n[1] Price Drop Event (-10% default)")
    console.print("[2] Volatility Spike (>2σ default)")
    console.print("[3] Price Surge Event (+5% default)")  # New option
    event_type = Prompt.ask("Choose event type", default="1")
    
    scanner = EventScanner(ticker)
    
    # Run selected scan
    try:
        if event_type == "1":
            # Ask for custom threshold percentage (e.g., 10 for -10%)
            while True:
                threshold_pct = Prompt.ask(
                    "Enter price drop threshold (as %, e.g., 10 for -10%)",
                    default="10"
                )
                try:
                    threshold_pct = float(threshold_pct)
                    if threshold_pct > 0:
                        threshold = -threshold_pct / 100  # Convert to decimal (e.g., 10 → -0.10)
                        event_title = f"{int(-100*threshold)}% Price Drop Events"
                        break
                    console.print("[red]Error: Threshold must be a positive number (e.g., 10 for -10%).[/red]")
                except ValueError:
                    console.print("[red]Error: Please enter a valid number.[/red]")
            results = scanner.scan_price_drops(threshold=threshold)
        elif event_type == "2":
            # Ask for custom sigma multiplier
            while True:
                sigma_input = Prompt.ask(
                    "Enter volatility multiplier (sigma, e.g., 2.0)",
                    default="2.0"
                )
                try:
                    sigma = float(sigma_input)
                    if sigma > 0:
                        event_title = f">{sigma}σ Volatility Events"
                        results = scanner.scan_volatility_spikes(sigma=sigma)
                        break
                except ValueError:
                    console.print("[red]Error: Please enter a valid number.[/red]")
        
        elif event_type == "3":  # Price Surge Event
            while True:
                threshold_pct = Prompt.ask(
                    "Enter price surge threshold (as %, e.g., 5 for +5%)",
                    default="5"
                )
                try:
                    threshold_pct = float(threshold_pct)
                    if threshold_pct > 0:
                        threshold = threshold_pct / 100  # Convert to decimal (e.g., 5 → 0.05)
                        event_title = f"{threshold_pct}% Price Surge Events"
                        results = scanner.scan_price_surges(threshold=threshold)
                        break
                    console.print("[red]Error: Threshold must be a positive number.[/red]")
                except ValueError:
                    console.print("[red]Error: Please enter a valid number.[/red]")
                    continue
    except FileNotFoundError as e:
        console.print(f"[red]✗ No data found for {ticker}[/red]")
        console.print("Use [blue]Data Management → Update All Data[/blue] to fetch data first.")
        input("Press Enter to continue...")
        return
    
    if "error" in results:
        console.print(f"[red]✗ {results['error']}[/red]")
        if results.get("frequency") == 0:
            console.print(f"Tip: Try adjusting thresholds or checking data for {ticker}.")
        input("Press Enter to continue...")
        return
    
    # Display results
    console.print(f"\n📊 {ticker} Event Study: {event_title}", style="bold green")
    console.print(f"[bold yellow]Occorrenza Evento: {results.get('events', 0)}[/bold yellow]")
    
    # Create table with columnDay+1 to Day+5
    table = Table(title="Event Study Results")
    table.add_column("Metric", style="bold")
    table.add_column("Day+1", style="green")
    table.add_column("Day+2", style="green")
    table.add_column("Day+3", style="green")
    table.add_column("Day+4", style="green")
    table.add_column("Day+5", style="green")
    
    # Add mean/average row (formatted as 1.5%, etc.)
    table.add_row("Average", 
                 format_value(results.get("day+1_mean")),
                 format_value(results.get("day+2_mean")),
                 format_value(results.get("day+3_mean")),
                 format_value(results.get("day+4_mean")),
                 format_value(results.get("day+5_mean")))
    
    # Add win rate row (formatted as 65%, etc.)
    table.add_row("Win Rate",
                 format_win_rate(results.get("day+1_win_rate")),
                 format_win_rate(results.get("day+2_win_rate")),
                 format_win_rate(results.get("day+3_win_rate")),
                 format_win_rate(results.get("day+4_win_rate")),
                 format_win_rate(results.get("day+5_win_rate")))
    
    console.print(table)
    
    # Add AI interpretation via LLM
    from core.config_loader import get_config
    
    # Multilingual prompt templates
    PROMPT_TEMPLATES = {
        "italian":"""
        Analizza questi risultati di un Event Study per {ticker} ({event_type}).
        Rispondi SOLO in italiano, massimo 100 parole.
        Considera questi punti:
        1. Sintesi (numero di eventi e frequenza).
        2. Andamenti (rendimenti a Day+1/Day+2 e win rate).
        3. Suggerimenti operativi basati sui dati.
        
        {data}
        """,
        "english":"""
        Analyze these Event Study results for {ticker} ({event_type}).
        Answer ONLY in English, 100 word max.
        Address:
        1. Summary (event count and frequency).
        2. Trends (Day+1/Day+2 returns and win rate).
        3. Actionable suggestions from the data.
        
        {data}
        """
    }
    
    def generate_llm_interpretation():
        try:
            config = get_config()  # Load config from file
            base_url = config.get('llm', {}).get('api_url')
            api_key = config.get('llm', {}).get('api_key')
            if not base_url or not api_key:
                return "[yellow]LLM not configured in config.json[/yellow]"
            
            import requests
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "mistral-small",
                "messages": [{"role": "user", "content": PROMPT_TEMPLATES.get(report_language, PROMPT_TEMPLATES["english"]).format(
                    ticker=ticker, event_type=event_title, data=json.dumps(results, indent=2)
                )}]
            }
            url = base_url.rstrip('/')  # Clean URL
            response = requests.post(url, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            return f"[red]LLM request failed with HTTP {response.status_code}: {response.text}[/red]"
        except Exception as e:
            return f"[red]LLM Error: {str(e)}[/red]"
    
    # Generate and display AI interpretation
    console.print(Panel(
        generate_llm_interpretation(),
        title="[bold blue]🤖 Automated Interpretation[/bold blue]",
        border_style="blue",
        padding=(1, 1),
        expand=True
    ))
    
    # Verbose mode option
    verbose_input = Prompt.ask("\nShow events? (Y/N)", default="N")
    if verbose_input.lower() in ("y", "yes"):
        # Re-run scan to get event details (include Price Surge)
        if event_type == "1":
            event_list = scanner.scan_price_drops(threshold=threshold)
        elif event_type == "2":
            event_list = scanner.scan_volatility_spikes(sigma=sigma)
        else:  # event_type == "3"
            event_list = scanner.scan_price_surges(threshold=threshold)
        if 'event_dates' in event_list:
            dates_table = Table(title="Detailed Events")
            dates_table.add_column("Date", style="cyan")
            dates_table.add_column("Day+1", style="green")
            dates_table.add_column("Day+2", style="green")
            dates_table.add_column("Day+3", style="green")
            dates_table.add_column("Day+4", style="green")
            dates_table.add_column("Day+5", style="green")
            for event in event_list['event_dates']:
                dates_table.add_row(
                    event['date'],
                    f"{event['day+1']:.2%}",
                    f"{event['day+2']:.2%}",
                    f"{event['day+3']:.2%}",
                    f"{event['day+4']:.2%}",
                    f"{event['day+5']:.2%}"
                )
            console.print(dates_table)
        else:
            console.print("[yellow]No event details available.[/yellow]")
    
    # Wait for user input before continuing
    input("Press Enter to continue...")
