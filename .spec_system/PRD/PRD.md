# n8n-workflow-analyzer - Product Requirements Document

## Overview

Toolkit for analyzing n8n workflow templates using Claude Code agents. This project provides:
- Utility scripts to search, download, and split n8n workflow JSON files
- Claude Code agents for AI-powered workflow analysis
- Pattern extraction and consolidation capabilities

The Phase 00 focus is migrating Bash utility scripts to Python (hybrid approach) while keeping all Claude Code agents unchanged.

## Goals

1. Convert 3 Bash scripts (~1,181 lines) to Python (~750 lines)
2. Maintain feature parity with existing Bash implementations
3. Improve cross-platform compatibility (Windows support)
4. Better error handling and terminal output with modern Python libraries
5. Keep all Claude Code agents and skills unchanged

## Technical Stack

- **Python:** 3.11+
- **CLI Framework:** click>=8.1.0
- **HTTP Client:** requests>=2.31.0
- **Terminal Formatting:** rich>=13.0.0
- **AI Orchestration:** Claude Code (unchanged)

## Phases

| Phase | Name | Sessions | Status |
|-------|------|----------|--------|
| 00 | Python Migration | 6 | Not Started |

---

## Phase 00: Python Migration

### Objectives

1. Set up Python project structure with dependencies
2. Convert search-workflows.sh to search.py
3. Convert download-workflows.sh to download.py
4. Convert split-workflows.sh to split.py
5. Test all scripts for feature parity
6. Update documentation

### Scope

#### Scripts to Convert

| Script | Current | Target | Functionality |
|--------|---------|--------|---------------|
| `search-workflows.sh` | 707 lines Bash | ~400 lines Python | Query n8n API, multiple output formats, filters, pagination |
| `download-workflows.sh` | 259 lines Bash | ~150 lines Python | Download workflows by ID/URL, validate JSON, sanitize filenames |
| `split-workflows.sh` | 215 lines Bash | ~200 lines Python | Split large JSONs into organized chunks, intelligent thresholds |

#### What Stays Unchanged

```
.claude/
├── agents/
│   ├── metadata-analyzer.md
│   ├── flow-analyzer.md
│   ├── node-analyzer.md
│   ├── docs-extractor.md
│   ├── analysis-extractor.md
│   ├── pattern-aggregator.md
│   └── solution-architect.md
├── skills/
│   ├── n8n-workflow-analyzer/
│   └── analysis-consolidator/
└── settings.local.json
```

### Sessions

| Session | Name | Description | Deliverables |
|---------|------|-------------|--------------|
| 00-01 | Project Setup | Create Python project structure | `requirements.txt`, directory structure |
| 00-02 | Search Script | Convert search-workflows.sh | `scripts/search.py` with all commands |
| 00-03 | Download Script | Convert download-workflows.sh | `scripts/download.py` with ID extraction |
| 00-04 | Split Script | Convert split-workflows.sh | `scripts/split.py` with chunking logic |
| 00-05 | Testing | Test all scripts for feature parity | Test results, bug fixes |
| 00-06 | Documentation | Update README and usage docs | Updated `scripts/README.md` |

### Script Specifications

#### search.py

**Commands:**
- `search [QUERY]` - Search workflows with filters (category, apps, nodes)
- `categories` - List all available categories
- `collections` - List curated collections
- `collection <ID>` - Get workflows in a specific collection
- `stats` - Show API statistics

**Options:**
- `-c, --category` - Filter by category
- `-a, --apps` - Filter by apps (comma-separated)
- `-n, --nodes` - Filter by node types
- `-r, --rows` - Results per page (max 100)
- `-p, --page` - Page number
- `-o, --output` - Output format: table, json, ids, compact
- `--save` - Save results to search_results/

#### download.py

**Arguments:**
- `WORKFLOW_IDS` - One or more workflow IDs or URLs

**Options:**
- `-f, --file` - Read IDs from file
- `-o, --output` - Output directory (default: n8n-workflows)
- `-s, --split` - Run splitter after download

**Features:**
- Extract IDs from n8n.io URLs
- Validate JSON responses
- Sanitize filenames from workflow names
- Track success/failure counts

#### split.py

**Options:**
- `-d, --directory` - Directory containing workflow JSONs (default: n8n-workflows)
- `-t, --threshold` - Line threshold before splitting (default: 300)

**Output Structure:**
```
workflow-folder/
├── 01-metadata.json
├── 02-settings.json
├── 03-connections.json
├── 04-nodes.json (or nodes/ directory if large)
├── 05-template-nodes.json (if present)
└── 06-image.json (if present)
```

---

## Installation & Usage

### Setup

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r scripts/requirements.txt
```

### Usage Examples

```bash
# Search
python scripts/search.py search "real estate" --rows 20 --output table
python scripts/search.py search --category AI --save
python scripts/search.py categories
python scripts/search.py stats

# Download
python scripts/download.py 5428 6332 6162
python scripts/download.py --file workflow-ids.txt --split

# Split
python scripts/split.py --threshold 300
```

---

## Success Criteria

- [ ] All 3 Python scripts work identically to Bash versions
- [ ] Cross-platform compatibility (Linux, macOS, Windows)
- [ ] requirements.txt with pinned dependencies
- [ ] Updated documentation for Python usage
- [ ] All search commands functional (search, categories, collections, stats)
- [ ] Download handles IDs, URLs, and file input
- [ ] Split produces identical output structure
- [ ] Rich terminal formatting with colors and tables

## Reference Documents

- `archive/convert-to-python.md` - Detailed conversion plan with code examples
- `scripts/README_scripts.md` - Current Bash script documentation
