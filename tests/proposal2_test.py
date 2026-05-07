#!/usr/bin/env python3

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Test the main structure
main_table = Table(title="", expand=True, show_header=False, box=None)
main_table.add_column("Category", style="green", width=20)
main_table.add_column("Value A", style="yellow", width=25)
main_table.add_column("Value B", style="yellow", width=25)
main_table.add_column("Value C", style="yellow", width=20)
main_table.add_column("Status", style="green", width=12)

main_table.add_row("Market Regime", "🐂 BULL", "📏 COMPRESSION", "ATR: 1.23", "↑↑↑")
main_table.add_row("Edge Scores", "Long: 8.1", "Short: 6.2", "Penalty: 0.5%", "SMALL")

console.print(Panel("[bold cyan]EDGE ANALYSIS - TEST[/]", width=70))
console.print(main_table)

llm_text = "Market shows strong bullish momentum. Support at 182.50 suggests buy zone."
ai_card = Panel(llm_text, title="[bold magenta]🤖 Trading Summary", border_style="blue", expand=True)
console.print(ai_card)

print("✅ Layout test passed")