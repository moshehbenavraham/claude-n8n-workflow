# NEXT_SESSION.md

## Session Recommendation

**Generated**: 2026-01-02
**Project State**: Phase 00 - Python Migration
**Completed Sessions**: 1/6 (17%)

---

## Recommended Next Session

**Session ID**: `phase00-session02-search-script`
**Session Name**: Search Script Conversion
**Estimated Duration**: 3-4 hours
**Estimated Tasks**: 18-22

---

## Why This Session Next?

### Prerequisites Met
- [x] Python project structure created (session 01)
- [x] `requirements.txt` with dependencies (click, requests, rich)
- [x] Virtual environment setup documented
- [x] Directory structure: `scripts/` directory exists

### Dependencies
- **Builds on**: phase00-session01-project-setup (Python foundation)
- **Enables**: phase00-session03-download-script (download can use shared utilities)

### Project Progression
This is the natural next step because:
1. Search script is the largest (707 lines) and most complex - tackling it first de-risks the project
2. Establishes patterns for API interaction, CLI structure, and output formatting that will be reused
3. Independent of other scripts - no blocking dependencies
4. Highest value to users - search is the primary discovery mechanism

---

## Session Overview

### Objective
Convert `scripts/search-workflows.sh` (707 lines Bash) to `scripts/search.py` (~400 lines Python) with complete feature parity.

### Key Deliverables
1. `scripts/search.py` - Click-based CLI with 5 commands
2. Multiple output formats: table, json, ids, compact
3. All search filters: category, apps, nodes
4. Save results functionality
5. Rich terminal formatting with tables and colors

### Scope Summary
- **In Scope (MVP)**: All 5 commands (`search`, `categories`, `collections`, `collection`, `stats`), all output formats, filtering, pagination, save to file
- **Out of Scope**: New features, additional output formats, GUI, configuration files

---

## Technical Considerations

### Technologies/Patterns
- **click** - Multi-command CLI with `@click.group()` and `@click.command()`
- **requests** - HTTP client for n8n API calls
- **rich** - Tables, panels, and colored output
- **dataclasses** - Type-safe workflow/collection models

### Potential Challenges
1. **API Rate Limiting**: n8n API limits unknown - may need request throttling
2. **Output Parity**: Table formatting must match Bash version closely
3. **Error Handling**: Network failures, invalid JSON, API errors need graceful handling
4. **Pagination Math**: Skip/page calculations must match Bash behavior exactly

### Relevant Considerations
- [P00] **n8n Public API**: Rate limits unknown, implement conservative delays between bulk requests
- [P00] **rich vs colorama**: Use rich for table formatting - better than colorama for structured output
- [P00] **click vs argparse**: Use click decorators for cleaner command structure

---

## Alternative Sessions

If this session is blocked:
1. **phase00-session03-download-script** - Simpler (259 lines), could be done first if search is problematic
2. **phase00-session04-split-script** - Already has embedded Python, could be quick win

---

## Next Steps

Run `/sessionspec` to generate the formal specification.
