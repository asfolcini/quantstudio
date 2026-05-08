from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from core.config_loader import get_config, update_config
from ui.console import console
from datetime import date
from rich.text import Text
from core.global_var import BUILD,URL,URL_TITLE

def show_main_menu() -> int:
    """
    Display main menu and return selected option.
    
    Returns:
        Integer option (0 or 1)
    """
    console.clear()

    today = date.today().strftime("%d %B %Y")

    content = Text.assemble(
        ("QuantStudio", "bold cyan"),
        " - Quant Analysis Tool\n",
        (f"{today}  - BUILD {BUILD}  -  ", "dim"),
        (f"{URL_TITLE}", f"link {URL}"),
    )

    console.print(Panel(content, expand=False))

    table = Table(title="Main Menu")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Option", style="green")
    
    table.add_row("0", "Exit")
    table.add_row("1", "DATA MANAGEMENT")
    table.add_row("2", "STATISTICAL EDGE ENGINE")
    table.add_row("3", "EVENT STUDY")
    table.add_row("9", "Configuration")
    
    console.print(table)
    
    choice = IntPrompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "9"])
    return choice


def show_config_menu():
    """
    Display and handle configuration menu.
    """
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Configuration[/bold cyan]", expand=False))
        
        table = Table(title="Configuration Options")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Option", style="green")
        
        table.add_row("1", "View current settings")
        table.add_row("2", "Change data provider")
        table.add_row("3", "Change report language")
        table.add_row("4", "Change news region")
        table.add_row("5", "Change LLM API")
        table.add_row("6", "Test LLM")
        table.add_row("0", "Back")
        
        console.print(table)
        
        choices = ["0", "1", "2", "3", "4", "5", "6"]
        choice = IntPrompt.ask("\nSelect option", choices=choices)
        
        if choice == 0:
            return
        
        config = get_config()
        
        if choice == 1:
            # View current settings
            console.clear()
            console.print(Panel("[bold cyan]CURRENT SETTINGS[/bold cyan]", expand=False))
            
            table = Table(title="Configuration")
            table.add_column("Key", style="green")
            table.add_column("Value", style="yellow")
            
            # LLM settings
            llm_url = config['llm']['api_url']
            llm_key_masked = config['llm']['api_key'][:4] + "***" + config['llm']['api_key'][-6:]
            table.add_row("LLM API URL", llm_url)
            table.add_row("LLM API Key", llm_key_masked)
            
            # Other settings
            table.add_row("Data Provider", config['data_provider'])
            table.add_row("Report Language", config['report_language'])
            table.add_row("News Region", config['news_region'])
            
            console.print(table)
            console.input("\nPress Enter to continue...")
            
        elif choice == 2:
            # Change data provider (only YAHOO supported)
            console.clear()
            console.print("[yellow]Only YAHOO provider is supported at this time.[/yellow]")
            console.input("\nPress Enter to continue...")
            
        elif choice == 3:
            # Change report language
            from core.ui_mappings import LANGUAGE_MAP, DEFAULT_LANGUAGE
            
            console.clear()
            console.print("[bold cyan]Available Languages:[/bold cyan]")
            for i, lang in LANGUAGE_MAP.items():
                console.print(f"[{i}] {lang.capitalize()}")
            console.print("[0] Back")
            
            while True:
                try:
                    # Get valid choices as strings from LANGUAGE_MAP keys
                    valid_choices = [str(k) for k in LANGUAGE_MAP.keys()]
                    valid_choices.append("0")  # Add back option
                    
                    choice_input = Prompt.ask("\nSelect language", default=str(DEFAULT_LANGUAGE), choices=valid_choices)
                    if not choice_input.strip():
                        choice_input = str(DEFAULT_LANGUAGE)
                    
                    lang_num = int(choice_input)
                    
                    if lang_num == 0:
                        break
                    
                    if lang_num in LANGUAGE_MAP:
                        lang_choice = LANGUAGE_MAP[lang_num]
                        update_config("report_language", lang_choice)
                        console.print(f"[green]Report language updated to {lang_choice}[/green]")
                        break
                    else:
                        console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 4:
            # Change news region
            from core.ui_mappings import REGION_MAP, DEFAULT_REGION
            
            console.clear()
            console.print("[bold cyan]Available Regions:[/bold cyan]")
            for i, region in REGION_MAP.items():
                console.print(f"[{i}] {region}")
            console.print("[0] Back")
            
            while True:
                try:
                    choice_input = Prompt.ask("\nSelect region", default=str(DEFAULT_REGION))
                    if not choice_input.strip():
                        choice_input = str(DEFAULT_REGION)
                    
                    region_num = int(choice_input)
                    
                    if region_num == 0:
                        break
                    
                    if region_num in REGION_MAP:
                        region_choice = REGION_MAP[region_num]
                        update_config("news_region", region_choice)
                        console.print(f"[green]News region updated to {region_choice}[/green]")
                        break
                    else:
                        console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 5:
            # Change LLM API
            console.clear()
            console.print("[bold cyan]LLM API Configuration[/bold cyan]")
            
            new_url = Prompt.ask("Enter new LLM API URL", default=config['llm']['api_url'])
            new_key = Prompt.ask("Enter new LLM API Key", default=config['llm']['api_key'])
            
            if not new_key.strip():
                console.print("[red]API key cannot be empty.[/red]")
                console.input("\nPress Enter to continue...")
                continue
            
            update_config("llm.api_url", new_url)
            update_config("llm.api_key", new_key)
            console.print("[green]LLM API settings updated successfully.[/green]")
            console.input("\nPress Enter to continue...")
        
        elif choice == 6:
            # Test LLM
            console.clear()
            console.print("[bold cyan]TESTING LLM CONNECTION[/bold cyan]")
            
            # Get LLM config
            llm_url = config['llm']['api_url']
            llm_key = config['llm']['api_key']
            
            # Mask key for display
            llm_key_masked = llm_key[:4] + "***" + llm_key[-6:]
            console.print(f"Testing connection to: {llm_url}")
            console.print(f"Using API key: {llm_key_masked}")
            console.print("")
            
            # Send test request
            import requests
            import time
            
            try:
                # Show spinner during request
                with console.status("[bold yellow]Testing LLM...", spinner="dots"):
                    start_time = time.time()
                    
                    response = requests.post(
                        llm_url,
                        headers={
                            "Authorization": f"Bearer {llm_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "hi there, are you there ?"
                                }
                            ]
                        },
                        timeout=10
                    )
                    
                    response_time = time.time() - start_time
                    
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract assistant response
                    if "choices" in result and len(result["choices"]) > 0:
                        message = result["choices"][0]["message"]["content"]
                        
                        # Display success panel
                        panel_content = f"[green]✓ Success![/green]\n\n[bold]Response:[/bold]\n{message}\n\n[bold]Latency:[/bold] {response_time:.2f}s"
                        
                        console.print(Panel(panel_content, title="LLM Test Result", border_style="green"))
                    else:
                        console.print(Panel("[red]✗ Failed: Unexpected response format[/red]", title="LLM Test Result", border_style="red"))
                else:
                    console.print(Panel(f"[red]✗ Failed: HTTP {response.status_code}[/red]\n\n{response.text}", title="LLM Test Result", border_style="red"))
                    
            except requests.exceptions.Timeout:
                console.print(Panel("[red]✗ Failed: Request timed out (10s)[/red]", title="LLM Test Result", border_style="red"))
            except requests.exceptions.ConnectionError:
                console.print(Panel("[red]✗ Failed: Could not connect to LLM endpoint[/red]", title="LLM Test Result", border_style="red"))
            except requests.exceptions.RequestException as e:
                console.print(Panel(f"[red]✗ Failed: {str(e)}[/red]", title="LLM Test Result", border_style="red"))
            except Exception as e:
                console.print(Panel(f"[red]✗ Failed: {str(e)}[/red]", title="LLM Test Result", border_style="red"))
            
            console.input("\nPress Enter to continue...")

def show_data_management_menu():
    """
    Display data management menu and handle user choices.
    """
    while True:
        console.clear()
        console.print(Panel("[bold cyan]DATA MANAGEMENT[/bold cyan]", expand=False))
        
        table = Table(title="Data Management Options")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Option", style="green")
        
        table.add_row("1", "List all tickers")
        table.add_row("2", "Add new ticker")
        table.add_row("3", "Remove ticker")
        table.add_row("4", "Update All data")
        table.add_row("5", "Inspect data")
        table.add_row("6", "Manage universes")
        table.add_row("0", "Back")
        
        console.print(table)
        
        choices = [str(i) for i in range(7)]
        choice = IntPrompt.ask("\nSelect option", choices=choices)
        
        if choice == 0:
            return
        
        elif choice == 1:
            # List all tickers
            from ui.core import get_ticker_summary
            ticker_summary = get_ticker_summary()
            
            console.clear()
            console.print(Panel("[bold cyan]AVAILABLE TICKERS[/bold cyan]", expand=False))
            
            if not ticker_summary:
                console.print("[yellow]No tickers found in historical_data directory.[/yellow]")
                console.input("\nPress Enter to continue...")
                continue
            
            table = Table(title="Tickers")
            table.add_column("Ticker", style="green")
            table.add_column("Name", style="cyan")
            table.add_column("Exchange", style="magenta")
            table.add_column("First Date", style="yellow")
            table.add_column("Last Date", style="yellow")
            
            for ticker_info in ticker_summary:
                table.add_row(
                    ticker_info["ticker"],
                    ticker_info["name"],
                    ticker_info["exchange"] if ticker_info["exchange"] else "N/A",
                    str(ticker_info["first_date"])[:10] if ticker_info["first_date"] else "N/A",
                    str(ticker_info["last_date"])[:10] if ticker_info["last_date"] else "N/A"
                )
                 
            console.print(table)
            console.input("\nPress Enter to continue...")
            
        elif choice == 2:
            # Add new ticker
            tickers_input = Prompt.ask("\nEnter ticker symbol(s) (comma-separated for multiple)")
            
            if not tickers_input.strip():
                console.print("[red]Ticker symbol cannot be empty.[/red]")
                console.input("\nPress Enter to continue...")
                continue
            
            from ui.core import add_ticker
            
            # Split input by commas and strip whitespace
            tickers_to_add = [t.strip().upper() for t in tickers_input.split(',')]
            
            # Filter out empty entries
            tickers_to_add = [t for t in tickers_to_add if t]
            
            if not tickers_to_add:
                console.print("[red]No valid ticker symbols provided.[/red]")
                console.input("\nPress Enter to continue...")
                continue
            
            # Add each ticker individually
            success_count = 0
            for ticker in tickers_to_add:
                if add_ticker(ticker):
                    console.print(f"[green]Ticker {ticker} added successfully.[/green]")
                    success_count += 1
                else:
                    console.print(f"[yellow]Ticker {ticker} already exists.[/yellow]")
            
            if success_count > 0:
                console.print(f"[green]Successfully added {success_count} of {len(tickers_to_add)} tickers.[/green]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 3:
            # Remove ticker
            ticker = Prompt.ask("\nEnter ticker symbol to remove")
            
            if not ticker.strip():
                console.print("[red]Ticker symbol cannot be empty.[/red]")
                console.input("\nPress Enter to continue...")
                continue
            
            from ui.core import remove_ticker
            if remove_ticker(ticker):
                console.print(f"[green]Ticker {ticker} removed successfully.[/green]")
            else:
                console.print(f"[yellow]Ticker {ticker} does not exist.[/yellow]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 4:
            # Update All data
            console.clear()
            console.print(Panel("[bold cyan]UPDATE ALL DATA[/bold cyan]", expand=False))
            
            # Ask for sync mode
            console.print("[bold green]Choose sync mode:[/bold green]")
            console.print("[1] Full Sync (reload all data, delete existing)")
            console.print("[2] Delta Sync (append only missing data)")
            
            mode_choice = Prompt.ask("Select mode (1-2)", default="2")
            
            if mode_choice == "1":
                mode = "full"
            else:
                mode = "update"
            
            console.print(f"[yellow]Selected mode: {mode.capitalize()} Sync[/yellow]")
            console.print("[yellow]Starting data update...[/yellow]")
            
            from ui.core import update_all_data
            try:
                # Show progress spinner during update
                with console.status(f"[bold yellow]Updating all tickers in {mode} mode...", spinner="dots"):
                    result = update_all_data(mode)
                
                console.clear()
                console.print(Panel(f"[bold cyan]UPDATE ALL DATA RESULTS[/bold cyan]", expand=False))
                
                table = Table(title="Summary")
                table.add_column("Metric", style="green")
                table.add_column("Value", style="yellow")
                
                table.add_row("Tickers processed", str(result['processed']))
                table.add_row("Successful updates", str(result['success']))
                table.add_row("Failed updates", str(result['failed']))
                
                console.print(table)
                
                # Show detailed results
                if result['processed'] > 0:
                    console.print("\n[bold green]Detailed Results:[/bold green]")
                    for ticker, ticker_result in result['tickers'].items():
                        if 'error' in ticker_result:
                            console.print(f"[red]{ticker}: ERROR - {ticker_result['error']}[/red]")
                        else:
                            rows = ticker_result.get('rows', 0)
                            date_range = ticker_result.get('date_range', 'N/A')
                            console.print(f"[green]{ticker}: {rows} rows, {date_range}[/green]")
            except Exception as e:
                console.print(f"[red]Error updating all data: {e}[/red]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 5:
            # Inspect data
            ticker = Prompt.ask("\nEnter ticker symbol")
            
            if not ticker.strip():
                console.print("[red]Ticker symbol cannot be empty.[/red]")
                console.input("\nPress Enter to continue...")
                continue
            
            from ui.core import inspect_data
            try:
                console.clear()
                with console.status(f"[bold yellow]Loading data for {ticker}...", spinner="dots"):
                    data = inspect_data(ticker)
                
                console.clear()
                console.print(Panel(f"[bold cyan]DATA INSPECTION - {ticker}[/bold cyan]", expand=False))
                
                if not data['last_10_rows']:
                    console.print(f"[yellow]No data available for {ticker}.[/yellow]")
                else:
                    table = Table(title="Last 10 Rows")
                    table.add_column("Date", style="cyan")
                    table.add_column("Open", style="green")
                    table.add_column("High", style="green")
                    table.add_column("Low", style="green")
                    table.add_column("Close", style="green")
                    table.add_column("Volume", style="yellow")
                    
                    for row in data['last_10_rows']:
                        table.add_row(
                            str(row['datetime'])[:10],
                            f"{row['open']:.2f}",
                            f"{row['high']:.2f}",
                            f"{row['low']:.2f}",
                            f"{row['close']:.2f}",
                            f"{int(row['volume']):,}"
                        )
                    
                    console.print(table)
                
                if data['metadata']:
                    console.print("\n[bold cyan]Metadata:[/bold cyan]")
                    for key, value in data['metadata'].items():
                        console.print(f"  {key}: {value}")
            except Exception as e:
                console.print(f"[red]Error inspecting data: {e}[/red]")
            
            console.input("\nPress Enter to continue...")
            
            from ui.core import inspect_data
            try:
                data = inspect_data(ticker)
                
                console.clear()
                console.print(Panel(f"[bold cyan]DATA INSPECTION - {ticker}[/bold cyan]", expand=False))
                
                if not data['last_10_rows']:
                    console.print(f"[yellow]No data available for {ticker}.[/yellow]")
                else:
                    table = Table(title="Last 10 Rows")
                    table.add_column("Date", style="cyan")
                    table.add_column("Open", style="green")
                    table.add_column("High", style="green")
                    table.add_column("Low", style="green")
                    table.add_column("Close", style="green")
                    table.add_column("Volume", style="yellow")
                    
                    for row in data['last_10_rows']:
                        table.add_row(
                            str(row['datetime'])[:10],
                            f"{row['open']:.2f}",
                            f"{row['high']:.2f}",
                            f"{row['low']:.2f}",
                            f"{row['close']:.2f}",
                            f"{int(row['volume']):,}"
                        )
                    
                    console.print(table)
                
                if data['metadata']:
                    console.print("\n[bold cyan]Metadata:[/bold cyan]")
                    for key, value in data['metadata'].items():
                        console.print(f"  {key}: {value}")
                
            except Exception as e:
                console.print(f"[red]Error inspecting data: {e}[/red]")
            
            console.input("\nPress Enter to continue...")
            
        elif choice == 6:
            # Manage universes
            from core.universe_manager import load_universes
            
            while True:
                console.clear()
                console.print(Panel("[bold cyan]UNIVERSE MANAGEMENT[/bold cyan]", expand=False))
                
                table = Table(title="Universe Options")
                table.add_column("#", style="cyan", width=3)
                table.add_column("Option", style="green")
                
                table.add_row("1", "List all universes")
                table.add_row("2", "Create new universe")
                table.add_row("3", "Add ticker to universe")
                table.add_row("4", "Remove ticker from universe")
                table.add_row("5", "Delete universe")
                table.add_row("0", "Back")
                
                console.print(table)
                
                choices = [str(i) for i in range(7)]
                choice = IntPrompt.ask("\nSelect option", choices=choices)
                
                if choice == 0:
                    break
                
                elif choice == 1:
                    # List all universes
                    from core.universe_manager import load_universes
                    from data.metadata import load_metadata
                    
                    universes = load_universes()
                    
                    console.clear()
                    console.print(Panel("[bold cyan]AVAILABLE UNIVERSES[/bold cyan]", expand=False))
                    
                    if not universes:
                        console.print("[yellow]No universes defined.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    # Show each universe with its tickers in detail
                    for universe_name, ticker_list in sorted(universes.items()):
                        console.print(f"\n[bold green]{universe_name} ({len(ticker_list)} tickers)[/bold green]")
                        
                        if len(ticker_list) > 0:
                            # Create detailed table for each universe's tickers
                            ticker_table = Table(title=" ", show_header=True)
                            ticker_table.add_column("Ticker", style="green")
                            ticker_table.add_column("Name", style="cyan")
                            ticker_table.add_column("Exchange", style="magenta")
                            
                            for ticker in sorted(ticker_list):
                                metadata = load_metadata(ticker)
                                exchange = metadata.get("exchange", "N/A")
                                name = metadata.get("name", "N/A")
                                
                                ticker_table.add_row(ticker, name, exchange)
                            
                            console.print(ticker_table)
                        else:
                            console.print("  [yellow]No tickers in this universe[/yellow]")
                    
                    console.input("\nPress Enter to continue...")
                    
                elif choice == 2:
                    # Create new universe
                    name = Prompt.ask("\nEnter universe name")
                    
                    if not name.strip():
                        console.print("[red]Universe name cannot be empty.[/red]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    universes = load_universes()
                    
                    if name in universes:
                        console.print(f"[yellow]Universe {name} already exists.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    universes[name] = []
                    from core.universe_manager import save_universes
                    save_universes(universes)
                    console.print(f"[green]Universe {name} created successfully.[/green]")
                    console.input("\nPress Enter to continue...")
                    
                elif choice == 3:
                    # Add ticker to universe
                    universes = load_universes()
                    
                    if not universes:
                        console.print("[yellow]No universes defined. Create a universe first.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    console.clear()
                    console.print("[bold cyan]AVAILABLE UNIVERSES:[/bold cyan]")
                    universe_list = sorted(universes.keys())
                    for i, name in enumerate(universe_list, 1):
                        console.print(f"[{i}] {name}")
                    console.print("[0] Back")
                    
                    while True:
                        try:
                            choice_input = Prompt.ask("\nSelect universe", default="1")
                            if not choice_input.strip():
                                choice_input = "1"
                            
                            universe_num = int(choice_input)
                            
                            if universe_num == 0:
                                break
                            
                            if 1 <= universe_num <= len(universe_list):
                                 universe_name = universe_list[universe_num - 1]
                                 tickers_input = Prompt.ask("Enter ticker symbol(s) to add (comma-separated for multiple)")
                                 
                                 if not tickers_input.strip():
                                     console.print("[red]Ticker symbol cannot be empty.[/red]")
                                     continue
                                 
                                 from core.universe_manager import add_ticker
                                 
                                 # Split input by commas and strip whitespace
                                 tickers_to_add = [t.strip().upper() for t in tickers_input.split(',')]
                                 
                                 # Filter out empty entries
                                 tickers_to_add = [t for t in tickers_to_add if t]
                                 
                                 if not tickers_to_add:
                                     console.print("[red]No valid ticker symbols provided.[/red]")
                                     continue
                                 
                                 # Add each ticker individually
                                 success_count = 0
                                 for ticker in tickers_to_add:
                                     if add_ticker(universe_name, ticker):
                                         console.print(f"[green]Ticker {ticker} added to {universe_name} successfully.[/green]")
                                         success_count += 1
                                     else:
                                         console.print(f"[yellow]Failed to add {ticker} to {universe_name} (universe doesn't exist or ticker already exists)[/yellow]")
                                 
                                 if success_count > 0:
                                     console.print(f"[green]Successfully added {success_count} of {len(tickers_to_add)} tickers.[/green]")
                                 
                                 break
                            else:
                                console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
                        except ValueError:
                            console.print("[red]Please enter a valid number.[/red]")
                    
                    console.input("\nPress Enter to continue...")
                    
                elif choice == 4:
                    # Remove ticker from universe
                    universes = load_universes()
                    
                    if not universes:
                        console.print("[yellow]No universes defined.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    console.clear()
                    console.print("[bold cyan]AVAILABLE UNIVERSES:[/bold cyan]")
                    universe_list = sorted(universes.keys())
                    for i, name in enumerate(universe_list, 1):
                        console.print(f"[{i}] {name}")
                    console.print("[0] Back")
                    
                    while True:
                        try:
                            choice_input = Prompt.ask("\nSelect universe", default="1")
                            if not choice_input.strip():
                                choice_input = "1"
                            
                            universe_num = int(choice_input)
                            
                            if universe_num == 0:
                                break
                            
                            if 1 <= universe_num <= len(universe_list):
                                universe_name = universe_list[universe_num - 1]
                                ticker = Prompt.ask("Enter ticker symbol to remove")
                                
                                if not ticker.strip():
                                    console.print("[red]Ticker symbol cannot be empty.[/red]")
                                    continue
                                
                                from core.universe_manager import remove_ticker
                                if remove_ticker(universe_name, ticker):
                                    console.print(f"[green]Ticker {ticker} removed from {universe_name} successfully.[/green]")
                                else:
                                    console.print(f"[yellow]Failed to remove {ticker} from {universe_name} (universe doesn't exist or ticker not found)[/yellow]")
                                break
                            else:
                                console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
                        except ValueError:
                            console.print("[red]Please enter a valid number.[/red]")
                    
                    console.input("\nPress Enter to continue...")
                    
                elif choice == 5:
                    # Delete universe
                    universes = load_universes()
                    
                    if not universes:
                        console.print("[yellow]No universes defined.[/yellow]")
                        console.input("\nPress Enter to continue...")
                        continue
                    
                    console.clear()
                    console.print("[bold cyan]AVAILABLE UNIVERSES:[/bold cyan]")
                    universe_list = sorted(universes.keys())
                    for i, name in enumerate(universe_list, 1):
                        console.print(f"[{i}] {name}")
                    console.print("[0] Back")
                    
                    while True:
                        try:
                            choice_input = Prompt.ask("\nSelect universe to delete", default="1")
                            if not choice_input.strip():
                                choice_input = "1"
                            
                            universe_num = int(choice_input)
                            
                            if universe_num == 0:
                                break
                            
                            if 1 <= universe_num <= len(universe_list):
                                universe_name = universe_list[universe_num - 1]
                                
                                confirm = Prompt.ask(f"Are you sure you want to delete universe '{universe_name}'? (yes/no)", default="no")
                                if confirm.lower() == "yes":
                                    from core.universe_manager import delete_universe
                                    if delete_universe(universe_name):
                                        console.print(f"[green]Universe {universe_name} deleted successfully.[/green]")
                                    else:
                                        console.print(f"[yellow]Failed to delete {universe_name} (universe doesn't exist)[/yellow]")
                                else:
                                    console.print("[yellow]Deletion cancelled.[/yellow]")
                                break
                            else:
                                console.print("[red]Invalid selection. Please choose a number from the list.[/red]")
                        except ValueError:
                            console.print("[red]Please enter a valid number.[/red]")
                    
                    console.input("\nPress Enter to continue...")

def show_edge_engine_menu():
    """
    Display statistical edge engine menu and handle user choices.
    Follows clean pattern: clear() -> print_header() -> show_menu() -> process -> pause()
    """
    from ui.components import clear, print_header, pause, print_error
    from ui.components import show_menu, print_edge_report
    from edge_engine import EdgeEngine
    from ui.core import inspect_data
    import os
    import pandas as pd

    while True:
        clear()
        print_header("STATISTICAL EDGE ENGINE")

        MENU_OPTIONS = {
            "1": "Run on single ticker",
            "2": "Run on universe",
            "3": "Edge Discoverer",
            "0": "Back"
        }

        ch = show_menu("Edge Engine Options", MENU_OPTIONS, "0")

        if ch == "0":
            return
        elif ch == "2":
            run_on_universe()


        elif ch == "3":  # Edge Discoverer
            clear()
            print_header("EDGE DISCOVERER - Setup Finder")
            
            ticker = Prompt.ask("\nEnter ticker symbol")
            if not ticker.strip():
                print_error("Ticker symbol cannot be empty")
                pause()
                continue
                
            # Try to load data for the ticker
            try:
                from ui.core import inspect_data
                data = inspect_data(ticker)
                
                if not data.get('last_10_rows'):
                    print_error(f"No data available for {ticker}")
                    pause()
                    continue
                    
                # Load full OHLCV data
                historical_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
                csv_path = os.path.join(historical_dir, ticker, "data.csv")
                
                if not os.path.exists(csv_path):
                    print_error(f"No full data file found for {ticker}")
                    pause()
                    continue
                    
                # Read and prepare data
                df = pd.read_csv(csv_path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)  # Set datetime as index
                df.sort_index(inplace=True)  # Ensure ascending order
                print(f"Loaded {len(df)} observations for {ticker}")
                
                # Run setup_engine
                console.print("[yellow]Running Setup Finder...[/yellow]")
                 
                with console.status("[bold yellow]Analyzing setups...", spinner="dots"):
                    from setup_engine.runner import run as run_setup_engine
                    result = run_setup_engine(df, ticker)
                    
                # Display results as JSON
                clear()
                print_header(f"SETUP FINDER RESULTS - {ticker}")

                display_edge_discover_rich(result)
                
            except ImportError:
                print_error("Setup Engine not available")
            except Exception as exc:
                print_error(f"Edge Discoverer Error: {str(exc)}")
                import traceback
                traceback.print_exc()
                
            pause()
        
        elif ch == "1":  # Single ticker analysis
            ticker = Prompt.ask("\nEnter ticker symbol")
            if not ticker.strip():
                print_error("Ticker symbol cannot be empty")
                pause()
                continue
            
            try:
                # Step 1: Validate data exists via inspect_data
                from ui.core import inspect_data
                from edge_engine import EdgeEngine
                
                data = inspect_data(ticker)
                if not data.get('last_10_rows'):
                    print_error(f"No data available for {ticker}")
                    pause()
                    continue
                
                # Step 2: Load full OHLCV data for deep analysis (needs >20 rows)
                historical_dir = "/Users/alberto.sfolcini/Development/quantstudio/historical_data"
                csv_path = os.path.join(historical_dir, ticker, "data.csv")
                
                if not os.path.exists(csv_path):
                    print_error(f"No full data file found for {ticker}")
                    pause()
                    continue
                
                # Read CSV and ensure datetime column
                df = pd.read_csv(csv_path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                print(f"Loaded {len(df)} observations for {ticker}")
                
                # Step 3: Generate quantitative report
                try:
                    engine = EdgeEngine(df)
                    report = engine.generate_report()
                except Exception as exc:
                    print_error("Edge engine computation failed", exc)
                    pause()
                    continue
                
                # Step 4: Render using horizontal table layout
                from ui.components import print_edge_report_horizontal
                print_edge_report_horizontal(ticker, report, df)
                pause()

            except Exception as exc:
                print_error("Unexpected error during edge analysis", exc)
                pause()

def display_edge_discover_rich(result: dict) -> None:
    """
    Display edge Discoverer results in a rich multi-panel layout.
    Shows top strategies, their metrics, and setup rules.
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich import box
    console = Console()
    # Check if results are empty
    if not result or 'top_setups' not in result or not result['top_setups']:
        console.print(Panel("[bold red]NO VALID SETUPS FOUND[/bold red]", expand=False))
        return
    # === TOP STRATEGIES TABLE ===
    top_table = Table(title="TOP TRADING SETUPS", box=box.ROUNDED, header_style="bold magenta")
    top_table.add_column("Rank", width=5)
    top_table.add_column("Strategy", width=30)
    top_table.add_column("Score", width=8)
    top_table.add_column("Return", width=10)
    top_table.add_column("Win Rate", width=10)
    top_table.add_column("PF", width=8)
    top_table.add_column("DD", width=8)
    for setup in result['top_setups'][:15]:
        metrics = setup.get('metrics', {})
        return_pct = metrics.get('return', 0.0) * 100
        win_rate = metrics.get('win_rate', 0.0) * 100
        profit_factor = metrics.get('profit_factor', 0.0)
        max_dd = metrics.get('max_drawdown', 0.0) * 100
        # Color coding
        score = setup.get('score', 0.0)
        score_color = "green" if score > 0.7 else "yellow" if score > 0.5 else "red"
        return_color = "green" if return_pct >= 0 else "red"
        win_color = "green" if win_rate >= 55 else "red"
        top_table.add_row(
            f"{setup.get('rank', '?')}",
            f"[bold]{setup.get('name', 'N/A')}[/bold]",
            f"[{score_color}]{score:.3f}[/]",
            f"[{return_color}]{return_pct:.2f}%[/]",
            f"[{win_color}]{win_rate:.1f}%[/]",
            f"{profit_factor:.2f}",
            f"{max_dd:.2f}%"
        )
    # === STRATEGY RULES ===
    rules_text = ""
    for setup in result['top_setups'][:3]:
        entry = setup.get('rules', {}).get('entry', 'Not specified')
        exit_rule = setup.get('rules', {}).get('exit', 'Not specified')
        rules_text += (
            f"[bold]{setup.get('name', 'N/A')}[/]\n"
            f"[yellow]ENTRY:[/] {entry}\n"
            f"[magenta]EXIT:[/] {exit_rule}\n\n"
        )
    rules_panel = Panel(
        rules_text.strip(),
        title="[bold]TRADING RULES[/bold]",
        border_style="yellow",
        padding=(0, 0),
        expand=True
    )
    # === SYSTEM SUMMARY ===
    stats_text = (
        f"[bold]SYSTEM SUMMARY[/bold]\n"
        f"Generated: {result.get('generated_at', 'N/A')}\n"
        f"Bars: {result.get('total_bars', '?')}\n"
        f"Strategies: {result.get('strategy_count', 0)}\n"
        f"WF Validation: {result.get('walk_forward_stats', {}).get('average_folds', '?')} folds\n"
        f"Robustness: {result['top_setups'][0].get('robustness', {}).get('walk_forward_score', 0):.2f}\n"
        f"Regimes: {len(result.get('regime_summary', {}))}"
    )
    stats_panel = Panel(
        stats_text,
        title="[bold]SYSTEM INFO[/bold]",
        border_style="cyan",
        padding=(0, 0),
        expand=True
    )
    # === AI INSIGHTS ===
    ai_insights = (
        f"[bold]AI INSIGHTS[/bold]\n\n"
        f"• Best strategy: [bold]{result['top_setups'][0].get('name', 'N/A')}[/bold] "
        f"([green]{result['top_setups'][0].get('score', 0):.2f}[/green] score)\n"
        f"• Expected return: [green]{result['top_setups'][0]['metrics']['return']*100:.1f}%[/green]\n"
        f"• Market regime suggests: {'bullish' if 'BULL' in result.get('regime_summary', {}) else 'neutral'}\n\n"
        "[yellow]Recommendation:[/yellow] Combine top 2-3 strategies for robustness."
    )
    ai_panel = Panel(
        ai_insights,
        title="[bold]🤖 AI ANALYSIS[/bold]",
        padding=(0, 0),
        border_style="green",
        expand=True
    )
    # === ASSEMBLE LAYOUT ===
    layout = Layout()
    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )
    layout["upper"].split_row(
        Layout(top_table, name="table"),
        Layout(ai_panel, name="ai")
    )
    layout["lower"].split_row(
        Layout(rules_panel, name="rules"),
        Layout(stats_panel, name="stats")
    )
    console.print()
    console.print(layout)

def run_on_universe() -> None:
    """
    Run quantitative analysis on a universe of tickers.
    Universes are loaded from config/universes.json.
    Each ticker is analyzed using EdgeEngine, and results are rendered in a Rich table
    with AI summary panels that adapt to content height.
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn
    from rich.prompt import Prompt
    from rich import box
    import json
    import pandas as pd
    from pathlib import Path

    console = Console()
    historical_dir = Path("/Users/alberto.sfolcini/Development/quantstudio/historical_data")

    # Load universes from config/universes.json
    universe_file = Path("config/universes.json")
    if not universe_file.exists():
        console.print(Panel(
            "[bold red]File config/universes.json not found![/bold red]",
            title="Error"
        ))
        return

    try:
        with open(universe_file, 'r') as f:
            universes = json.load(f)
    except json.JSONDecodeError as e:
        console.print(Panel(f"[bold red]JSON error in {universe_file}: {e}[/bold red]", title="Error"))
        return

    # Display universes
    universe_list = list(universes.keys())
    table = Table(title="Available Universes", show_header=True, box=box.ROUNDED)
    table.add_column("#", style="magenta")
    table.add_column("Universe Name", style="green")
    table.add_column("# Tickers", style="yellow")

    sorted_universes = sorted(universes.items(), key=lambda x: len(x[1]), reverse=True)
    for idx, (name, tickers) in enumerate(sorted_universes, start=1):
        table.add_row(str(idx), name, str(len(tickers)))
    console.print(table)

    # Selection logic
    while True:
        try:
            choice_input = Prompt.ask(f"\nSelect universe [1-{len(sorted_universes)}]")
            universe_num = int(choice_input)
            if 1 <= universe_num <= len(sorted_universes):
                universe_name, selected_universe = sorted_universes[universe_num - 1]
                break
            console.print("[red]Invalid selection.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

    # Analysis process
    results = []
    with Progress(SpinnerColumn(), BarColumn(), TimeElapsedColumn(), console=console, expand=True) as progress:
        task = progress.add_task(f"[cyan]Analyzing {universe_name}...", total=len(selected_universe))
        for ticker in selected_universe:
            try:
                ticker_path = historical_dir / ticker / "data.csv"
                if not ticker_path.exists():
                    progress.advance(task)
                    continue

                df = pd.read_csv(ticker_path)
                if len(df) < 30:
                    progress.advance(task)
                    continue

                from edge_engine import EdgeEngine
                engine = EdgeEngine(df)
                report = engine.generate_report()
                quant = report.get('quantitative', {})
                decision = quant.get('decision', {})
                edge = quant.get('edge', {})

                signal = decision.get('bias', 'WAIT')

                # Variations calculation
                closes = df['close'].values
                daily_var = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 else 0
                weekly_var = ((closes[-1] - closes[-7]) / closes[-7] * 100) if len(closes) >= 7 else None
                monthly_var = ((closes[-1] - closes[-30]) / closes[-30] * 100) if len(closes) >= 30 else None

                # Calculate 1-day return on close (close vs previous close)
                close_return = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 else 0

                results.append({
                    'ticker': ticker,
                    'signal': signal,
                    'confidence': decision.get('confidence', 'UNKNOWN'),
                    'pf': edge.get('long_score', 50)/100 if "BUY" in signal else edge.get('short_score', 50)/100,
                    'last_price': df['close'].iloc[-1],
                    'variations': {'daily': daily_var, 'weekly': weekly_var, 'monthly': monthly_var},
                    'close_return': close_return,  # New field for 1-day return
                    'trend': quant.get('market_regime', {}).get('trend', 'UNKNOWN'),
                    'volatility': quant.get('market_regime', {}).get('volatility', 'UNKNOWN')
                })
            except Exception:
                pass
            finally:
                progress.advance(task)

    if not results:
        console.print("[red]No results generated.[/red]")
        return

    # Ranking
    conf_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
    top_results = sorted(results, key=lambda x: (conf_map.get(x['confidence'], 0), x['pf']), reverse=True)[:20]

    # Main Table
    res_table = Table(title=f"Results: {universe_name}", box=box.ROUNDED, header_style="bold magenta")
    res_table.add_column("#", width=3)
    res_table.add_column("Ticker", style="green")
    res_table.add_column("Signal")
    res_table.add_column("Confidence")
    res_table.add_column("Trend")
    res_table.add_column("Price", justify="right")
    res_table.add_column("1d %", justify="right")
    res_table.add_column("7d %", justify="right")
    res_table.add_column("30d %", justify="right")

    for idx, res in enumerate(top_results, start=1):
        def c(v): return "green" if v and v > 0.1 else "red" if v and v < -0.1 else "white"

        sig_col = "green" if "BUY" in res['signal'] else "red" if "SELL" in res['signal'] else "yellow"
        trend_col = "green" if res['trend'] == "BULL" else "red" if res['trend'] == "BEAR" else "yellow"

        res_table.add_row(
            str(idx), res['ticker'], f"[{sig_col}]{res['signal']}[/{sig_col}]",
            res['confidence'], f"[{trend_col}]{res['trend']}[/{trend_col}]",
            f"{res['last_price']:.2f}",
            f"[{c(res['close_return'])}]{res['close_return']:.1f}%[/]",
            f"[{c(res['variations']['weekly'])}]{res['variations']['weekly'] or 0:.1f}%[/]" if res['variations']['weekly'] is not None else "N/A",
            f"[{c(res['variations']['monthly'])}]{res['variations']['monthly'] or 0:.1f}%[/]" if res['variations']['monthly'] is not None else "N/A"
        )
    console.print(res_table)

    # --- AI & QUANT SUMMARY PANELS (HEIGHT OPTIMIZED) ---

    # 1. LLM Report Generation
    from reports.llm_aggregator import generate_aggregated_llm_report
    from core.config_loader import get_config

    llm_config = get_config().get('llm', {})
    if all(k in llm_config and llm_config[k].strip() for k in ['api_url', 'api_key']):
        try:
            raw_report = generate_aggregated_llm_report(top_results=top_results, universe_name=universe_name, llm_config=llm_config)
            llm_lines = [line.strip() for line in raw_report.split('\n') if line.strip()]
            llm_content = "\n".join(llm_lines)
        except Exception as e:
            llm_content = f"[red]Error: {str(e)}[/red]"
    else:
        llm_content = "[yellow]LLM not configured. Check settings.[/yellow]"

    # 2. Quant Summary Generation
    quant_lines = ["[bold]Top 5 Opportunities:[/bold]"]
    for res in top_results[:5]:
        icon = "[green]▲[/green]" if "BUY" in res['signal'] else "[red]▼[/red]" if "SELL" in res['signal'] else "➖"
        quant_lines.append(f"{icon} [bold]{res['ticker']}[/bold]: {res['signal']} (Confidence: {res['confidence']})")
    quant_content = "\n".join(quant_lines)

    # 3. Dynamic Printing (No Layout wrapper to avoid empty vertical space)
    console.print(Panel(
        llm_content or "[yellow]No content available.[/yellow]",
        title="[bold blue]AI Analysis Report[/bold blue]",
        border_style="blue",
        padding=(0, 1),
        expand=True  # Keeps it full width like the table
    ))

    console.print(Panel(
        quant_content,
        title="[bold green]Quantitative Summary[/bold green]",
        border_style="green",
        padding=(0, 1),
        expand=True
    ))

    # Prompt follows immediately
    console.input("\n[bold white]>> Press Enter to return to main menu...[/bold white]")

def run_ui():
    """
    Main TUI loop.
    """
    while True:
        choice = show_main_menu()
        
        if choice == 0:
            console.print("[bold green]Exiting QuantStudio...[/bold green]")
            break
        elif choice == 1:
            show_data_management_menu()
        elif choice == 2:
            show_edge_engine_menu()
        elif choice == 3:
            from events.event_tui import run_event_study
            run_event_study()
        elif choice == 9:
            show_config_menu()
