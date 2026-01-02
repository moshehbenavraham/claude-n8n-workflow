# Session Specification

**Session ID**: `phase00-session03-download-script`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This session converts the `download-workflows.sh` Bash script (259 lines) to `scripts/download.py` (estimated ~150 lines Python), completing the third step of the Python migration phase. The download script is a core utility that fetches n8n workflow JSON files from the public template API.

The conversion follows patterns established in session02 (search script) including click-based CLI, rich terminal output, and requests-based HTTP handling. This ensures consistency across the toolkit while providing a cleaner, more maintainable Python implementation.

Completing this session enables the split script (session04) to be integrated via the `--split` flag, maintaining the workflow where users can download and immediately split a workflow for analysis.

---

## 2. Objectives

1. Convert download-workflows.sh to scripts/download.py with full feature parity
2. Implement ID extraction from multiple URL patterns (n8n.io and api.n8n.io)
3. Support batch downloads from file input
4. Integrate with split script via --split flag (subprocess call)

---

## 3. Prerequisites

### Required Sessions
- [x] `phase00-session01-project-setup` - Python project structure, pyproject.toml, dependencies
- [x] `phase00-session02-search-script` - API patterns, error handling, rich output conventions

### Required Tools/Knowledge
- Python 3.11+
- click CLI library
- requests HTTP library
- rich terminal library
- Regex for URL parsing

### Environment Requirements
- Network access to api.n8n.io
- Write access to n8n-workflows/ directory

---

## 4. Scope

### In Scope (MVP)
- Download single workflow by numeric ID
- Download single workflow by URL (extract ID from n8n.io and api.n8n.io patterns)
- Download multiple workflows from command line arguments
- Batch download from file (one ID/URL per line, skip comments/blanks)
- JSON validation of downloaded responses
- Sanitized filename generation from workflow name
- Rich progress output with success/failure status
- `--split` flag to invoke split-workflows.sh after download
- `--output` directory option
- `--verbose` flag for debug output

### Out of Scope (Deferred)
- Async/parallel downloads - *Reason: Keep simple, may add in session05 for performance*
- Retry logic on failures - *Reason: Defer to session05*
- Rate limiting/throttling - *Reason: API limits unknown, test in session05*
- Progress bars for large batches - *Reason: Sequential downloads are fast enough*

---

## 5. Technical Approach

### Architecture
Single-file CLI script following the same structure as search.py:
- Global configuration constants
- Rich console for output
- Dataclass for workflow representation (optional, may just use dict)
- Helper functions for ID extraction and filename sanitization
- click command with options/arguments
- Main entry point

### Design Patterns
- **Decorator-based CLI**: click decorators for clean argument parsing
- **Fail-fast validation**: Validate URL patterns before making API requests
- **Temp file download**: Download to temp file, validate JSON, then move to final location

### Technology Stack
- Python 3.11+
- click 8.x for CLI
- requests 2.x for HTTP
- rich for terminal output
- re (stdlib) for regex URL parsing
- pathlib (stdlib) for file paths
- tempfile (stdlib) for safe downloads
- subprocess (stdlib) for --split integration

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| `scripts/download.py` | Main CLI script for downloading workflows | ~150 |

### Files to Modify
| File | Changes | Est. Lines |
|------|---------|------------|
| None | No modifications to existing files | 0 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] `python scripts/download.py 5428` downloads workflow by ID
- [ ] `python scripts/download.py "https://n8n.io/workflows/5428-name/"` extracts ID from URL
- [ ] `python scripts/download.py "https://api.n8n.io/api/templates/workflows/5428"` extracts ID from API URL
- [ ] `python scripts/download.py 5428 6332 6162` downloads multiple workflows
- [ ] `python scripts/download.py --file workflows.txt` reads IDs/URLs from file
- [ ] Comments and blank lines in input file are skipped
- [ ] Invalid inputs are skipped with warning (not fatal)
- [ ] Downloaded JSON is validated before saving
- [ ] Filename includes workflow name when available (sanitized)
- [ ] `--split` flag invokes split-workflows.sh after successful downloads
- [ ] `--output DIR` changes output directory
- [ ] `--verbose` shows API URLs and extra details
- [ ] Exit code 0 if all downloads succeed, 1 if any fail

### Testing Requirements
- [ ] Manual test: download by numeric ID
- [ ] Manual test: download by n8n.io URL
- [ ] Manual test: download by api.n8n.io URL
- [ ] Manual test: batch download from file
- [ ] Manual test: invalid ID returns error
- [ ] Manual test: --split flag works

### Quality Gates
- [ ] All files ASCII-encoded (0-127)
- [ ] Unix LF line endings
- [ ] Code follows project conventions (CONVENTIONS.md)
- [ ] ruff format passes
- [ ] ruff check passes (no lint errors)
- [ ] Type hints on public functions
- [ ] No external dependencies beyond existing requirements.txt

---

## 8. Implementation Notes

### Key Considerations
- Follow search.py patterns for consistency (console setup, api_request style, verbose flag)
- Use pathlib.Path over os.path per CONVENTIONS.md
- Use sys.exit(1) for CLI failures per CONVENTIONS.md
- Keep functions small and focused per CONVENTIONS.md

### Potential Challenges
- **URL Pattern Variations**: Handle both n8n.io/workflows/ID and api.n8n.io patterns; use regex with multiple patterns
- **Filename Sanitization**: Special characters in workflow names need safe conversion to filesystem-friendly strings
- **Subprocess Integration**: --split flag needs to find and invoke split-workflows.sh correctly

### Relevant Considerations
- [P00] **n8n Public API rate limits**: May need throttling for bulk downloads - keep simple for now, monitor in testing
- [P00] **rich vs colorama**: Continue using rich for consistency with search.py (proven pattern)
- [P00] **click vs argparse**: Continue with click for consistency (proven pattern)
- [P00] **Avoid jq dependency**: Use Python's native JSON parsing, no shell to jq

### ASCII Reminder
All output files must use ASCII-only characters (0-127).

---

## 9. Testing Strategy

### Unit Tests
- Not required for this session (manual testing sufficient for CLI script)

### Integration Tests
- Not required for this session

### Manual Testing
1. Download single workflow by ID: `python scripts/download.py 5428`
2. Download by n8n.io URL: `python scripts/download.py "https://n8n.io/workflows/5428-test/"`
3. Download by API URL: `python scripts/download.py "https://api.n8n.io/api/templates/workflows/5428"`
4. Download multiple: `python scripts/download.py 5428 6332`
5. Batch from file: Create test file with IDs/URLs/comments, run `--file`
6. Invalid ID handling: `python scripts/download.py 99999999`
7. Split integration: `python scripts/download.py --split 5428`
8. Output directory: `python scripts/download.py -o /tmp/test 5428`
9. Verbose mode: `python scripts/download.py -v 5428`

### Edge Cases
- Empty input file
- File with only comments
- Malformed URLs (should skip with warning)
- Non-numeric ID strings (should skip with warning)
- Network timeout (should report error and continue)
- Invalid JSON response (should report error and continue)

---

## 10. Dependencies

### External Libraries
- click: 8.x (existing in requirements.txt)
- requests: 2.x (existing in requirements.txt)
- rich: existing in requirements.txt

### Other Sessions
- **Depends on**: `phase00-session01-project-setup`, `phase00-session02-search-script`
- **Depended by**: `phase00-session04-split-script` (--split flag integration)

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
