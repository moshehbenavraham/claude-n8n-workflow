# Scripts

## Python Setup

The Python scripts require Python 3.11+ with the following dependencies.

### Setup

```bash
# Create virtual environment (from project root)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r scripts/requirements.txt

# Verify installation
python -c "from scripts.utils import get_logger; print('OK')"
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

### Utilities

The `scripts/utils/` package provides shared functionality:

- **logging.py**: Structured logging with colored output (mirrors logging.sh)
- **cli.py**: Shared click decorators for common CLI options
- **paths.py**: Cross-platform path utilities using pathlib

Example usage:

```python
from scripts.utils import get_logger, common_options
import click

logger = get_logger(verbose=True)
logger.info("Processing started")

@click.command()
@common_options
def my_script(verbose: bool, dry_run: bool):
    logger = get_logger(verbose=verbose)
    if dry_run:
        logger.info("Dry run mode - no changes will be made")
```

---

## search-workflows.sh

Searches and explores n8n workflow templates using the public API.

### Usage

```bash
# Keyword search
./scripts/search-workflows.sh "real estate"
./scripts/search-workflows.sh -q "telegram bot"

# Filter by category, apps, or node types
./scripts/search-workflows.sh --category AI
./scripts/search-workflows.sh --apps "Telegram,OpenAI"
./scripts/search-workflows.sh --nodes "n8n-nodes-base.telegram"

# Combine filters with pagination
./scripts/search-workflows.sh -q "chatbot" -c AI -a Telegram -r 20 --page 2

# Output formats
./scripts/search-workflows.sh "real estate" --json
./scripts/search-workflows.sh "real estate" --ids
./scripts/search-workflows.sh --category AI --compact -r 50

# Save results to file
./scripts/search-workflows.sh "real estate" --save

# Pipe to download script
./scripts/search-workflows.sh "real estate" --ids | xargs ./scripts/download-workflows.sh

# Discovery
./scripts/search-workflows.sh --list-categories
./scripts/search-workflows.sh --list-collections
./scripts/search-workflows.sh --collection 8
./scripts/search-workflows.sh --stats
```

### Options

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
| `--list-categories` | List all 31 workflow categories |
| `--list-collections` | List 8 curated collections |
| `--collection ID` | Get collection details with workflows |
| `--stats` | Show API statistics |
| `--health` | Check API health status |
| `-v, --verbose` | Show API URLs |
| `-h, --help` | Show help |

### Output

- `table` (default): Formatted table with ID, name, views, author
- `json`: Raw API response
- `ids`: Workflow IDs only (one per line, for piping)
- `compact`: One-line-per-result minimal format

### API

Uses: `https://api.n8n.io/api/templates/search`

---

## download-workflows.sh

Downloads n8n workflow JSON files from the n8n template API.

### Usage

```bash
# Single workflow by ID
./scripts/download-workflows.sh 5428

# Multiple workflows
./scripts/download-workflows.sh 5428 6332 6162

# From URL (ID extracted automatically)
./scripts/download-workflows.sh "https://n8n.io/workflows/5428-workflow-name/"

# From file (one ID or URL per line, supports # comments)
./scripts/download-workflows.sh --file workflow-list.txt

# Download and split into smaller files
./scripts/download-workflows.sh --split 5428

# Custom output directory
./scripts/download-workflows.sh --output ./my-workflows 5428

# Verbose mode (shows API URL and workflow name)
./scripts/download-workflows.sh --verbose 5428

# Combine options
./scripts/download-workflows.sh --file list.txt --split --verbose
```

### Options

| Option | Description |
|--------|-------------|
| `-f, --file FILE` | Read IDs/URLs from file (one per line) |
| `-s, --split` | Run `split-workflows.sh` after downloading |
| `-o, --output DIR` | Output directory (default: `n8n-workflows/`) |
| `-v, --verbose` | Show API URLs and workflow names |
| `-h, --help` | Show help |

### Output

- Downloads to `n8n-workflows/` by default
- Files named: `{id}-{sanitized-workflow-name}.json`
- Exit code 0 on success, 1 if any downloads fail

### API

Uses: `https://api.n8n.io/api/templates/workflows/{ID}`

## split-workflows.sh

Splits n8n workflow JSON files into organized, manageable chunks for easier analysis.

### Usage

```bash
# Default threshold (300 lines)
./scripts/split-workflows.sh

# Custom line threshold
./scripts/split-workflows.sh 500
```

### Options

| Argument | Description |
|----------|-------------|
| `line_threshold` | Max formatted lines before splitting (default: 300) |

### Output Structure

Workflows under threshold get a single `workflow.json`. Larger workflows split into:

```
{workflow-name}/
├── 01-metadata.json      # ID, name, description, author, views
├── 02-settings.json      # Workflow settings, tags, meta
├── 03-connections.json   # Node connection graph
├── 04-nodes.json         # All nodes (if under threshold)
├── 05-template-nodes.json # Template display nodes (if present)
├── 06-image.json         # Preview image URL (if present)
└── nodes/                # Individual nodes (if over threshold)
    ├── _index.json       # Node index with names/types
    ├── 00-trigger-Start.json
    ├── 01-httpRequest-API_Call.json
    └── ...
```

### Features

- Graceful error handling (continues on invalid JSON)
- Safe filename handling (special characters escaped)
- Idempotent (safe to re-run)
- Reports success/failure counts
