# Scripts

Utilities for searching, downloading, and processing n8n workflow templates.

---

## Python Setup

The Python CLI scripts require Python 3.11+ and are the recommended interface.

### Quick Start

```bash
# Create virtual environment (from project root)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r scripts/requirements.txt

# Verify installation
python scripts/search.py --help
```

### Development

```bash
# Install ruff for linting/formatting
pip install ruff

# Run linter
ruff check scripts/

# Run formatter
ruff format scripts/
```

### Utilities Package

The `scripts/utils/` package provides shared functionality:

| Module | Purpose |
|--------|---------|
| `logging.py` | Structured logging with colored output via rich |
| `cli.py` | Shared click decorators for common CLI options |
| `paths.py` | Cross-platform path utilities using pathlib |

---

## Python CLI Reference

### search.py

Search and explore n8n workflow templates using the public API.

#### Main Command

```
Usage: search.py [OPTIONS] COMMAND [ARGS]...

  Search n8n workflow templates using the public API.

Options:
  -v, --verbose  Show verbose output including API URLs
  --help         Show this message and exit.

Commands:
  categories   List all available workflow categories.
  collection   Get details for a specific collection.
  collections  List all curated workflow collections.
  search       Search workflow templates.
  stats        Show API statistics.
```

#### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Show verbose output including API URLs |
| `--help` | Show this message and exit |

---

#### search subcommand

Search workflow templates with filters and pagination.

```bash
# Basic keyword search
python scripts/search.py search "real estate"

# Filter by category
python scripts/search.py search --category AI

# Filter by apps/integrations
python scripts/search.py search --apps "Telegram,OpenAI"

# Combined filters with pagination
python scripts/search.py search "chatbot" --category AI --rows 20 --page 2

# Output formats
python scripts/search.py search "automation" --json
python scripts/search.py search "automation" --ids --save
python scripts/search.py search "automation" --compact
```

**Options:**

| Option | Description |
|--------|-------------|
| `QUERY` | Search query string (optional positional argument) |
| `-c, --category TEXT` | Filter by category (comma-separated) |
| `-a, --apps TEXT` | Filter by app/integration names (comma-separated) |
| `-n, --nodes TEXT` | Filter by node type names (comma-separated) |
| `-r, --rows INTEGER` | Number of results (default: 10, max: 100) |
| `-p, --page INTEGER` | Page number (default: 1) |
| `-s, --skip INTEGER` | Skip N results (overrides --page) |
| `-o, --output [table\|json\|ids\|compact]` | Output format (default: table) |
| `--json` | Shorthand for --output json |
| `--ids` | Shorthand for --output ids |
| `--compact` | Shorthand for --output compact |
| `--save` | Save results to search_results/ folder |
| `--help` | Show this message and exit |

**Output Formats:**

| Format | Description |
|--------|-------------|
| `table` | Formatted table with ID, name, views, author (default) |
| `json` | Raw API response in JSON format |
| `ids` | Workflow IDs only, one per line (for piping) |
| `compact` | One-line-per-result minimal format |

---

#### categories subcommand

List all available workflow categories.

```bash
# Table format (default)
python scripts/search.py categories

# JSON format
python scripts/search.py categories --json
```

**Options:**

| Option | Description |
|--------|-------------|
| `-o, --output [table\|json]` | Output format (default: table) |
| `--json` | Shorthand for --output json |
| `--help` | Show this message and exit |

---

#### collections subcommand

List all curated workflow collections.

```bash
# Table format (default)
python scripts/search.py collections

# JSON format
python scripts/search.py collections --json
```

**Options:**

| Option | Description |
|--------|-------------|
| `-o, --output [table\|json]` | Output format (default: table) |
| `--json` | Shorthand for --output json |
| `--help` | Show this message and exit |

---

#### collection subcommand

Get details for a specific collection by ID.

```bash
# Show collection details with workflows
python scripts/search.py collection 8

# Output workflow IDs only
python scripts/search.py collection 8 --ids

# JSON format
python scripts/search.py collection 8 --json
```

**Options:**

| Option | Description |
|--------|-------------|
| `ID` | Collection ID (required positional argument) |
| `-o, --output [table\|json\|ids]` | Output format (default: table) |
| `--json` | Shorthand for --output json |
| `--ids` | Shorthand for --output ids |
| `--help` | Show this message and exit |

---

#### stats subcommand

Show API statistics including total workflows, categories, and collections.

```bash
python scripts/search.py stats
```

**Options:**

| Option | Description |
|--------|-------------|
| `--help` | Show this message and exit |

---

### download.py

Download n8n workflow templates from the public API.

```bash
# Download by ID
python scripts/download.py 5428

# Download multiple workflows
python scripts/download.py 5428 6332

# Download from URL (ID extracted automatically)
python scripts/download.py "https://n8n.io/workflows/5428-workflow-name/"

# Batch download from file
python scripts/download.py --file workflows.txt

# Download and split immediately
python scripts/download.py --split 5428

# Custom output directory
python scripts/download.py --output ./my-workflows 5428

# Verbose mode
python scripts/download.py --verbose 5428
```

**Options:**

| Option | Description |
|--------|-------------|
| `IDS` | Workflow IDs or URLs (positional arguments) |
| `-o, --output PATH` | Output directory (default: n8n-workflows) |
| `-f, --file PATH` | Read IDs/URLs from file (one per line) |
| `--split` | Run split-workflows.sh after download |
| `-v, --verbose` | Show verbose output including API URLs |
| `--help` | Show this message and exit |

**Output:**

- Downloads to `n8n-workflows/` by default
- Files named: `{id}-{sanitized-workflow-name}.json`
- Exit code 0 on success, 1 if any downloads fail

**API:**

Uses: `https://api.n8n.io/api/templates/workflows/{ID}`

---

### split.py

Split n8n workflow JSON files into organized chunks for easier analysis.

```bash
# Process all files in n8n-workflows/
python scripts/split.py

# Process a single file
python scripts/split.py workflow.json

# Custom line threshold
python scripts/split.py --threshold 500

# Custom input/output directories
python scripts/split.py --input-dir /path/to/input
python scripts/split.py --output-dir /path/to/output

# Verbose mode
python scripts/split.py --verbose
```

**Options:**

| Option | Description |
|--------|-------------|
| `WORKFLOW_FILE` | Single workflow file to process (optional positional argument) |
| `-t, --threshold INTEGER` | Line threshold before splitting (default: 300) |
| `-i, --input-dir DIRECTORY` | Input directory containing workflow JSON files (default: n8n-workflows) |
| `-o, --output-dir DIRECTORY` | Output directory for split files (default: n8n-workflows) |
| `-v, --verbose` | Show verbose output including processing details |
| `--help` | Show this message and exit |

**Output Structure:**

Workflows under threshold get a single `workflow.json`. Larger workflows split into:

```
{workflow-name}/
  01-metadata.json      # ID, name, description, author, views
  02-settings.json      # Workflow settings, tags, meta
  03-connections.json   # Node connection graph
  04-nodes.json         # All nodes (if under threshold)
  05-template-nodes.json # Template display nodes (if present)
  06-image.json         # Preview image URL (if present)
  nodes/                # Individual nodes (if over threshold)
    _index.json         # Node index with names/types
    00-trigger-Start.json
    01-httpRequest-API_Call.json
    ...
```

**Features:**

- Graceful error handling (continues on invalid JSON)
- Safe filename handling (special characters escaped)
- Idempotent (safe to re-run)
- Reports success/failure counts

---

## Legacy Bash Scripts

> **DEPRECATION NOTICE**: The Bash scripts below are deprecated and maintained for backwards compatibility only. Please use the Python CLI scripts above for all new workflows.

### search-workflows.sh (Deprecated)

> Use `python scripts/search.py` instead.

```bash
# Legacy usage
./scripts/search-workflows.sh "real estate"
./scripts/search-workflows.sh --category AI
./scripts/search-workflows.sh --list-categories
```

**Options:**

| Option | Description |
|--------|-------------|
| `-q, --query QUERY` | Search query string |
| `-c, --category CAT` | Filter by category (comma-separated) |
| `-a, --apps APPS` | Filter by apps/integrations (comma-separated) |
| `-n, --nodes NODES` | Filter by node types (comma-separated) |
| `-r, --rows NUM` | Results to return (default: 10, max: 100) |
| `-p, --page NUM` | Page number (auto-calculates skip) |
| `-s, --skip NUM` | Skip N results (manual pagination) |
| `--show-filters` | Show available filter facets in results |
| `-o, --output FMT` | Output format: `table`, `json`, `ids`, `compact` |
| `--json` | Shorthand for `--output json` |
| `--ids` | Shorthand for `--output ids` |
| `--compact` | Shorthand for `--output compact` |
| `--save` | Save results to `search_results/` folder (JSON) |
| `--list-categories` | List all workflow categories |
| `--list-collections` | List curated collections |
| `--collection ID` | Get collection details with workflows |
| `--stats` | Show API statistics |
| `--health` | Check API health status |
| `-v, --verbose` | Show API URLs |
| `-h, --help` | Show help |

---

### download-workflows.sh (Deprecated)

> Use `python scripts/download.py` instead.

```bash
# Legacy usage
./scripts/download-workflows.sh 5428
./scripts/download-workflows.sh --file workflow-list.txt --split
```

**Options:**

| Option | Description |
|--------|-------------|
| `-f, --file FILE` | Read IDs/URLs from file (one per line) |
| `-s, --split` | Run `split-workflows.sh` after downloading |
| `-o, --output DIR` | Output directory (default: `n8n-workflows/`) |
| `-v, --verbose` | Show API URLs and workflow names |
| `-h, --help` | Show help |

---

### split-workflows.sh (Deprecated)

> Use `python scripts/split.py` instead.

```bash
# Legacy usage
./scripts/split-workflows.sh
./scripts/split-workflows.sh 500  # Custom threshold
```

**Options:**

| Argument | Description |
|----------|-------------|
| `line_threshold` | Max formatted lines before splitting (default: 300) |

---

## Migration Guide

Migrating from Bash to Python CLI:

| Bash Command | Python Equivalent |
|--------------|-------------------|
| `./scripts/search-workflows.sh "query"` | `python scripts/search.py search "query"` |
| `./scripts/search-workflows.sh --list-categories` | `python scripts/search.py categories` |
| `./scripts/search-workflows.sh --list-collections` | `python scripts/search.py collections` |
| `./scripts/search-workflows.sh --collection 8` | `python scripts/search.py collection 8` |
| `./scripts/search-workflows.sh --stats` | `python scripts/search.py stats` |
| `./scripts/download-workflows.sh 5428` | `python scripts/download.py 5428` |
| `./scripts/download-workflows.sh --split 5428` | `python scripts/download.py --split 5428` |
| `./scripts/split-workflows.sh` | `python scripts/split.py` |
| `./scripts/split-workflows.sh 500` | `python scripts/split.py --threshold 500` |
