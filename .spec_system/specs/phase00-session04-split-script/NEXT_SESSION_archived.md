# NEXT_SESSION.md

## Session Recommendation

**Generated**: 2026-01-02
**Project State**: Phase 00 - Python Migration
**Completed Sessions**: 3

---

## Recommended Next Session

**Session ID**: `phase00-session04-split-script`
**Session Name**: Split Script - Convert split-workflows.sh to Python
**Estimated Duration**: 2-3 hours
**Estimated Tasks**: 15-18

---

## Why This Session Next?

### Prerequisites Met
- [x] Python project structure established (session-01)
- [x] Click CLI patterns established (session-02)
- [x] Rich terminal formatting patterns established (session-02, session-03)
- [x] JSON handling utilities in place

### Dependencies
- **Builds on**: session-03 (download-script) - users will download workflows, then split them
- **Enables**: session-05 (testing) - split script is the final core functionality needed before comprehensive testing

### Project Progression
This is the logical next step because:
1. It's the third and final script conversion (search -> download -> split)
2. The workflow is sequential: search workflows, download them, then split for analysis
3. Completes the core Python utility toolkit before integration testing

---

## Session Overview

### Objective
Convert `split-workflows.sh` (216 lines Bash + embedded Python) to a standalone Python CLI script using click and rich, maintaining identical output structure.

### Key Deliverables
1. `scripts/split.py` - Click-based CLI with options for directory and threshold
2. Intelligent JSON splitting logic (extracted from embedded Python)
3. Rich terminal output with progress tracking and summary tables
4. Identical output structure to existing Bash script

### Scope Summary
- **In Scope (MVP)**: CLI arguments, JSON splitting logic, node file splitting, progress output, summary display
- **Out of Scope**: Additional split strategies, compression, async processing, configuration files

---

## Technical Considerations

### Technologies/Patterns
- **click** - CLI framework (consistent with search.py and download.py)
- **rich** - Terminal formatting with progress bars and tables
- **pathlib** - Cross-platform path handling
- **json** - Native JSON processing (already used in embedded Python)

### Potential Challenges
- Preserving exact output structure for compatibility with existing Claude Code agents
- Handling edge cases in node name sanitization across platforms
- Large workflow files may need memory-efficient streaming (monitor during testing)

### Relevant Considerations
- [P00] **Embedded Python in Bash**: The existing script already contains ~150 lines of embedded Python - extract and enhance rather than rewrite from scratch
- [P00] **Avoid jq dependency**: Python's native JSON is cleaner, continue this pattern
- [P00] **rich vs colorama**: Use rich for progress display and summary tables

---

## Alternative Sessions

If this session is blocked:
1. **phase00-session05-testing** - Could start testing search.py and download.py while split.py is pending (not recommended - better to complete all scripts first)
2. **phase00-session06-documentation** - Could update docs for completed scripts (not recommended - documentation should cover all scripts together)

---

## Next Steps

Run `/sessionspec` to generate the formal specification.
