#!/usr/bin/env python3
"""
Search n8n workflow templates using the public API.

Usage:
    python scripts/search.py search "real estate"          # Basic search
    python scripts/search.py categories                    # List all categories
    python scripts/search.py collections                   # List all collections
    python scripts/search.py collection 8                  # Get collection details
    python scripts/search.py stats                         # Show API statistics

API Reference: docs/n8n-public-API.md
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import click
import requests
from rich.console import Console
from rich.table import Table

# API Configuration
API_BASE = "https://api.n8n.io/api/templates"
API_HEALTH = "https://api.n8n.io/api/health"

# Default values
DEFAULT_ROWS = 10
MAX_ROWS = 100
DEFAULT_SKIP = 0
SAVE_DIR = "search_results"

# Console for Rich output
console = Console()
err_console = Console(stderr=True)

# Global verbose flag
_verbose = False


@dataclass
class Workflow:
    """Workflow template from the API."""

    id: int
    name: str
    total_views: int
    author: str
    description: str = ""
    created_at: str = ""

    @classmethod
    def from_api(cls, data: dict) -> "Workflow":
        """Create Workflow from API response data."""
        user = data.get("user") or {}
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            total_views=data.get("totalViews", 0),
            author=user.get("name", "Unknown"),
            description=data.get("description", ""),
            created_at=data.get("createdAt", ""),
        )


@dataclass
class Category:
    """Workflow category from the API."""

    id: int
    name: str
    icon: str
    parent_name: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> "Category":
        """Create Category from API response data."""
        parent = data.get("parent")
        parent_name = parent.get("name") if parent else None
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon=data.get("icon", ""),
            parent_name=parent_name,
        )


@dataclass
class Collection:
    """Curated collection from the API."""

    id: int
    name: str
    description: str
    workflow_count: int
    workflows: list

    @classmethod
    def from_api(cls, data: dict, detailed: bool = False) -> "Collection":
        """Create Collection from API response data."""
        workflows = data.get("workflows", [])
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            workflow_count=len(workflows),
            workflows=workflows if detailed else [],
        )


def api_request(endpoint: str) -> dict:
    """Make API request with error handling."""
    url = f"{API_BASE}{endpoint}"

    if _verbose:
        err_console.print(f"[dim]API: {url}[/dim]")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Check for API error in response body
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            err_console.print(f"[red]Error: {error_msg}[/red]")
            sys.exit(1)

        return data

    except requests.exceptions.Timeout:
        err_console.print("[red]Error: API request timed out[/red]")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        err_console.print("[red]Error: Could not connect to API[/red]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        err_console.print(f"[red]Error: API request failed (HTTP {e.response.status_code})[/red]")
        sys.exit(1)
    except json.JSONDecodeError:
        err_console.print("[red]Error: Invalid JSON response from API[/red]")
        sys.exit(1)


def format_number(n: int) -> str:
    """Format number with comma separators."""
    return f"{n:,}"


def truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def save_results(
    data: dict,
    query: str = "",
    category: str = "",
    apps: str = "",
    nodes: str = "",
) -> None:
    """Save search results to JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Build filename from search parameters
    parts = []
    if query:
        safe_query = "".join(c if c.isalnum() or c in "-_" else "-" for c in query)[:30]
        parts.append(f"q-{safe_query}")
    if category:
        safe_cat = "".join(c if c.isalnum() or c in "-_" else "-" for c in category)[:20]
        parts.append(f"cat-{safe_cat}")
    if apps:
        safe_apps = "".join(c if c.isalnum() or c in "-_" else "-" for c in apps)[:20]
        parts.append(f"apps-{safe_apps}")
    if nodes:
        safe_nodes = "".join(c if c.isalnum() or c in "-_" else "-" for c in nodes)[:20]
        parts.append(f"nodes-{safe_nodes}")

    if not parts:
        parts.append("search")

    filename = f"{timestamp}_{'_'.join(parts)}.json"
    save_path = Path(SAVE_DIR)
    save_path.mkdir(exist_ok=True)

    filepath = save_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    console.print(f"[green]Results saved to:[/green] {filepath}")


# Output formatters


def output_table_search(
    data: dict,
    query: str,
    category: str,
    apps: str,
    nodes: str,
    rows: int,
    skip: int,
) -> None:
    """Output search results in table format."""
    total = data.get("totalWorkflows", 0)
    workflows = data.get("workflows", [])
    count = len(workflows)
    current_page = skip // rows + 1
    total_pages = (total + rows - 1) // rows if rows > 0 else 1

    console.print("[bold]=== n8n Workflow Search Results ===[/bold]\n")

    # Search info
    if query:
        console.print(f'[cyan]Search:[/cyan]   "{query}"')
    if category:
        console.print(f"[cyan]Category:[/cyan] {category}")
    if apps:
        console.print(f"[cyan]Apps:[/cyan]     {apps}")
    if nodes:
        console.print(f"[cyan]Nodes:[/cyan]    {nodes}")

    results_msg = f"{format_number(total)} total (page {current_page} of {total_pages})"
    console.print(f"[cyan]Results:[/cyan]  {results_msg}\n")

    if count == 0:
        console.print("[yellow]No workflows found matching your criteria.[/yellow]")
        return

    # Table
    table = Table(show_header=True, header_style="dim")
    table.add_column("ID", style="", width=8)
    table.add_column("Name", style="", width=55)
    table.add_column("Views", style="", width=10, justify="right")
    table.add_column("Author", style="", width=15)

    for wf in workflows:
        w = Workflow.from_api(wf)
        table.add_row(
            str(w.id),
            truncate(w.name, 53),
            format_number(w.total_views),
            truncate(w.author, 15),
        )

    console.print(table)

    # Pagination hint
    if total > skip + rows:
        next_page = current_page + 1
        hint = f"More results available. Use --page {next_page} to see next page."
        console.print(f"\n[dim]{hint}[/dim]")


def output_json(data: dict) -> None:
    """Output data as formatted JSON."""
    print(json.dumps(data, indent=2))


def output_ids(workflows: list) -> None:
    """Output workflow IDs only (for piping)."""
    for wf in workflows:
        print(wf.get("id", ""))


def output_compact(data: dict) -> None:
    """Output in compact format."""
    total = data.get("totalWorkflows", 0)
    workflows = data.get("workflows", [])
    count = len(workflows)

    console.print(f"[dim]Found {total} workflows (showing {count})[/dim]\n")

    for wf in workflows:
        w = Workflow.from_api(wf)
        print(f"{w.id} | {w.name} | {format_number(w.total_views)} views")


def output_table_categories(categories: list) -> None:
    """Output categories in table format."""
    console.print("[bold]=== n8n Workflow Categories ===[/bold]\n")

    # Parent categories
    console.print("[cyan]Parent Categories:[/cyan]")
    for cat in categories:
        c = Category.from_api(cat)
        if c.parent_name is None:
            console.print(f"  {c.icon} {c.name}")

    console.print("\n[cyan]Subcategories:[/cyan]")
    for cat in categories:
        c = Category.from_api(cat)
        if c.parent_name is not None:
            console.print(f"  {c.icon} {c.name} (parent: {c.parent_name})")

    console.print(f"\n[dim]Total: {len(categories)} categories[/dim]")


def output_table_collections(collections: list) -> None:
    """Output collections in table format."""
    console.print("[bold]=== n8n Curated Collections ===[/bold]\n")

    table = Table(show_header=True, header_style="cyan")
    table.add_column("ID", width=4)
    table.add_column("Name", width=40)
    table.add_column("Workflows", justify="right")

    # Sort by rank if available
    sorted_cols = sorted(collections, key=lambda x: x.get("rank", 0))

    for col in sorted_cols:
        c = Collection.from_api(col)
        wf_count = len(col.get("workflows", []))
        table.add_row(str(c.id), c.name, str(wf_count))

    console.print(table)
    console.print(f"\n[dim]Total: {len(collections)} collections[/dim]")


def output_table_collection(data: dict) -> None:
    """Output single collection details in table format."""
    col_data = data.get("collection", {})
    c = Collection.from_api(col_data, detailed=True)

    console.print(f"[bold]=== Collection: {c.name} ===[/bold]\n")

    console.print("[cyan]Description:[/cyan]")
    # Word wrap description
    if c.description:
        for i in range(0, len(c.description), 80):
            console.print(f"  {c.description[i : i + 80]}")
    else:
        console.print("  No description")

    console.print(f"\n[cyan]Workflows ({c.workflow_count}):[/cyan]\n")

    table = Table(show_header=True, header_style="dim")
    table.add_column("ID", width=8)
    table.add_column("Name", width=50)
    table.add_column("Views", justify="right")

    for wf in c.workflows:
        wf_id = wf.get("id", "")
        wf_name = wf.get("name", "")
        wf_views = wf.get("totalViews") or wf.get("views", 0)
        table.add_row(str(wf_id), truncate(wf_name, 48), format_number(wf_views))

    console.print(table)


# CLI Commands


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Show verbose output including API URLs")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Search n8n workflow templates using the public API.

    \b
    Examples:
      python scripts/search.py search "real estate"
      python scripts/search.py categories
      python scripts/search.py collections
      python scripts/search.py collection 8
      python scripts/search.py stats
    """
    global _verbose
    _verbose = verbose
    ctx.ensure_object(dict)


@cli.command()
@click.argument("query", required=False, default="")
@click.option("-c", "--category", default="", help="Filter by category (comma-separated)")
@click.option("-a", "--apps", default="", help="Filter by app/integration names (comma-separated)")
@click.option("-n", "--nodes", default="", help="Filter by node type names (comma-separated)")
@click.option(
    "-r",
    "--rows",
    default=DEFAULT_ROWS,
    type=int,
    help=f"Number of results (default: {DEFAULT_ROWS}, max: {MAX_ROWS})",
)
@click.option("-p", "--page", default=1, type=int, help="Page number (default: 1)")
@click.option("-s", "--skip", default=None, type=int, help="Skip N results (overrides --page)")
@click.option(
    "-o",
    "--output",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "ids", "compact"]),
    help="Output format (default: table)",
)
@click.option("--json", "json_flag", is_flag=True, help="Shorthand for --output json")
@click.option("--ids", "ids_flag", is_flag=True, help="Shorthand for --output ids")
@click.option("--compact", "compact_flag", is_flag=True, help="Shorthand for --output compact")
@click.option("--save", is_flag=True, help="Save results to search_results/ folder")
def search(
    query: str,
    category: str,
    apps: str,
    nodes: str,
    rows: int,
    page: int,
    skip: int | None,
    output_format: str,
    json_flag: bool,
    ids_flag: bool,
    compact_flag: bool,
    save: bool,
) -> None:
    """Search workflow templates.

    \b
    Examples:
      search "real estate"              Basic keyword search
      search -c AI                      Filter by category
      search -a "Telegram,OpenAI"       Filter by apps
      search -q "chatbot" -c AI -r 20   Combined filters with pagination
    """
    # Validate rows
    if rows > MAX_ROWS:
        warn_msg = f"Warning: Maximum rows is {MAX_ROWS}. Setting to {MAX_ROWS}."
        err_console.print(f"[yellow]{warn_msg}[/yellow]")
        rows = MAX_ROWS
    if rows < 1:
        rows = DEFAULT_ROWS

    # Calculate skip from page if not explicitly set
    if skip is None:
        skip = (page - 1) * rows

    # Determine output format from flags
    if json_flag:
        output_format = "json"
    elif ids_flag:
        output_format = "ids"
    elif compact_flag:
        output_format = "compact"

    # Check if any search criteria provided
    if not query and not category and not apps and not nodes:
        err_console.print("[yellow]No search criteria provided.[/yellow]\n")
        console.print("Quick examples:")
        console.print('  search "real estate"           # Search by keyword')
        console.print("  search --category AI           # Filter by category")
        console.print("  categories                     # See available categories")
        console.print("  --help                         # Full usage")
        sys.exit(1)

    # Build query string
    params = []
    if query:
        params.append(f"search={quote(query, safe='')}")
    if category:
        params.append(f"category={quote(category, safe='')}")
    if apps:
        params.append(f"apps={quote(apps, safe='')}")
    if nodes:
        params.append(f"nodes={quote(nodes, safe='')}")
    params.append(f"rows={rows}")
    params.append(f"skip={skip}")

    endpoint = f"/search?{'&'.join(params)}"
    data = api_request(endpoint)

    # Save if requested
    if save:
        save_results(data, query, category, apps, nodes)

    # Output
    if output_format == "json":
        output_json(data)
    elif output_format == "ids":
        output_ids(data.get("workflows", []))
    elif output_format == "compact":
        output_compact(data)
    else:
        output_table_search(data, query, category, apps, nodes, rows, skip)


@cli.command()
@click.option(
    "-o",
    "--output",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format (default: table)",
)
@click.option("--json", "json_flag", is_flag=True, help="Shorthand for --output json")
def categories(output_format: str, json_flag: bool) -> None:
    """List all available workflow categories."""
    if json_flag:
        output_format = "json"

    data = api_request("/categories")

    if output_format == "json":
        output_json(data)
    else:
        output_table_categories(data.get("categories", []))


@cli.command()
@click.option(
    "-o",
    "--output",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format (default: table)",
)
@click.option("--json", "json_flag", is_flag=True, help="Shorthand for --output json")
def collections(output_format: str, json_flag: bool) -> None:
    """List all curated workflow collections."""
    if json_flag:
        output_format = "json"

    data = api_request("/collections")

    if output_format == "json":
        output_json(data)
    else:
        output_table_collections(data.get("collections", []))


@cli.command()
@click.argument("id", type=int)
@click.option(
    "-o",
    "--output",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "ids"]),
    help="Output format (default: table)",
)
@click.option("--json", "json_flag", is_flag=True, help="Shorthand for --output json")
@click.option("--ids", "ids_flag", is_flag=True, help="Shorthand for --output ids")
def collection(id: int, output_format: str, json_flag: bool, ids_flag: bool) -> None:
    """Get details for a specific collection.

    \b
    Examples:
      collection 8                      Show collection details
      collection 8 --ids                Output workflow IDs only
    """
    if json_flag:
        output_format = "json"
    elif ids_flag:
        output_format = "ids"

    data = api_request(f"/collections/{id}")

    if output_format == "json":
        output_json(data)
    elif output_format == "ids":
        col_data = data.get("collection", {})
        for wf in col_data.get("workflows", []):
            print(wf.get("id", ""))
    else:
        output_table_collection(data)


@cli.command()
def stats() -> None:
    """Show API statistics (total workflows, categories, collections)."""
    console.print("[blue]Fetching API statistics...[/blue]\n")

    # Get workflow count
    wf_data = api_request("/workflows?rows=1&skip=0")
    total_workflows = wf_data.get("totalWorkflows", 0)

    # Get category count
    cat_data = api_request("/categories")
    total_categories = len(cat_data.get("categories", []))

    # Get collection count
    col_data = api_request("/collections")
    total_collections = len(col_data.get("collections", []))

    console.print("[bold]=== n8n Template API Statistics ===[/bold]\n")
    console.print(f"  [cyan]Total Workflows:[/cyan]    {format_number(total_workflows)}")
    console.print(f"  [cyan]Total Categories:[/cyan]   {total_categories}")
    console.print(f"  [cyan]Total Collections:[/cyan]  {total_collections}")
    console.print("\n[dim]Data cached for 4 hours by Cloudflare[/dim]")


if __name__ == "__main__":
    cli()
