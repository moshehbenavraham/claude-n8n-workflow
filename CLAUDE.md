# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLI toolkit for searching, downloading, and analyzing n8n workflow templates. Python scripts interact with the n8n public API to find workflows, download them, split large JSONs into analyzable chunks, and then Claude Code skills/agents analyze and consolidate findings.

## Common Commands

```bash
# Environment setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

# Search workflows
python scripts/search.py search "query"
python scripts/search.py search "chatbot" --category AI --rows 20 --page 2
python scripts/search.py search "automation" --json        # Output as JSON
python scripts/search.py search "automation" --ids --save  # Save IDs to file
python scripts/search.py categories                        # List all categories
python scripts/search.py collections                       # List curated collections
python scripts/search.py collection 8                      # Collection details
python scripts/search.py stats                             # API statistics

# Download workflows
python scripts/download.py 5428                              # Single ID
python scripts/download.py 5428 6332 6162                    # Multiple IDs
python scripts/download.py "https://n8n.io/workflows/5428"   # From URL
python scripts/download.py --file workflow-ids.txt           # Batch from file
python scripts/download.py --split 5428                      # Download and split

# Crawl all workflows (download everything missing)
python scripts/crawl.py                         # Resume or start full crawl
python scripts/crawl.py --fresh                 # Start over, ignore checkpoint
python scripts/crawl.py --rediscover            # Re-check API for new workflows
python scripts/crawl.py --dry-run               # Show plan without downloading
python scripts/crawl.py --max-downloads 50      # Limit count (for testing)
python scripts/crawl.py --delay-min 2 --delay-max 6  # Custom delay range
python scripts/crawl.py --split                 # Run split.py on each download

# Split existing workflows
python scripts/split.py

# Linting/formatting
ruff check scripts/
ruff format scripts/
mypy scripts/ --config-file pyproject.toml

# Run tests
pytest tests/ --cov=scripts

# Pre-commit hooks
uvx pre-commit install
uvx pre-commit run --all-files
```

## Bulk Search & Download Workflow

To search and download all workflows for a topic:

### 1. Define Search Terms
Group related terms by category:
```
voice ai, voice agent, elevenlabs, vapi, retell, twilio, whisper, tts, text-to-speech
```

### 2. Run Searches in Parallel
```bash
source .venv/bin/activate

# Run multiple searches (use --save to persist results)
python scripts/search.py search "term1" --rows 100 --save
python scripts/search.py search "term2" --rows 100 --save
# ... repeat for all terms

# If any search returns 100 results, paginate:
python scripts/search.py search "term" --rows 100 --page 2 --save
```

### 3. Combine & Deduplicate IDs
```bash
jq -r '.workflows[].id' search_results/*.json | sort -un > workflow-ids.txt
echo "Total unique: $(wc -l < workflow-ids.txt)"
```

### 4. Download All Workflows
```bash
python scripts/download.py --file workflow-ids.txt
```

### 5. Organize Results
```bash
mkdir -p topic_folder/{search_results,workflows}
mv search_results/YYYYMMDD-*.json topic_folder/search_results/
mv workflow-ids.txt topic_folder/
while read id; do mv n8n-workflows/${id}-*.json topic_folder/workflows/ 2>/dev/null; done < topic_folder/workflow-ids.txt
```

## Architecture

### Data Pipeline

```
n8n API → search.py → download.py → split.py → [analysis skill] → [consolidation skill]
                ↓           ↓            ↓              ↓                  ↓
         search_results/  n8n-workflows/  (split folders)  analysis/   docs/consolidated-solution.md

n8n API → crawl.py → n8n-workflows/{Category}/*.json + index.json
           (discovers all IDs via pagination, downloads missing, checkpoint/resume)
```

### Directory Structure

| Folder | Purpose |
|--------|---------|
| `n8n-workflows/` | Downloaded workflows (raw JSON and split folders) |
| `search_results/` | Saved API search results |
| `analysis/` | Generated workflow analysis markdown |
| `archive/` | Processed workflow folders (moved after analysis) |
| `docs/` | Consolidated solutions |
| `scripts/` | Python CLI tools |
| `.claude/` | Claude Code agents and skills |

### Split Workflow Structure

Large workflows are split into:
```
workflow-folder/
├── 01-metadata.json      # Name, description, author
├── 02-settings.json      # Settings, tags
├── 03-connections.json   # Node-to-node connections
├── 05-template-nodes.json # Display nodes (optional)
└── nodes/
    ├── _index.json       # Node manifest
    └── NN-type-Name.json # Individual nodes
```

### Claude Code Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `n8n-workflow-analyzer` | "analyze workflow in [folder]" | Parallel analysis via 4 sub-agents |
| `analysis-consolidator` | "consolidate analyses" | Batch extraction → aggregation → architecture doc |

### Sub-Agents (7 total)

| Agent | Model | Purpose |
|-------|-------|---------|
| metadata-analyzer | haiku | Workflow context from metadata files |
| flow-analyzer | haiku | Data flow from connections |
| node-analyzer | sonnet | Individual node configurations |
| docs-extractor | haiku | Documentation from stickyNote nodes |
| analysis-extractor | sonnet | Pattern extraction from analysis docs |
| pattern-aggregator | sonnet | Combine extraction batches |
| solution-architect | sonnet | Create consolidated architecture |

## Code Conventions

- Python 3.11+ required
- Use `pathlib.Path` over `os.path`
- Use `click` for CLI, `rich` for output, `requests` for HTTP
- Type hints required on all public functions
- Line length: 100 characters
- Config: `pyproject.toml` (ruff, mypy settings)

## API Reference

- Search/categories/collections: `https://api.n8n.io/api/templates/search`
- Download workflow: `https://api.n8n.io/api/templates/workflows/{ID}`
