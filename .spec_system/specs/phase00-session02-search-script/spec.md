# Session Specification

**Session ID**: `phase00-session02-search-script`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This session converts the largest and most complex utility script in the project: `scripts/search-workflows.sh` (707 lines of Bash) to `scripts/search.py` (estimated ~400 lines of Python). The search script is the primary discovery mechanism for users to find n8n workflow templates, making it the highest-value migration target.

The conversion establishes foundational patterns for API interaction, CLI structure using Click, and terminal output formatting with Rich that will be reused across all subsequent script migrations. By tackling the most complex script first, we de-risk the entire Python migration phase and validate our technical approach early.

This script provides 5 distinct commands (search, categories, collections, collection, stats), multiple output formats (table, json, ids, compact), comprehensive filtering (category, apps, nodes), pagination, and the ability to save results to files. Complete feature parity with the Bash version is required.

---

## 2. Objectives

1. Convert all 5 CLI commands from Bash to Python Click with identical functionality
2. Implement all 4 output formats (table, json, ids, compact) using Rich for terminal rendering
3. Preserve all filtering capabilities (category, apps, nodes) and pagination logic
4. Establish reusable patterns for API requests, error handling, and CLI structure

---

## 3. Prerequisites

### Required Sessions
- [x] `phase00-session01-project-setup` - Python project structure, requirements.txt, virtual environment

### Required Tools/Knowledge
- Python 3.11+ with virtual environment
- Understanding of Click CLI framework decorators
- Understanding of Rich library for terminal output
- Familiarity with n8n public API (documented in docs/n8n-public-API.md)

### Environment Requirements
- Virtual environment activated with dependencies installed (`pip install -r requirements.txt`)
- Network access to api.n8n.io for API testing
- Terminal with color support for Rich output testing

---

## 4. Scope

### In Scope (MVP)
- `search` command with query, filtering (category/apps/nodes), pagination (rows/page/skip)
- `categories` command listing all n8n workflow categories
- `collections` command listing all curated collections
- `collection <id>` command showing specific collection details
- `stats` command displaying API statistics
- All output formats: table (default), json, ids, compact
- `--save` flag to write results to JSON files
- `--verbose` flag for debugging API calls
- `--help` for all commands
- Identical CLI argument names and behavior to Bash version

### Out of Scope (Deferred)
- New features beyond Bash version - *Reason: migration must maintain parity first*
- Configuration file support - *Reason: not in original, adds complexity*
- GUI or web interface - *Reason: CLI tool only*
- Caching layer - *Reason: API already cached by Cloudflare*
- Rate limiting implementation - *Reason: will add if needed based on API behavior*

---

## 5. Technical Approach

### Architecture
Single-file Python script with Click command group. The script will be organized as:
1. Imports and constants (API URLs, default values)
2. Data classes for type-safe API response models (Workflow, Category, Collection)
3. API client functions (request handling, error handling)
4. Output formatters (table, json, ids, compact using Rich)
5. Click commands with decorators for each subcommand
6. Main entry point

### Design Patterns
- **Command Pattern**: Click's `@click.group()` and `@click.command()` for CLI structure
- **Data Classes**: Type-safe models for API responses using `@dataclass`
- **Strategy Pattern**: Output formatters selected by format flag
- **Single Responsibility**: Separate functions for API calls, formatting, file I/O

### Technology Stack
- Python 3.11+
- click 8.x - CLI framework with decorators
- requests 2.x - HTTP client for API calls
- rich 13.x - Terminal tables, panels, colored output

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| `scripts/search.py` | Main CLI script with all commands | ~400 |

### Files to Modify
| File | Changes | Est. Lines |
|------|---------|------------|
| `README.md` | Add usage examples for new Python script | ~20 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] `python scripts/search.py search "real estate"` returns same workflows as Bash
- [ ] `python scripts/search.py categories` lists all categories with icons
- [ ] `python scripts/search.py collections` lists all collections with workflow counts
- [ ] `python scripts/search.py collection 8` shows collection details
- [ ] `python scripts/search.py stats` shows total workflows, categories, collections
- [ ] All output formats produce identical data (table layout may differ slightly)
- [ ] `--ids` output can be piped to other scripts
- [ ] `--save` creates valid JSON files in search_results/ directory
- [ ] Pagination with `--rows`, `--page`, `--skip` matches Bash behavior exactly
- [ ] Filter combinations (--category + --apps + query) work correctly

### Testing Requirements
- [ ] Manual testing of all 5 commands with various inputs
- [ ] Manual testing of all 4 output formats
- [ ] Manual testing of filter combinations
- [ ] Manual testing of pagination edge cases
- [ ] Manual testing of error scenarios (network failure, invalid inputs)

### Quality Gates
- [ ] All files ASCII-encoded (no Unicode in source)
- [ ] Unix LF line endings
- [ ] Code follows project conventions (snake_case, type hints)
- [ ] `ruff check scripts/search.py` passes with no errors
- [ ] `ruff format scripts/search.py` produces no changes
- [ ] Script is executable (`chmod +x`) with proper shebang

---

## 8. Implementation Notes

### Key Considerations
- Click uses decorators - command structure must be defined before CLI group
- Rich tables need explicit column definitions for alignment
- API returns nested JSON - use `.get()` with defaults to avoid KeyError
- Pagination: page number starts at 1, skip = (page - 1) * rows

### Potential Challenges
- **Table Formatting**: Rich tables may not match Bash printf exactly - focus on data correctness over pixel-perfect layout
- **Error Messages**: Ensure error output goes to stderr, matches user-friendly Bash messages
- **Unicode in API Data**: Workflow names/descriptions may contain Unicode - handle gracefully in table display
- **Empty Results**: Handle zero-result searches without crashing

### Relevant Considerations
- [P00] **n8n Public API**: Rate limits unknown - implement no throttling initially, add if 429 errors occur
- [P00] **rich vs colorama**: Using Rich for all output - provides tables, panels, and colors in one library
- [P00] **click vs argparse**: Using Click decorators for cleaner multi-command CLI structure
- [P00] **Avoid jq dependency**: Python's native json module replaces all jq functionality

### ASCII Reminder
All output files must use ASCII-only characters (0-127). Source code comments and strings should avoid Unicode.

---

## 9. Testing Strategy

### Unit Tests
- Not required for MVP (manual testing sufficient for script migration)
- Future: Test API response parsing with mock data

### Integration Tests
- Not required for MVP
- Future: Test full command execution with recorded API responses

### Manual Testing
- Run each command and compare output to Bash version
- Test with real API calls to api.n8n.io
- Test error handling by disconnecting network
- Test pagination by verifying result counts and skip values

### Edge Cases
- Empty search results (query with no matches)
- Very long workflow names (truncation in table display)
- Special characters in search query (URL encoding)
- Invalid collection ID (API error handling)
- Network timeout (graceful error message)
- Invalid filter values (e.g., non-existent category)

---

## 10. Dependencies

### External Libraries
- click: 8.1.7 (already in requirements.txt)
- requests: 2.31.0 (already in requirements.txt)
- rich: 13.7.0 (already in requirements.txt)

### Other Sessions
- **Depends on**: phase00-session01-project-setup (Python environment)
- **Depended by**: phase00-session03-download-script (may share API utilities), phase00-session05-unified-cli (will import search commands)

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
