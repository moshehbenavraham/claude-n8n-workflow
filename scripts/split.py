#!/usr/bin/env python3
"""
Split n8n workflow JSON files into organized, manageable chunks.

Intelligently splits large workflow files into separate components:
- metadata, settings, connections, nodes
- Individual node files when node array exceeds threshold

Usage:
    python scripts/split.py                              # All files in n8n-workflows/
    python scripts/split.py workflow.json               # Single file
    python scripts/split.py --threshold 500             # Custom threshold
    python scripts/split.py --input-dir /path           # Custom input directory
    python scripts/split.py --output-dir /path          # Custom output directory
    python scripts/split.py --verbose                   # Debug output
"""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Default configuration
DEFAULT_INPUT_DIR = "n8n-workflows"
DEFAULT_OUTPUT_DIR = "n8n-workflows"
DEFAULT_THRESHOLD = 300

# Characters to replace in filenames (cross-platform compatibility)
UNSAFE_FILENAME_CHARS = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "\n", "\r", "\t"]

# Console for Rich output
console = Console()
err_console = Console(stderr=True)

# Global verbose flag
_verbose = False


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in a filename.

    Replaces unsafe filesystem characters with underscores.

    Args:
        name: Original string (e.g., node name, workflow name).

    Returns:
        Sanitized string safe for use in filenames.
    """
    result = name
    for char in UNSAFE_FILENAME_CHARS:
        result = result.replace(char, "_")
    return result


def count_formatted_lines(data: dict | list) -> int:
    """Count lines when JSON data is formatted with indent=2.

    Args:
        data: JSON-serializable data structure.

    Returns:
        Number of lines in the formatted JSON output.
    """
    return len(json.dumps(data, indent=2).split("\n"))


def write_json(filepath: Path, data: dict | list, indent: int = 2) -> int:
    """Write JSON data to file with consistent formatting.

    Args:
        filepath: Path to write the JSON file.
        data: JSON-serializable data to write.
        indent: Indentation level (default: 2).

    Returns:
        Number of lines written.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    # Return line count
    with open(filepath, encoding="utf-8") as f:
        return len(f.readlines())


def find_json_files(directory: Path) -> list[Path]:
    """Find all JSON files in a directory.

    Args:
        directory: Directory to search.

    Returns:
        List of paths to JSON files, sorted alphabetically.
    """
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


def extract_metadata(workflow: dict) -> dict:
    """Extract metadata fields from workflow.

    Args:
        workflow: Workflow data dict.

    Returns:
        Dict containing only metadata fields (id, name, description, etc.).
    """
    metadata_keys = [
        "id",
        "name",
        "description",
        "createdAt",
        "views",
        "totalViews",
        "status",
        "user",
        "categories",
        "workflowInfo",
        "lastUpdatedBy",
    ]
    metadata = {k: workflow.get(k) for k in metadata_keys if workflow.get(k) is not None}
    return metadata


def extract_settings(inner_workflow: dict) -> dict:
    """Extract settings/meta fields from inner workflow.

    Args:
        inner_workflow: Inner workflow data dict.

    Returns:
        Dict containing settings fields (id, name, meta, tags, etc.).
    """
    settings_keys = [
        "id",
        "name",
        "meta",
        "tags",
        "active",
        "pinData",
        "settings",
        "versionId",
    ]
    settings = {
        k: inner_workflow.get(k) for k in settings_keys if inner_workflow.get(k) is not None
    }
    return settings


def extract_connections(inner_workflow: dict) -> dict:
    """Extract connections from inner workflow.

    Args:
        inner_workflow: Inner workflow data dict.

    Returns:
        Connections dict.
    """
    return inner_workflow.get("connections", {})


def extract_nodes(inner_workflow: dict) -> list:
    """Extract nodes array from inner workflow.

    Args:
        inner_workflow: Inner workflow data dict.

    Returns:
        List of node objects.
    """
    return inner_workflow.get("nodes", [])


def split_nodes_to_files(nodes: list, nodes_dir: Path) -> int:
    """Split nodes into individual files in a nodes/ subdirectory.

    Creates individual files for each node plus an index file.

    Args:
        nodes: List of node objects.
        nodes_dir: Directory to write node files.

    Returns:
        Number of files created.
    """
    nodes_dir.mkdir(parents=True, exist_ok=True)

    node_index = []
    for i, node in enumerate(nodes):
        node_name = sanitize_filename(node.get("name", f"node_{i}"))
        node_type = node.get("type", "unknown").split(".")[-1]
        filename = f"{i:02d}-{node_type}-{node_name[:30]}.json"

        write_json(nodes_dir / filename, node)
        node_index.append(
            {
                "index": i,
                "file": filename,
                "name": node.get("name"),
                "type": node.get("type"),
            }
        )

    write_json(nodes_dir / "_index.json", node_index)
    return len(nodes) + 1  # nodes + index file


def handle_template_nodes(workflow: dict, nodes: list, output_dir: Path) -> bool:
    """Handle outer template nodes if they differ from inner nodes.

    Args:
        workflow: Outer workflow data.
        nodes: Inner workflow nodes.
        output_dir: Directory to write files.

    Returns:
        True if template nodes file was created.
    """
    outer_nodes = workflow.get("nodes", [])
    if outer_nodes and outer_nodes != nodes:
        write_json(output_dir / "05-template-nodes.json", outer_nodes)
        return True
    return False


def split_workflow(
    json_file: Path,
    output_dir: Path,
    threshold: int,
) -> dict:
    """Split a single workflow JSON file.

    Args:
        json_file: Path to input JSON file.
        output_dir: Base directory for output.
        threshold: Line threshold for splitting.

    Returns:
        Dict with keys: success, output_dir, file_count, error (if failed).
    """
    # Extract base name (remove .json extension)
    base_name = json_file.stem
    workflow_output_dir = output_dir / base_name

    try:
        # Load the workflow
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "output_dir": workflow_output_dir,
            "file_count": 0,
            "error": f"Invalid JSON: {e}",
        }
    except OSError as e:
        return {
            "success": False,
            "output_dir": workflow_output_dir,
            "file_count": 0,
            "error": f"Read error: {e}",
        }

    total_lines = count_formatted_lines(data)

    if _verbose:
        console.print(f"  [dim]Total formatted lines: {total_lines}[/dim]")

    # Create output directory
    workflow_output_dir.mkdir(parents=True, exist_ok=True)
    file_count = 0

    # Check if small enough to keep intact
    if total_lines <= threshold:
        write_json(workflow_output_dir / "workflow.json", data)
        file_count = 1
        if _verbose:
            console.print(f"  [dim]Compact workflow ({total_lines} lines), kept intact[/dim]")
        return {
            "success": True,
            "output_dir": workflow_output_dir,
            "file_count": file_count,
            "compact": True,
        }

    # Extract the main workflow object
    # Handle both n8n export format (workflow.workflow) and API format (workflow)
    workflow = data.get("workflow", data)
    inner_workflow = workflow.get("workflow", {})

    # If inner_workflow is empty, the workflow object itself contains the nodes/connections
    # This happens with API downloads where structure is {workflow: {meta, nodes, connections}}
    if not inner_workflow:
        inner_workflow = workflow

    # 1. Extract metadata (from top-level data for API format, or workflow for export format)
    metadata = extract_metadata(data) or extract_metadata(workflow)
    if metadata:
        write_json(workflow_output_dir / "01-metadata.json", metadata)
        file_count += 1

    # 2. Extract settings
    if inner_workflow:
        settings = extract_settings(inner_workflow)
        if settings:
            write_json(workflow_output_dir / "02-settings.json", settings)
            file_count += 1

    # 3. Extract connections
    connections = extract_connections(inner_workflow)
    if connections:
        write_json(workflow_output_dir / "03-connections.json", connections)
        file_count += 1

    # 4. Extract nodes
    nodes = extract_nodes(inner_workflow)
    if nodes:
        nodes_lines = count_formatted_lines(nodes)

        if nodes_lines <= threshold:
            # Keep all nodes in one file
            write_json(workflow_output_dir / "04-nodes.json", nodes)
            file_count += 1
        else:
            # Split nodes into individual files
            nodes_dir = workflow_output_dir / "nodes"
            node_file_count = split_nodes_to_files(nodes, nodes_dir)
            file_count += node_file_count

    # 5. Handle template nodes (at top level for API format, in workflow for export format)
    if handle_template_nodes(data, nodes, workflow_output_dir):
        file_count += 1

    # 6. Save image URL if present (at top level for API format)
    image_url = data.get("image") or workflow.get("image")
    if image_url:
        image_data = {"image": image_url}
        write_json(workflow_output_dir / "06-image.json", image_data)
        file_count += 1

    return {
        "success": True,
        "output_dir": workflow_output_dir,
        "file_count": file_count,
        "compact": False,
    }


@click.command()
@click.argument("workflow_file", required=False, type=click.Path(path_type=Path))
@click.option(
    "-t",
    "--threshold",
    default=DEFAULT_THRESHOLD,
    type=int,
    help=f"Line threshold before splitting (default: {DEFAULT_THRESHOLD})",
)
@click.option(
    "-i",
    "--input-dir",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help=f"Input directory containing workflow JSON files (default: {DEFAULT_INPUT_DIR})",
)
@click.option(
    "-o",
    "--output-dir",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help=f"Output directory for split files (default: {DEFAULT_OUTPUT_DIR})",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show verbose output including processing details",
)
def main(
    workflow_file: Path | None,
    threshold: int,
    input_dir: Path | None,
    output_dir: Path | None,
    verbose: bool,
) -> None:
    """Split n8n workflow JSON files into organized chunks.

    \b
    Examples:
      python scripts/split.py                              All files in n8n-workflows/
      python scripts/split.py workflow.json               Single file
      python scripts/split.py --threshold 500             Custom threshold
      python scripts/split.py --input-dir /path           Custom input directory
      python scripts/split.py --output-dir /path          Custom output directory
    """
    global _verbose
    _verbose = verbose

    # Determine input files
    if workflow_file:
        # Single file mode
        if not workflow_file.exists():
            err_console.print(f"[red]Error: File not found: {workflow_file}[/red]")
            sys.exit(1)
        json_files = [workflow_file]
        effective_input = workflow_file.parent
    else:
        # Directory mode
        effective_input = input_dir or Path(DEFAULT_INPUT_DIR)
        if not effective_input.exists():
            err_console.print(f"[red]Error: Input directory not found: {effective_input}[/red]")
            sys.exit(1)
        json_files = find_json_files(effective_input)

    # Determine output directory
    effective_output = output_dir or Path(DEFAULT_OUTPUT_DIR)

    # Print header
    console.print("[bold]=== n8n Workflow Splitter ===[/bold]")
    console.print(f"[cyan]Threshold:[/cyan] {threshold} lines")
    console.print(f"[cyan]Input:[/cyan] {effective_input}")
    console.print(f"[cyan]Output:[/cyan] {effective_output}")
    console.print()

    # Check for files
    if not json_files:
        err_console.print("[yellow]No JSON files found to process.[/yellow]")
        sys.exit(0)

    console.print(f"Processing {len(json_files)} workflow(s)...\n")

    # Process files with progress tracking
    results = []
    success_count = 0
    failure_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing...", total=len(json_files))

        for json_file in json_files:
            progress.update(task, description=f"Processing {json_file.name}...")

            result = split_workflow(json_file, effective_output, threshold)
            result["name"] = json_file.name
            results.append(result)

            if result["success"]:
                success_count += 1
                status = "compact" if result.get("compact") else "split"
                files = result["file_count"]
                console.print(f"[green]OK[/green] {json_file.name} -> {files} file(s) ({status})")
            else:
                failure_count += 1
                err_console.print(
                    f"[red]FAIL[/red] {json_file.name}: {result.get('error', 'Unknown error')}"
                )

            progress.advance(task)

    # Print summary table
    console.print()
    table = Table(title="Split Summary", show_header=True, header_style="bold")
    table.add_column("Workflow", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Files", justify="right")
    table.add_column("Output Directory", style="dim")

    for result in results:
        status = "[green]OK[/green]" if result["success"] else "[red]FAIL[/red]"
        files = str(result["file_count"]) if result["success"] else "-"
        output_path = (
            str(result["output_dir"].relative_to(effective_output)) if result["success"] else "-"
        )
        table.add_row(result["name"], status, files, output_path)

    console.print(table)

    # Print final summary
    console.print()
    if success_count > 0:
        console.print(f"[green]Success: {success_count} workflow(s) processed[/green]")
    if failure_count > 0:
        console.print(f"[red]Failed: {failure_count} workflow(s)[/red]")

    # Exit code: 0 if all succeeded, 1 if any failed
    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
