# Session Specification

**Session ID**: `phase00-session04-split-script`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This session converts `split-workflows.sh` (216 lines Bash with ~150 lines embedded Python) to `scripts/split.py` (estimated ~200 lines Python), completing the fourth step of the Python migration phase. The split script is the final core utility that intelligently splits large n8n workflow JSON files into organized, manageable chunks for analysis by Claude Code agents.

The conversion extracts and enhances the existing embedded Python logic, which already handles JSON parsing, node extraction, and file organization. By converting to a standalone Python CLI, we gain consistent command-line patterns (click), improved terminal output (rich progress bars and tables), and better cross-platform compatibility.

This session completes the core toolkit conversion (search -> download -> split). Users will download workflows with `download.py`, then split them with `split.py` to create manageable chunks for the Claude Code analysis agents. The split output structure must remain identical to the existing script to maintain compatibility with the downstream agents.

---

## 2. Objectives

1. Convert split-workflows.sh to scripts/split.py with full feature parity
2. Extract and enhance the embedded Python splitting logic
3. Implement rich terminal output with progress tracking and summary tables
4. Maintain identical output structure for agent compatibility

---

## 3. Prerequisites

### Required Sessions
- [x] `phase00-session01-project-setup` - Python project structure, pyproject.toml, dependencies
- [x] `phase00-session02-search-script` - Click CLI patterns, rich output conventions
- [x] `phase00-session03-download-script` - JSON handling patterns, error handling conventions

### Required Tools/Knowledge
- Python 3.11+
- click CLI library
- rich terminal library (progress, tables)
- pathlib for cross-platform path handling
- json (stdlib) for JSON processing

### Environment Requirements
- Read access to n8n-workflows/ directory (or specified input directory)
- Write access to create output folders for split workflows

---

## 4. Scope

### In Scope (MVP)
- Split all JSON workflow files in a directory
- Split a single specified workflow file
- Configurable line threshold for splitting (default: 300)
- Configurable input and output directories
- Intelligent JSON splitting: metadata, settings, connections, nodes
- Node-level file splitting when nodes exceed threshold
- Sanitized filenames for cross-platform compatibility
- Rich progress bar during processing
- Rich summary table showing results
- Success/failure tracking with appropriate exit codes
- Verbose mode for debug output

### Out of Scope (Deferred)
- Alternative split strategies - *Reason: Current strategy proven, defer to future enhancement*
- Output compression - *Reason: JSON files are text, defer to future*
- Async/parallel processing - *Reason: Keep simple, disk I/O is fast*
- Configuration file support - *Reason: CLI flags sufficient for current use*
- Streaming for memory efficiency - *Reason: Monitor in testing first, workflows rarely exceed 10MB*

---

## 5. Technical Approach

### Architecture
Single-file CLI script following established patterns from search.py and download.py:
- Global configuration constants (DEFAULT_THRESHOLD, DEFAULT_DIR)
- Rich console for output
- Helper functions for JSON operations, filename sanitization, line counting
- Core splitting logic extracted from embedded Python (enhanced)
- click command with options/arguments
- Main entry point with progress tracking

### Design Patterns
- **Decorator-based CLI**: click decorators for clean argument parsing
- **Extract and Enhance**: Lift existing embedded Python, add rich integration
- **Fail-graceful Processing**: Continue processing remaining files on individual failures
- **Consistent Output**: Preserve exact output structure for agent compatibility

### Technology Stack
- Python 3.11+
- click 8.x for CLI
- rich for terminal output (Progress, Table, Console)
- pathlib (stdlib) for file paths
- json (stdlib) for JSON processing

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| `scripts/split.py` | Main CLI script for splitting workflows | ~200 |

### Files to Modify
| File | Changes | Est. Lines |
|------|---------|------------|
| None | No modifications to existing files | 0 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] `python scripts/split.py` processes all JSON files in default n8n-workflows/ directory
- [ ] `python scripts/split.py workflow.json` processes a single specified file
- [ ] `python scripts/split.py --threshold 500` uses custom line threshold
- [ ] `python scripts/split.py --input-dir /path/to/dir` processes custom input directory
- [ ] `python scripts/split.py --output-dir /path/to/output` writes to custom output directory
- [ ] Small workflows (under threshold) kept intact as workflow.json
- [ ] Large workflows split into: 01-metadata.json, 02-settings.json, 03-connections.json, 04-nodes.json
- [ ] Very large node arrays split into individual files in nodes/ subdirectory with _index.json
- [ ] 05-template-nodes.json created when outer nodes differ from inner nodes
- [ ] 06-image.json created when image URL present
- [ ] Filenames sanitized (no /:*?"<>| characters)
- [ ] Rich progress bar shows processing status
- [ ] Rich summary table shows processed workflows and file counts
- [ ] Exit code 0 if all succeed, 1 if any failures
- [ ] `--verbose` shows detailed processing info

### Testing Requirements
- [ ] Manual test: default directory processing
- [ ] Manual test: single file processing
- [ ] Manual test: custom threshold
- [ ] Manual test: small workflow kept intact
- [ ] Manual test: large workflow split correctly
- [ ] Manual test: node files split when threshold exceeded
- [ ] Manual test: invalid JSON handled gracefully

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
- Extract embedded Python from split-workflows.sh as the foundation
- Follow search.py and download.py patterns for CLI structure
- Use pathlib.Path over os.path per CONVENTIONS.md
- Use sys.exit(1) for CLI failures per CONVENTIONS.md
- Keep functions small and focused per CONVENTIONS.md
- Preserve exact output structure for agent compatibility

### Potential Challenges
- **Output Compatibility**: Ensure split files exactly match existing script output structure
- **Node Name Sanitization**: Edge cases with special characters in node names
- **Large Workflows**: Memory usage with very large workflows (monitor, add streaming if needed)

### Relevant Considerations
- [P00] **Embedded Python in Bash**: Extract the ~150 lines of embedded Python and enhance with click/rich integration
- [P00] **Avoid jq dependency**: Python's native JSON is cleaner - continue this established pattern
- [P00] **rich vs colorama**: Use rich for progress bars and summary tables (proven pattern from session02/03)
- [P00] **Sanitized filenames**: Existing approach to sanitizing workflow names is robust - preserve the logic

### ASCII Reminder
All output files must use ASCII-only characters (0-127).

---

## 9. Testing Strategy

### Unit Tests
- Not required for this session (manual testing sufficient for CLI script)

### Integration Tests
- Not required for this session

### Manual Testing
1. Default processing: `python scripts/split.py` (with test workflows in n8n-workflows/)
2. Single file: `python scripts/split.py n8n-workflows/test.json`
3. Custom threshold: `python scripts/split.py --threshold 500`
4. Custom input dir: `python scripts/split.py --input-dir /tmp/workflows`
5. Custom output dir: `python scripts/split.py --output-dir /tmp/split-output`
6. Verbose mode: `python scripts/split.py --verbose`
7. Help output: `python scripts/split.py --help`

### Edge Cases
- Empty input directory (should report, exit cleanly)
- No JSON files in directory (should report, exit cleanly)
- Invalid JSON file (should skip with warning, continue)
- Very small workflow (should keep intact)
- Very large workflow with many nodes (should split nodes into individual files)
- Workflow names with special characters (should sanitize)
- Read-only output directory (should fail gracefully)

---

## 10. Dependencies

### External Libraries
- click: 8.x (existing in requirements.txt)
- rich: existing in requirements.txt

### Other Sessions
- **Depends on**: `phase00-session01-project-setup`, `phase00-session02-search-script`, `phase00-session03-download-script`
- **Depended by**: `phase00-session05-testing` (comprehensive testing), `phase00-session06-documentation`

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
