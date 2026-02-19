# n8n Workflow Analyzer

Claude Code toolkit for finding, downloading, analyzing and consolidating n8n workflow templates.

## Quick Start

### Python CLI (recommended)

```bash
# Setup (one-time)
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

# Search n8n templates
python scripts/search.py search "real estate"

# List available categories
python scripts/search.py categories

# List curated collections
python scripts/search.py collections

# Get collection details
python scripts/search.py collection 8

# Show API statistics
python scripts/search.py stats

# Advanced search with filters and pagination
python scripts/search.py search "chatbot" --category AI --rows 20 --page 2

# Output formats: table (default), json, ids, compact
python scripts/search.py search "automation" --json
python scripts/search.py search "automation" --ids --save

# Download workflows
python scripts/download.py 5428                              # Single ID
python scripts/download.py 5428 6332 6162                    # Multiple IDs
python scripts/download.py "https://n8n.io/workflows/5428"   # From n8n.io URL
python scripts/download.py --file workflow-ids.txt           # Batch from file
python scripts/download.py --split 5428                      # Download and split

# Crawl & download ALL workflows (with checkpoint/resume)
python scripts/crawl.py                    # Resume or start full crawl
python scripts/crawl.py --rediscover       # Re-check API for new workflows
python scripts/crawl.py --dry-run          # Show plan without downloading
python scripts/crawl.py --fresh            # Start over, ignore checkpoint
python scripts/crawl.py --max-downloads 50 # Limit count (for testing)

# Split existing workflow files
python scripts/split.py
```

### Bash Scripts (legacy)

```bash
# Search n8n templates
./scripts/search-workflows.sh "search query"

# Download a workflow from n8n templates
./scripts/download-workflows.sh <workflow-id>

# Split into analyzable chunks
./scripts/split-workflows.sh
```

### Analysis Workflow

```bash
# Analyze (triggers n8n-workflow-analyzer skill)
# "Analyze the workflow in n8n-workflows/<folder-name>/"

# Consolidate multiple analyses (triggers analysis-consolidator skill)
# "Consolidate the analysis documents into a unified solution"
```

## Project Structure

| Folder | Description | Details |
|--------|-------------|---------|
| `n8n-workflows/` | Downloaded workflows awaiting analysis | [README](n8n-workflows/README_n8n-workflows.md) |
| `search_results/` | Saved search results from template API | [README](search_results/README_search-results.md) |
| `analysis/` | Generated workflow analysis reports | [README](analysis/README_analysis.md) |
| `archive/` | Processed workflow folders | [README](archive/README_archive.md) |
| `docs/` | Consolidated solutions and documentation | [README](docs/README_docs.md) |
| `scripts/` | Download, split, and search utilities | [README](scripts/README_scripts.md) |
| `logs/` | Processing logs | [README](logs/README_logs.md) |
| `.claude/` | Custom agents, skills, and settings | [README](.claude/README_p_claude.md) |

## Key Components

**Skills:**
- `n8n-workflow-analyzer` - Parallel analysis of split workflow folders
- `analysis-consolidator` - Batch consolidation into unified architecture

**Agents:** 7 specialized sub-agents (metadata, flow, node, docs analyzers + extraction/aggregation pipeline)

## Output

- Individual analyses: `analysis/workflow-analysis-{name}.md`
- Consolidated solution: `docs/consolidated-solution.md`

**Samples:**

| Stage | Sample |
|-------|--------|
| Search results | [search_results/sample-search-results.json](search_results/sample-search-results.json) |
| Downloaded workflow | [n8n-workflows/sample-workflow-4281.json](n8n-workflows/sample-workflow-4281.json) |
| Split workflow | [n8n-workflows/sample-workflow-4281/](n8n-workflows/sample-workflow-4281/) |
| Single analysis | [analysis/sample-analysis_real-estate.md](analysis/sample-analysis_real-estate.md) |
| Consolidated solution | [docs/sample-consolidation_real-estate.md](docs/sample-consolidation_real-estate.md) |
