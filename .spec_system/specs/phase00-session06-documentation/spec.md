# Session Specification

**Session ID**: `phase00-session06-documentation`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This is the final session of Phase 00 (Python Migration). All three Python CLI scripts (search.py, download.py, split.py) have been implemented and tested for feature parity with the legacy Bash scripts. The project now needs comprehensive documentation that reflects the completed migration.

The current `scripts/README_scripts.md` provides excellent documentation for the legacy Bash scripts but only has basic Python setup information. The main `README.md` has been partially updated with Python examples but the scripts README needs a complete overhaul to document the new Python CLI tools as the primary interface.

This session will update all documentation to provide users with clear, comprehensive guides for using the Python CLI scripts, while handling the legacy Bash scripts appropriately (deprecation notices or documentation updates).

---

## 2. Objectives

1. Document all Python CLI commands with complete option tables, examples, and output descriptions
2. Update scripts/README_scripts.md to feature Python CLI as the primary interface
3. Ensure consistency between CLI help text and written documentation
4. Add deprecation notices for legacy Bash scripts and clean up outdated documentation

---

## 3. Prerequisites

### Required Sessions
- [x] `phase00-session01-project-setup` - Python project structure and dependencies
- [x] `phase00-session02-search-script` - search.py implementation
- [x] `phase00-session03-download-script` - download.py implementation
- [x] `phase00-session04-split-script` - split.py implementation
- [x] `phase00-session05-testing` - Feature parity testing

### Required Tools/Knowledge
- Markdown formatting and GitHub-flavored markdown
- Understanding of click CLI conventions
- Familiarity with n8n workflow template API

### Environment Requirements
- Access to Python venv with scripts installed
- Ability to run CLI commands to verify documentation accuracy

---

## 4. Scope

### In Scope (MVP)
- Complete Python CLI documentation in scripts/README_scripts.md
- Option tables for all three Python scripts (search.py, download.py, split.py)
- Usage examples matching actual CLI behavior
- Deprecation notices for legacy Bash scripts
- Consistent formatting across all README files

### Out of Scope (Deferred)
- API reference documentation - *Reason: Not needed for CLI users*
- Developer/contributor guide - *Reason: Future phase concern*
- Architecture documentation - *Reason: Future phase concern*
- Removal of legacy Bash scripts - *Reason: Keep for backwards compatibility*

---

## 5. Technical Approach

### Architecture
Documentation-only session with no code changes. The primary deliverable is updated markdown files that accurately reflect the Python CLI interface.

### Design Patterns
- **CLI-first documentation**: Options tables mirror actual --help output
- **Progressive disclosure**: Quick start examples first, then detailed options
- **Consistent structure**: Each script section follows same format

### Technology Stack
- Markdown (GitHub-flavored)
- Shell examples for CLI invocation

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| None | Documentation-only session | - |

### Files to Modify
| File | Changes | Est. Lines Changed |
|------|---------|-------------------|
| `scripts/README_scripts.md` | Complete rewrite for Python CLI primary, Bash legacy | ~250 |
| `README.md` | Minor refinements to Quick Start section | ~20 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] All Python CLI options documented with accurate descriptions
- [ ] Usage examples match actual CLI behavior (verified by running commands)
- [ ] Deprecation notices clearly mark Bash scripts as legacy
- [ ] Documentation is consistent with `--help` output for all scripts

### Testing Requirements
- [ ] Manual verification: Run each documented command to confirm accuracy
- [ ] Review: Cross-check option tables against CLI help text

### Quality Gates
- [ ] All files ASCII-encoded
- [ ] Unix LF line endings
- [ ] Markdown renders correctly (no broken links, proper table formatting)
- [ ] No orphaned or outdated command examples

---

## 8. Implementation Notes

### Key Considerations
- Python scripts use click-based CLI with subcommands (search.py has 5 subcommands)
- The search.py uses command groups (search, categories, collections, collection, stats)
- download.py and split.py are simpler single-command CLIs
- Legacy Bash scripts should be preserved but clearly marked as deprecated

### Potential Challenges
- **CLI help vs docs sync**: Mitigation - Run each command during documentation to verify
- **Bash deprecation wording**: Mitigation - Keep documentation but add clear deprecation notice

### Relevant Considerations
- [P00] **click vs argparse**: Document click-based subcommand patterns for search.py
- [P00] **rich vs colorama**: Note rich's table formatting capabilities in output descriptions
- [P00] **Embedded Python for JSON**: No longer relevant - split.py is now pure Python

### ASCII Reminder
All output files must use ASCII-only characters (0-127).

---

## 9. Testing Strategy

### Unit Tests
- N/A (documentation-only session)

### Integration Tests
- N/A (documentation-only session)

### Manual Testing
- Run each documented Python CLI command and verify output matches documentation
- Test example commands from README.md Quick Start section
- Verify all option flags work as documented

### Edge Cases
- Ensure verbose mode examples show expected additional output
- Verify --help output matches option tables

---

## 10. Dependencies

### External Libraries
- None (documentation only)

### Other Sessions
- **Depends on**: phase00-session01 through phase00-session05 (all complete)
- **Depended by**: None - this completes Phase 00

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
