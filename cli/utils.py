import questionary
from typing import List, Optional, Tuple, Dict
import os
import re
import shutil
from datetime import datetime

from cli.models import AnalystType
from rich.console import Console

console = Console()

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent() -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = [
        ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
        ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
        ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
        ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
    ]

    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent() -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = [
        ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
        ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
        ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ("o4-mini - Specialized reasoning model (compact)", "o4-mini"),
        ("o3-mini - Advanced reasoning model (lightweight)", "o3-mini"),
        ("o3 - Full advanced reasoning model", "o3"),
        ("o1 - Premier reasoning and problem-solving model", "o1"),
    ]

    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice


def scan_cached_tickers() -> List[Tuple[str, str, str]]:
    """Scan the data cache directory for cached tickers and return ticker info.
    
    Returns:
        List of tuples containing (ticker, cache_type, file_path)
    """
    from tradingagents.default_config import DEFAULT_CONFIG
    
    cache_dir = DEFAULT_CONFIG["data_cache_dir"]
    cached_tickers = []
    
    if not os.path.exists(cache_dir):
        return cached_tickers
    
    # Scan for ticker directories first (new structure)
    for item in os.listdir(cache_dir):
        item_path = os.path.join(cache_dir, item)
        if os.path.isdir(item_path):
            # This is a ticker directory
            ticker = item.upper()
            cached_tickers.append((ticker, "directory", item_path))
    
    # Scan for legacy CSV files (old structure)
    for file in os.listdir(cache_dir):
        if file.endswith(".csv") and not os.path.isdir(os.path.join(cache_dir, file)):
            # Extract ticker from filename: TICKER-YFin-data-*.csv
            match = re.match(r"([A-Z]+)-YFin-data-.*\.csv", file)
            if match:
                ticker = match.group(1)
                file_path = os.path.join(cache_dir, file)
                # Only add if not already found as a directory
                if not any(t[0] == ticker and t[1] == "directory" for t in cached_tickers):
                    cached_tickers.append((ticker, "file", file_path))
    
    return sorted(cached_tickers, key=lambda x: x[0])


def select_cached_ticker_to_delete() -> Optional[Tuple[str, str, str]]:
    """Select a cached ticker to delete using an interactive selection.
    
    Returns:
        Tuple containing (ticker, cache_type, file_path) or None if cancelled
    """
    cached_tickers = scan_cached_tickers()
    
    if not cached_tickers:
        print("\n[yellow]No cached data found.[/yellow]")
        return None
    
    # Create display choices
    choices = []
    for ticker, cache_type, path in cached_tickers:
        if cache_type == "directory":
            display = f"{ticker} (Full Analysis Data)"
        else:
            display = f"{ticker} (Market Data Only)"
        choices.append(questionary.Choice(display, value=(ticker, cache_type, path)))
    
    # Add cancel option
    choices.append(questionary.Choice("← Back to Main Menu", value=None))
    
    choice = questionary.select(
        "Select cached ticker to DELETE:",
        choices=choices,
        instruction="\n- Use arrow keys to navigate\n- Press Enter to DELETE selected ticker data\n- Select 'Back to Main Menu' to cancel",
        style=questionary.Style(
            [
                ("selected", "fg:red noinherit"),
                ("highlighted", "fg:red noinherit"),
                ("pointer", "fg:red noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        return None
    
    return choice


def delete_cached_ticker(ticker: str, cache_type: str, path: str) -> bool:
    """Delete cached ticker data.
    
    Args:
        ticker: The ticker symbol
        cache_type: Either 'directory' or 'file'
        path: Full path to the cached data
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Confirm deletion
        confirm = questionary.confirm(
            f"Are you sure you want to DELETE all cached data for {ticker}?",
            default=False,
            style=questionary.Style(
                [
                    ("question", "fg:red bold"),
                    ("answer", "fg:red bold"),
                ]
            ),
        ).ask()
        
        if not confirm:
            print(f"\n[yellow]Deletion cancelled for {ticker}[/yellow]")
            return False
        
        if cache_type == "directory":
            shutil.rmtree(path)
            print(f"\n[green]Successfully deleted directory for {ticker}[/green]")
        else:
            os.remove(path)
            print(f"\n[green]Successfully deleted file for {ticker}[/green]")
        
        return True
        
    except Exception as e:
        print(f"\n[red]Error deleting {ticker}: {str(e)}[/red]")
        return False


def manage_data_cache() -> bool:
    """Interactive data cache management menu.
    
    Returns:
        True to continue to main analysis, False to exit
    """
    while True:
        cached_tickers = scan_cached_tickers()
        
        print(f"\n[bold cyan]Data Cache Management[/bold cyan]")
        print(f"Found {len(cached_tickers)} cached tickers:")
        
        if cached_tickers:
            for ticker, cache_type, path in cached_tickers:
                cache_info = "Full Analysis" if cache_type == "directory" else "Market Data"
                print(f"  • {ticker} ({cache_info})")
        else:
            print("  [dim]No cached data found[/dim]")
        
        # Show menu options
        action = questionary.select(
            "\nWhat would you like to do?",
            choices=[
                questionary.Choice("🗑️  Delete cached ticker data", value="delete"),
                questionary.Choice("📊 Continue to new analysis", value="continue"),
                questionary.Choice("❌ Exit", value="exit"),
            ],
            instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
            style=questionary.Style(
                [
                    ("selected", "fg:cyan noinherit"),
                    ("highlighted", "fg:cyan noinherit"),
                    ("pointer", "fg:cyan noinherit"),
                ]
            ),
        ).ask()
        
        if action == "delete":
            if not cached_tickers:
                print("\n[yellow]No cached data to delete.[/yellow]")
                continue
                
            ticker_info = select_cached_ticker_to_delete()
            if ticker_info:
                ticker, cache_type, path = ticker_info
                delete_cached_ticker(ticker, cache_type, path)
                
        elif action == "continue":
            return True
            
        elif action == "exit":
            return False
        
        # Small pause before showing menu again
        questionary.press_any_key_to_continue("\nPress any key to continue...").ask()


def create_ticker_cache_directory(ticker: str) -> str:
    """Create a directory for ticker-specific cache data.
    
    Args:
        ticker: The ticker symbol
        
    Returns:
        Path to the created directory
    """
    from tradingagents.default_config import DEFAULT_CONFIG
    
    cache_dir = DEFAULT_CONFIG["data_cache_dir"]
    ticker_dir = os.path.join(cache_dir, ticker.upper())
    
    os.makedirs(ticker_dir, exist_ok=True)
    return ticker_dir


def save_final_report(ticker: str, analysis_date: str, final_state: dict, final_report: str) -> str:
    """Save the final analysis report to the ticker's cache directory.
    
    Args:
        ticker: The ticker symbol
        analysis_date: The analysis date
        final_state: The final state dictionary from the analysis
        final_report: The formatted final report
        
    Returns:
        Path to the saved report file
    """
    ticker_dir = create_ticker_cache_directory(ticker)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%H%M%S")
    report_filename = f"{ticker}_analysis_{analysis_date}_{timestamp}.md"
    report_path = os.path.join(ticker_dir, report_filename)
    
    # Save the final report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# {ticker} Trading Analysis Report\n\n")
        f.write(f"**Analysis Date:** {analysis_date}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(final_report)
    
    return report_path
