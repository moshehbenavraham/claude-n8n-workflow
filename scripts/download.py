#!/usr/bin/env python3
"""
Download n8n workflow templates from the public API.

Usage:
    python scripts/download.py 5428                              # Download by ID
    python scripts/download.py "https://n8n.io/workflows/5428-name/"  # From n8n.io URL
    python scripts/download.py 5428 6332 6162                    # Download multiple
    python scripts/download.py --file workflows.txt              # Batch from file
    python scripts/download.py --split 5428                      # Download and split

API Reference: docs/n8n-public-API.md
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import click
import requests
from rich.console import Console

# API Configuration
API_BASE = "https://api.n8n.io/api/templates/workflows"

# Default values
DEFAULT_OUTPUT_DIR = "n8n-workflows"
REQUEST_TIMEOUT = 30

# URL patterns for extracting workflow IDs
# Pattern 1: n8n.io URL - https://n8n.io/workflows/5428-workflow-name/
URL_PATTERN_N8N_IO = re.compile(r"n8n\.io/workflows/(\d+)")
# Pattern 2: API URL - https://api.n8n.io/api/templates/workflows/5428
URL_PATTERN_API = re.compile(r"api\.n8n\.io/api/templates/workflows/(\d+)")

# Console for Rich output
console = Console()
err_console = Console(stderr=True)

# Global verbose flag
_verbose = False


def extract_workflow_id(input_str: str) -> int | None:
    """Extract workflow ID from various input formats.

    Supports:
    - Numeric ID: "5428"
    - n8n.io URL: "https://n8n.io/workflows/5428-name/"
    - API URL: "https://api.n8n.io/api/templates/workflows/5428"

    Returns:
        Workflow ID as integer, or None if extraction fails.
    """
    input_str = input_str.strip()

    # Try numeric ID first
    if input_str.isdigit():
        return int(input_str)

    # Try n8n.io URL pattern
    match = URL_PATTERN_N8N_IO.search(input_str)
    if match:
        return int(match.group(1))

    # Try API URL pattern
    match = URL_PATTERN_API.search(input_str)
    if match:
        return int(match.group(1))

    return None


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Convert workflow name to filesystem-safe filename.

    Args:
        name: Workflow name from API.
        max_length: Maximum length for the sanitized name.

    Returns:
        Sanitized string safe for use in filenames.
    """
    # Replace spaces and unsafe characters with hyphens
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
    # Collapse multiple hyphens
    while "--" in safe:
        safe = safe.replace("--", "-")
    # Remove leading/trailing hyphens
    safe = safe.strip("-")
    # Truncate if needed
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip("-")
    return safe or "workflow"


def api_download(workflow_id: int) -> dict | None:
    """Download workflow data from API.

    Args:
        workflow_id: Numeric workflow ID.

    Returns:
        Workflow data as dict, or None on failure.
    """
    url = f"{API_BASE}/{workflow_id}"

    if _verbose:
        err_console.print(f"[dim]API: {url}[/dim]")

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Check for API error in response body
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            err_console.print(f"[red]Error: {error_msg}[/red]")
            return None

        return data

    except requests.exceptions.Timeout:
        err_console.print(f"[red]Error: Request timed out for workflow {workflow_id}[/red]")
        return None
    except requests.exceptions.ConnectionError:
        err_console.print(f"[red]Error: Could not connect to API for workflow {workflow_id}[/red]")
        return None
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 404:
            err_console.print(f"[red]Error: Workflow {workflow_id} not found[/red]")
        else:
            err_console.print(f"[red]Error: API request failed (HTTP {status})[/red]")
        return None
    except json.JSONDecodeError:
        err_console.print(f"[red]Error: Invalid JSON response for workflow {workflow_id}[/red]")
        return None


def download_workflow(workflow_id: int, output_dir: Path) -> Path | None:
    """Download a single workflow and save to file.

    Uses temp file pattern: write to temp, validate, then move to final location.

    Args:
        workflow_id: Numeric workflow ID.
        output_dir: Directory to save the workflow JSON.

    Returns:
        Path to saved file on success, None on failure.
    """
    # Fetch workflow data from API
    data = api_download(workflow_id)
    if data is None:
        return None

    # Extract workflow info for filename
    workflow_data = data.get("workflow", {})
    workflow_name = workflow_data.get("name", "")
    sanitized_name = sanitize_filename(workflow_name) if workflow_name else "workflow"

    # Build filename: ID-sanitized-name.json
    filename = f"{workflow_id}-{sanitized_name}.json"
    final_path = output_dir / filename

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write to temp file first, then move (atomic write pattern)
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            dir=output_dir,
            delete=False,
            encoding="utf-8",
        ) as tmp_file:
            json.dump(workflow_data, tmp_file, indent=2)
            tmp_path = Path(tmp_file.name)

        # Validate JSON by re-reading
        with open(tmp_path, encoding="utf-8") as f:
            json.load(f)

        # Move temp file to final location
        tmp_path.replace(final_path)

        if _verbose:
            console.print(f"[dim]Saved: {final_path}[/dim]")

        return final_path

    except (OSError, json.JSONDecodeError) as e:
        err_console.print(f"[red]Error: Failed to save workflow {workflow_id}: {e}[/red]")
        # Clean up temp file if it exists
        if "tmp_path" in locals() and tmp_path.exists():
            tmp_path.unlink()
        return None


def read_ids_from_file(file_path: Path) -> list[str]:
    """Read workflow IDs/URLs from a file.

    Args:
        file_path: Path to file containing IDs/URLs (one per line).

    Returns:
        List of ID/URL strings (comments and blank lines skipped).
    """
    ids = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip blank lines and comments
                if not line or line.startswith("#"):
                    continue
                ids.append(line)
    except OSError as e:
        err_console.print(f"[red]Error: Could not read file {file_path}: {e}[/red]")
    return ids


def run_split_script(downloaded_files: list[Path]) -> bool:
    """Run split-workflows.sh on downloaded files.

    Args:
        downloaded_files: List of paths to downloaded workflow JSON files.

    Returns:
        True if split succeeded, False otherwise.
    """
    if not downloaded_files:
        return True

    # Find split script relative to this script
    script_dir = Path(__file__).parent
    split_script = script_dir / "split-workflows.sh"

    if not split_script.exists():
        err_console.print(f"[red]Error: Split script not found: {split_script}[/red]")
        return False

    for file_path in downloaded_files:
        if _verbose:
            console.print(f"[dim]Splitting: {file_path}[/dim]")

        try:
            result = subprocess.run(
                ["bash", str(split_script), str(file_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                err_console.print(f"[yellow]Warning: Split failed for {file_path}[/yellow]")
                if _verbose and result.stderr:
                    err_console.print(f"[dim]{result.stderr}[/dim]")
        except OSError as e:
            err_console.print(f"[red]Error running split script: {e}[/red]")
            return False

    return True


@click.command()
@click.argument("ids", nargs=-1)
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
)
@click.option(
    "-f",
    "--file",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="Read IDs/URLs from file (one per line)",
)
@click.option(
    "--split",
    is_flag=True,
    help="Run split-workflows.sh after download",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show verbose output including API URLs",
)
def main(
    ids: tuple[str, ...],
    output_dir: Path,
    input_file: Path | None,
    split: bool,
    verbose: bool,
) -> None:
    """Download n8n workflow templates from the public API.

    \b
    Examples:
      python scripts/download.py 5428                    Download by ID
      python scripts/download.py 5428 6332               Download multiple
      python scripts/download.py "https://n8n.io/..."    Download from URL
      python scripts/download.py --file workflows.txt    Batch from file
      python scripts/download.py --split 5428            Download and split
    """
    global _verbose
    _verbose = verbose

    # Collect all inputs
    all_inputs: list[str] = list(ids)

    if input_file:
        file_inputs = read_ids_from_file(input_file)
        all_inputs.extend(file_inputs)

    if not all_inputs:
        err_console.print("[yellow]No workflow IDs or URLs provided.[/yellow]\n")
        console.print("Usage examples:")
        console.print("  download.py 5428                    # Download by ID")
        console.print('  download.py "https://n8n.io/..."    # Download from URL')
        console.print("  download.py --file workflows.txt    # Batch from file")
        console.print("  download.py --help                  # Full usage")
        sys.exit(1)

    # Process all inputs
    success_count = 0
    fail_count = 0
    downloaded_files: list[Path] = []

    console.print(f"[bold]Downloading {len(all_inputs)} workflow(s)...[/bold]\n")

    for input_str in all_inputs:
        workflow_id = extract_workflow_id(input_str)

        if workflow_id is None:
            err_console.print(f"[yellow]Skipping invalid input: {input_str}[/yellow]")
            fail_count += 1
            continue

        result = download_workflow(workflow_id, output_dir)

        if result:
            console.print(f"[green]Downloaded:[/green] {result.name}")
            downloaded_files.append(result)
            success_count += 1
        else:
            fail_count += 1

    # Summary
    console.print()
    if success_count > 0:
        console.print(f"[green]Success: {success_count} workflow(s) downloaded[/green]")
    if fail_count > 0:
        console.print(f"[red]Failed: {fail_count} workflow(s)[/red]")

    # Run split if requested
    if split and downloaded_files:
        console.print("\n[bold]Running split script...[/bold]")
        run_split_script(downloaded_files)

    # Exit code: 0 if all succeeded, 1 if any failed
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
