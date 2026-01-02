# NEXT_SESSION.md

## Session Recommendation

**Generated**: 2026-01-02
**Project State**: Phase 00 - Python Migration
**Completed Sessions**: 2

---

## Recommended Next Session

**Session ID**: `phase00-session03-download-script`
**Session Name**: Download Script
**Estimated Duration**: 2-3 hours
**Estimated Tasks**: 15-20

---

## Why This Session Next?

### Prerequisites Met
- [x] Python project structure exists (session01)
- [x] Search script converted with API patterns established (session02)
- [x] `click` and `rich` libraries already integrated
- [x] Shared utilities available (`scripts/__init__.py`)

### Dependencies
- **Builds on**: `phase00-session02-search-script` - API patterns, error handling, rich output
- **Enables**: `phase00-session04-split-script` (uses --split flag integration)

### Project Progression
This is the natural next step following the sequential script conversion approach. The download script is simpler than search (259 lines Bash vs 707 lines), making it an ideal intermediate step before the split script. The session02 work established patterns for API calls, error handling, and rich terminal output that can be directly reused.

---

## Session Overview

### Objective
Convert `download-workflows.sh` (259 lines Bash) to `scripts/download.py` (~150 lines Python) with full feature parity.

### Key Deliverables
1. `scripts/download.py` - Complete CLI for downloading workflows
2. ID extraction from URLs (n8n.io/workflows/ID and api.n8n.io patterns)
3. File input support for batch downloads
4. JSON validation and sanitized filename generation
5. Integration with split script via --split flag

### Scope Summary
- **In Scope (MVP)**: Download by ID, download by URL, batch from file, JSON validation, rich progress output, --split flag
- **Out of Scope**: Async/parallel downloads, retry logic, rate limiting (defer to session05)

---

## Technical Considerations

### Technologies/Patterns
- `click` decorators for CLI (established in session02)
- `requests` for HTTP downloads (already used in session02)
- `rich` for progress bars and status output
- Regex for URL ID extraction

### Potential Challenges
- URL pattern variations (handle both n8n.io and api.n8n.io patterns)
- Filename sanitization from workflow names with special characters
- Subprocess integration for --split flag

### Relevant Considerations
- [P00] **n8n Public API rate limits**: May need throttling for bulk downloads - keep simple for now, test in session05
- [P00] **rich vs colorama**: Use rich for progress bars and status (proven in session02)
- [P00] **click vs argparse**: Continue with click for consistency

---

## Alternative Sessions

If this session is blocked:
1. **phase00-session04-split-script** - Can be done in parallel if download features aren't needed yet
2. **phase00-session06-documentation** - Low-dependency, can start early

---

## Next Steps

Run `/sessionspec` to generate the formal specification.
