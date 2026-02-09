#!/usr/bin/env python3
"""
Crawl and download all n8n workflow templates from the public API.

Discovers all workflow IDs via pagination, then downloads each into
category-organized folders with human-like request delays and checkpoint/resume.

Usage:
    python scripts/crawl.py                         # Resume or start full crawl
    python scripts/crawl.py --fresh                 # Start over, ignore checkpoint
    python scripts/crawl.py --rediscover            # Re-check API for new workflows
    python scripts/crawl.py --dry-run               # Show plan without downloading
    python scripts/crawl.py --max-downloads 50      # Limit count (for testing)
    python scripts/crawl.py --delay-min 2 --delay-max 6  # Custom delay range
    python scripts/crawl.py --split                 # Run split.py on each download
    python scripts/crawl.py -v                      # Verbose logging

API Reference: docs/n8n-public-API.md
"""

import json
import random
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import click
import requests
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn

# API Configuration
API_BASE = "https://api.n8n.io/api/templates"
LIST_ENDPOINT = "/workflows"
DETAIL_ENDPOINT = "/workflows"

# Defaults
DEFAULT_OUTPUT_DIR = "n8n-workflows"
DEFAULT_PAGE_SIZE = 100
REQUEST_TIMEOUT = 30
STATE_FILENAME = ".crawl_state.json"
INDEX_FILENAME = "index.json"
DEFAULT_DELAY_MIN = 1.5
DEFAULT_DELAY_MAX = 4.0
DEFAULT_BURST_MIN = 20
DEFAULT_BURST_MAX = 40
DEFAULT_BURST_PAUSE_MIN = 10.0
DEFAULT_BURST_PAUSE_MAX = 20.0
JITTER = 0.5
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5.0
RETRY_MULTIPLIER = 3.0

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Console
console = Console()
err_console = Console(stderr=True)

# Verbose flag
_verbose = False

# Graceful shutdown
_shutdown_requested = False


def _handle_signal(signum: int, frame: Any) -> None:
    """Handle interrupt signal for graceful shutdown."""
    global _shutdown_requested
    _shutdown_requested = True
    console.print("\n[yellow]Shutdown requested, finishing current download...[/yellow]")


# --- Helpers ---


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Convert workflow name to filesystem-safe filename.

    Args:
        name: Workflow name from API.
        max_length: Maximum length for the sanitized name.

    Returns:
        Sanitized string safe for use in filenames.
    """
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
    while "--" in safe:
        safe = safe.replace("--", "-")
    safe = safe.strip("-")
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip("-")
    return safe or "workflow"


# --- Session ---


def create_session() -> requests.Session:
    """Create a requests session with browser-like headers."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


# --- Delay ---


def human_delay(
    min_s: float,
    max_s: float,
    request_num: int,
    burst_interval: int,
) -> None:
    """Sleep with human-like jitter and periodic micro-burst pauses.

    Args:
        min_s: Minimum delay in seconds.
        max_s: Maximum delay in seconds.
        request_num: Current request counter (1-based).
        burst_interval: Take a longer break every N requests.
    """
    if request_num > 0 and request_num % burst_interval == 0:
        pause = random.uniform(DEFAULT_BURST_PAUSE_MIN, DEFAULT_BURST_PAUSE_MAX)
        if _verbose:
            console.print(f"[dim]Coffee break: {pause:.1f}s after {request_num} requests[/dim]")
        time.sleep(pause)
        return

    base = random.uniform(min_s, max_s)
    jitter = random.uniform(-JITTER, JITTER)
    delay = max(0.5, base + jitter)
    time.sleep(delay)


# --- Retry ---


def request_with_retry(
    session: requests.Session,
    url: str,
) -> requests.Response | None:
    """Make a GET request with exponential backoff on 429/5xx.

    Args:
        session: Requests session to use.
        url: URL to fetch.

    Returns:
        Response object on success, None after all retries exhausted.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt < MAX_RETRIES:
                    backoff = RETRY_BASE_DELAY * (RETRY_MULTIPLIER**attempt)
                    err_console.print(
                        f"[yellow]HTTP {resp.status_code}, retry {attempt + 1}/{MAX_RETRIES} "
                        f"in {backoff:.0f}s[/yellow]"
                    )
                    time.sleep(backoff)
                    continue
                err_console.print(
                    f"[red]HTTP {resp.status_code} after {MAX_RETRIES} retries: {url}[/red]"
                )
                return None
            if resp.status_code == 404:
                if _verbose:
                    err_console.print(f"[dim]404: {url}[/dim]")
                return None
            err_console.print(f"[red]HTTP {resp.status_code}: {url}[/red]")
            return None
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                backoff = RETRY_BASE_DELAY * (RETRY_MULTIPLIER**attempt)
                err_console.print(
                    f"[yellow]Timeout, retry {attempt + 1}/{MAX_RETRIES} in {backoff:.0f}s[/yellow]"
                )
                time.sleep(backoff)
                continue
            err_console.print(f"[red]Timeout after {MAX_RETRIES} retries: {url}[/red]")
            return None
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                backoff = RETRY_BASE_DELAY * (RETRY_MULTIPLIER**attempt)
                err_console.print(
                    f"[yellow]Connection error, retry {attempt + 1}/{MAX_RETRIES} "
                    f"in {backoff:.0f}s[/yellow]"
                )
                time.sleep(backoff)
                continue
            err_console.print(f"[red]Connection failed after {MAX_RETRIES} retries: {url}[/red]")
            return None
    return None


# --- Discovery Phase ---


def fetch_all_ids(
    session: requests.Session,
    delay_min: float,
    delay_max: float,
) -> list[dict[str, Any]]:
    """Paginate the list API to collect all workflow summaries.

    Args:
        session: Requests session.
        delay_min: Minimum delay between pages.
        delay_max: Maximum delay between pages.

    Returns:
        List of workflow summary dicts with id, name, and category info.
    """
    all_workflows: list[dict[str, Any]] = []
    skip = 0
    total: int | None = None
    page_num = 0
    burst_interval = random.randint(DEFAULT_BURST_MIN, DEFAULT_BURST_MAX)

    console.print("[bold]Phase 1: Discovering workflow IDs...[/bold]")

    while True:
        if _shutdown_requested:
            break

        url = f"{API_BASE}{LIST_ENDPOINT}?rows={DEFAULT_PAGE_SIZE}&skip={skip}"
        if _verbose:
            console.print(f"[dim]Fetching: {url}[/dim]")

        resp = request_with_retry(session, url)
        if resp is None:
            err_console.print(f"[red]Failed to fetch page at skip={skip}, stopping discovery[/red]")
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            err_console.print(f"[red]Invalid JSON at skip={skip}, stopping discovery[/red]")
            break

        if total is None:
            total = data.get("totalWorkflows", 0)
            console.print(f"[cyan]Total workflows on API: {total:,}[/cyan]")

        workflows = data.get("workflows", [])
        if not workflows:
            break

        all_workflows.extend(workflows)
        page_num += 1
        skip += len(workflows)

        console.print(
            f"  Page {page_num}: collected {len(all_workflows):,}/{total:,} IDs",
            highlight=False,
        )

        if total and skip >= total:
            break

        human_delay(delay_min, delay_max, page_num, burst_interval)

    console.print(
        f"[green]Discovery complete: {len(all_workflows):,} workflow IDs collected[/green]"
    )
    return all_workflows


# --- State Management ---


def load_state(state_path: Path) -> dict[str, Any]:
    """Load crawl checkpoint state from disk.

    Args:
        state_path: Path to state JSON file.

    Returns:
        State dict with downloaded_ids, failed_ids, and discovered_ids.
    """
    empty: dict[str, Any] = {
        "downloaded_ids": [],
        "failed_ids": [],
        "discovered_ids": [],
        "total_on_api": 0,
        "timestamp": "",
    }
    if not state_path.exists():
        return empty

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return {
            "downloaded_ids": data.get("downloaded_ids", []),
            "failed_ids": data.get("failed_ids", []),
            "discovered_ids": data.get("discovered_ids", []),
            "total_on_api": data.get("total_on_api", 0),
            "timestamp": data.get("timestamp", ""),
        }
    except (json.JSONDecodeError, OSError):
        return empty


def save_state(state: dict[str, Any], state_path: Path) -> None:
    """Save crawl checkpoint state to disk.

    Args:
        state: State dict with downloaded_ids and failed_ids.
        state_path: Path to write state JSON.
    """
    from datetime import UTC, datetime

    state["timestamp"] = datetime.now(UTC).isoformat()
    try:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError as e:
        err_console.print(f"[yellow]Warning: Could not save state: {e}[/yellow]")


# --- Scan Existing ---


def scan_existing(output_dir: Path) -> set[int]:
    """Scan output directory for already-downloaded workflow files.

    Looks for files matching pattern `{id}-*.json` in all subdirectories.

    Args:
        output_dir: Root output directory to scan.

    Returns:
        Set of workflow IDs already on disk.
    """
    existing: set[int] = set()
    if not output_dir.exists():
        return existing

    for json_file in output_dir.rglob("*.json"):
        name = json_file.stem
        # Skip index and state files
        if name in ("index", ".crawl_state") or json_file.name == STATE_FILENAME:
            continue
        # Extract leading numeric ID from "1234-Workflow-Name"
        parts = name.split("-", 1)
        if parts and parts[0].isdigit():
            existing.add(int(parts[0]))

    return existing


# --- Category Helpers ---


def sanitize_category(name: str) -> str:
    """Convert category name to filesystem-safe directory name.

    Args:
        name: Category name from API.

    Returns:
        Sanitized directory name.
    """
    safe = "".join(c if c.isalnum() or c in " -_" else "" for c in name).strip()
    # Collapse whitespace
    safe = "-".join(safe.split())
    return safe or "Uncategorized"


def extract_category(workflow_data: dict[str, Any]) -> str:
    """Extract the first category name from a workflow API response.

    Args:
        workflow_data: Full API response for a single workflow.

    Returns:
        Category name string, or "Uncategorized" if none found.
    """
    wf = workflow_data.get("workflow", workflow_data)
    categories = wf.get("categories", [])
    if categories and isinstance(categories, list):
        first = categories[0]
        if isinstance(first, dict):
            return str(first.get("name", "Uncategorized"))
        if isinstance(first, str):
            return first
    return "Uncategorized"


def extract_all_categories(workflow_data: dict[str, Any]) -> list[str]:
    """Extract all category names from a workflow API response.

    Args:
        workflow_data: Full API response for a single workflow.

    Returns:
        List of category name strings.
    """
    wf = workflow_data.get("workflow", workflow_data)
    categories = wf.get("categories", [])
    names: list[str] = []
    if isinstance(categories, list):
        for cat in categories:
            if isinstance(cat, dict):
                names.append(cat.get("name", "Uncategorized"))
            elif isinstance(cat, str):
                names.append(cat)
    return names or ["Uncategorized"]


# --- Download One ---


def download_one(
    session: requests.Session,
    wf_id: int,
    output_dir: Path,
) -> tuple[bool, str]:
    """Fetch a single workflow and save to category subfolder.

    Uses atomic write via temp file.

    Args:
        session: Requests session.
        wf_id: Workflow ID to download.
        output_dir: Root output directory.

    Returns:
        Tuple of (success: bool, workflow_name: str).
    """
    url = f"{API_BASE}{DETAIL_ENDPOINT}/{wf_id}"
    if _verbose:
        console.print(f"[dim]Fetching: {url}[/dim]")

    resp = request_with_retry(session, url)
    if resp is None:
        return False, ""

    try:
        data = resp.json()
    except json.JSONDecodeError:
        err_console.print(f"[red]Invalid JSON for workflow {wf_id}[/red]")
        return False, ""

    if "error" in data:
        err_console.print(f"[red]API error for {wf_id}: {data['error']}[/red]")
        return False, ""

    # Extract metadata
    wf = data.get("workflow", data)
    name = wf.get("name", "") or data.get("name", "")
    category = extract_category(data)
    safe_category = sanitize_category(category)
    safe_name = sanitize_filename(name) if name else "workflow"

    # Build path: output_dir/Category/ID-Name.json
    cat_dir = output_dir / safe_category
    cat_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{wf_id}-{safe_name}.json"
    final_path = cat_dir / filename

    # Atomic write via temp file
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            dir=cat_dir,
            delete=False,
            encoding="utf-8",
        ) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_path = Path(tmp.name)

        # Validate
        with open(tmp_path, encoding="utf-8") as f:
            json.load(f)

        tmp_path.replace(final_path)
        return True, name

    except (OSError, json.JSONDecodeError) as e:
        err_console.print(f"[red]Failed to save {wf_id}: {e}[/red]")
        if "tmp_path" in locals() and tmp_path.exists():
            tmp_path.unlink()
        return False, ""


# --- Index ---


def build_index(output_dir: Path) -> dict[str, Any]:
    """Scan all downloaded workflow files and build/update index.json.

    Args:
        output_dir: Root output directory containing category subfolders.

    Returns:
        Index dict mapping workflow ID to metadata.
    """
    index: dict[str, Any] = {}

    for json_file in output_dir.rglob("*.json"):
        if json_file.name in (INDEX_FILENAME, STATE_FILENAME):
            continue
        if json_file.parent == output_dir:
            continue  # Skip root-level non-workflow files

        stem = json_file.stem
        parts = stem.split("-", 1)
        if not parts or not parts[0].isdigit():
            continue

        wf_id = parts[0]
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(data, dict):
            continue

        wf = data.get("workflow", data)
        if not isinstance(wf, dict):
            continue
        user = wf.get("user", {}) or {}
        categories = extract_all_categories(data)

        index[wf_id] = {
            "name": wf.get("name", ""),
            "categories": categories,
            "author": user.get("name", "Unknown"),
            "totalViews": wf.get("totalViews", 0),
            "nodeCount": wf.get("nodeCount", len(wf.get("nodes", []))),
            "file": str(json_file.relative_to(output_dir)),
        }

    # Write index
    index_path = output_dir / INDEX_FILENAME
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    console.print(f"[green]Index updated: {len(index):,} workflows in {index_path}[/green]")
    return index


# --- Split ---


def run_split_on_file(file_path: Path, output_dir: Path) -> bool:
    """Run split.py on a single downloaded workflow file.

    Args:
        file_path: Path to downloaded workflow JSON.
        output_dir: Output directory for split files.

    Returns:
        True if split succeeded.
    """
    script_dir = Path(__file__).parent
    split_script = script_dir / "split.py"

    if not split_script.exists():
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(split_script), str(file_path), "-o", str(output_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except OSError:
        return False


# --- CLI ---


@click.command()
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
)
@click.option("--fresh", is_flag=True, help="Ignore checkpoint, start fresh crawl")
@click.option("--rediscover", is_flag=True, help="Re-run discovery phase (check for new workflows)")
@click.option("--dry-run", is_flag=True, help="Show plan without downloading")
@click.option(
    "--max-downloads",
    type=int,
    default=0,
    help="Limit number of downloads (0 = unlimited)",
)
@click.option(
    "--delay-min",
    type=float,
    default=DEFAULT_DELAY_MIN,
    help=f"Minimum delay between requests in seconds (default: {DEFAULT_DELAY_MIN})",
)
@click.option(
    "--delay-max",
    type=float,
    default=DEFAULT_DELAY_MAX,
    help=f"Maximum delay between requests in seconds (default: {DEFAULT_DELAY_MAX})",
)
@click.option("--split", "do_split", is_flag=True, help="Run split.py on each download")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging")
def main(
    output_dir: Path,
    fresh: bool,
    rediscover: bool,
    dry_run: bool,
    max_downloads: int,
    delay_min: float,
    delay_max: float,
    do_split: bool,
    verbose: bool,
) -> None:
    """Crawl and download all n8n workflow templates.

    \b
    Discovers all workflow IDs via API pagination, then downloads each
    workflow into category-organized folders with human-like request timing.

    \b
    Supports checkpoint/resume: interrupt with Ctrl+C and re-run to continue
    from where you left off. Discovery results are cached so re-runs skip
    straight to downloading. Use --rediscover to check for new workflows.

    \b
    Examples:
      python scripts/crawl.py                          Resume or start crawl
      python scripts/crawl.py --fresh                  Start fresh
      python scripts/crawl.py --rediscover             Check for new workflows
      python scripts/crawl.py --dry-run                Show plan only
      python scripts/crawl.py --max-downloads 50       Test with 50 downloads
      python scripts/crawl.py --delay-min 2 --delay-max 6  Custom delays
    """
    global _verbose
    _verbose = verbose

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / STATE_FILENAME

    # Load state
    if fresh:
        state: dict[str, Any] = {
            "downloaded_ids": [],
            "failed_ids": [],
            "discovered_ids": [],
            "total_on_api": 0,
        }
        console.print("[yellow]Fresh crawl: ignoring any existing checkpoint[/yellow]")
    else:
        state = load_state(state_path)
        if state["downloaded_ids"]:
            console.print(
                f"[cyan]Resuming: {len(state['downloaded_ids']):,} previously downloaded "
                f"(checkpoint from {state.get('timestamp', 'unknown')})[/cyan]"
            )

    # Scan filesystem for existing downloads
    existing_ids = scan_existing(output_dir)
    state_ids = set(state["downloaded_ids"])
    failed_state_ids = set(state.get("failed_ids", []))
    all_known_ids = existing_ids | state_ids | failed_state_ids

    if (existing_ids | state_ids) and not fresh:
        console.print(
            f"[cyan]Found {len(existing_ids | state_ids):,} existing downloads on disk/state[/cyan]"
        )
    if failed_state_ids and not fresh:
        console.print(
            f"[cyan]Skipping {len(failed_state_ids):,} previously failed IDs "
            f"(use --fresh to retry)[/cyan]"
        )

    # Phase 1: Discovery (use cache if available)
    session = create_session()
    cached_ids: list[int] = state.get("discovered_ids", [])
    need_discovery = fresh or rediscover or not cached_ids

    if need_discovery:
        summaries = fetch_all_ids(session, delay_min, delay_max)
        if not summaries:
            err_console.print("[red]No workflows discovered. Exiting.[/red]")
            sys.exit(1)
        discovered_ids_list = [int(wf["id"]) for wf in summaries if wf.get("id") is not None]
        total_on_api = len(summaries)
    else:
        discovered_ids_list = cached_ids
        total_on_api = state.get("total_on_api", len(cached_ids))
        console.print(
            f"[cyan]Using cached discovery: {len(discovered_ids_list):,} workflow IDs "
            f"(use --rediscover to refresh)[/cyan]"
        )

    # Build download queue (skip known IDs)
    queue: list[int] = [wf_id for wf_id in discovered_ids_list if wf_id not in all_known_ids]
    skipped = len(discovered_ids_list) - len(queue)

    if max_downloads > 0:
        queue = queue[:max_downloads]

    # Cache discovery results so future runs skip Phase 1
    if need_discovery:
        save_state(
            {
                "downloaded_ids": list(state_ids),
                "failed_ids": state.get("failed_ids", []),
                "discovered_ids": discovered_ids_list,
                "total_on_api": total_on_api,
            },
            state_path,
        )

    console.print("\n[bold]Phase 2: Download[/bold]")
    console.print(
        f"  To download: {len(queue):,}  |  "
        f"Skipping: {skipped:,} (already have)  |  "
        f"Total discovered: {total_on_api:,}"
    )

    if dry_run:
        console.print("\n[yellow]Dry run: no downloads performed[/yellow]")
        if queue and _verbose:
            console.print(f"[dim]First 20 IDs in queue: {queue[:20]}[/dim]")
        sys.exit(0)

    if not queue:
        console.print("\n[green]Nothing to download - all workflows already present![/green]")
        build_index(output_dir)
        sys.exit(0)

    # Phase 2: Download with progress
    downloaded_ids: list[int] = list(state_ids)
    failed_ids: list[int] = list(state.get("failed_ids", []))
    new_downloads = 0
    new_failures = 0
    burst_interval = random.randint(DEFAULT_BURST_MIN, DEFAULT_BURST_MAX)

    with Progress(
        TextColumn("[bold blue]Crawling"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[cyan]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("{task.fields[status]}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "download",
            total=len(queue),
            status="starting...",
        )

        for i, wf_id in enumerate(queue):
            if _shutdown_requested:
                console.print("\n[yellow]Graceful shutdown: saving state...[/yellow]")
                break

            progress.update(
                task,
                status=f"| {wf_id}",
            )

            success, name = download_one(session, wf_id, output_dir)

            if success:
                downloaded_ids.append(wf_id)
                new_downloads += 1
                display_name = name[:40] if name else str(wf_id)
                progress.update(
                    task,
                    advance=1,
                    status=f"| {wf_id} - {display_name}",
                )

                if do_split:
                    # Find the file we just wrote to run split on it
                    for json_file in output_dir.rglob(f"{wf_id}-*.json"):
                        if json_file.name != INDEX_FILENAME:
                            run_split_on_file(json_file, output_dir)
                            break
            else:
                failed_ids.append(wf_id)
                new_failures += 1
                progress.update(task, advance=1, status=f"| {wf_id} FAILED")

            # Save state periodically (every 50 downloads)
            if (new_downloads + new_failures) % 50 == 0:
                save_state(
                    {
                        "downloaded_ids": downloaded_ids,
                        "failed_ids": failed_ids,
                        "discovered_ids": discovered_ids_list,
                        "total_on_api": total_on_api,
                    },
                    state_path,
                )

            # Human delay before next request
            if i < len(queue) - 1 and not _shutdown_requested:
                human_delay(delay_min, delay_max, i + 1, burst_interval)

    # Final state save
    save_state(
        {
            "downloaded_ids": downloaded_ids,
            "failed_ids": failed_ids,
            "discovered_ids": discovered_ids_list,
            "total_on_api": total_on_api,
        },
        state_path,
    )

    # Build index
    console.print()
    build_index(output_dir)

    # Summary
    console.print("\n[bold]Crawl Summary[/bold]")
    console.print(f"  [green]New downloads:[/green] {new_downloads:,}")
    console.print(f"  [red]Failed:[/red]         {new_failures:,}")
    console.print(f"  [cyan]Total on disk:[/cyan]  {len(downloaded_ids):,}")

    if failed_ids:
        console.print(
            "\n[yellow]Failed IDs saved to state. Re-run to retry or use --fresh to reset.[/yellow]"
        )

    if new_failures > 0 and new_downloads == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
