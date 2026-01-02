# Session Specification

**Session ID**: `phase00-session05-testing`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This session validates the Python migration by testing all three converted scripts (search.py, download.py, split.py) to ensure they have complete feature parity with their original Bash counterparts. Testing is critical at this stage because the entire Phase 00 migration depends on these scripts working correctly before we can proceed to documentation and phase completion.

The validation approach is manual and systematic rather than automated. We will execute each script's commands, verify outputs match expected behavior, test edge cases, and document any bugs discovered along the way. Any issues found will be fixed immediately before proceeding.

This session serves as the quality gate between implementation (sessions 02-04) and documentation (session 06). No documentation should be written until we have confidence that the scripts work correctly across all supported use cases.

---

## 2. Objectives

1. Verify search.py supports all search modes (--search, --info, --list-categories, --list-subcategories) with correct output formatting
2. Verify download.py correctly downloads workflows and creates proper file structure
3. Verify split.py correctly splits multi-workflow JSON files into individual workflow files
4. Fix any bugs or regressions discovered during testing

---

## 3. Prerequisites

### Required Sessions
- [x] `phase00-session01-project-setup` - Python environment and project structure
- [x] `phase00-session02-search-script` - search.py implementation
- [x] `phase00-session03-download-script` - download.py implementation
- [x] `phase00-session04-split-script` - split.py implementation

### Required Tools/Knowledge
- Python 3.11+ installed and configured
- Internet access for n8n API calls
- Understanding of CLI testing patterns

### Environment Requirements
- Linux environment (WSL or native)
- Virtual environment activated
- Required packages installed (click, requests, rich)

---

## 4. Scope

### In Scope (MVP)
- Manual testing of all CLI commands and options
- Edge case validation (empty results, special characters, large files)
- Bug fixes for any issues discovered
- Test results documentation in a simple format
- Verification of output formatting (tables, colors, JSON)

### Out of Scope (Deferred)
- Automated test suite with pytest - *Reason: Future enhancement, manual testing sufficient for migration validation*
- CI/CD integration - *Reason: No CI/CD pipeline exists yet*
- Windows compatibility testing - *Reason: Primary target is Linux/WSL*
- Performance benchmarking - *Reason: Not a current requirement*

---

## 5. Technical Approach

### Architecture
Testing follows a black-box approach, treating each script as a standalone CLI tool. We execute commands with various inputs and verify outputs match expected behavior. No mocking or stubbing - all tests use live API calls to ensure real-world validity.

### Design Patterns
- **Manual Verification**: Direct command execution with visual output inspection
- **Edge Case Coverage**: Systematic testing of boundary conditions
- **Fix-Forward**: Issues are fixed immediately, not tracked for later

### Technology Stack
- Python 3.11+
- click (CLI framework)
- requests (HTTP client)
- rich (terminal output)
- n8n Public API (live testing)

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| `.spec_system/specs/phase00-session05-testing/test_results.md` | Document test outcomes | ~100 |

### Files to Modify
| File | Changes | Est. Lines |
|------|---------|------------|
| `scripts/search.py` | Bug fixes if needed | ~20 |
| `scripts/download.py` | Bug fixes if needed | ~20 |
| `scripts/split.py` | Bug fixes if needed | ~20 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] search.py --search returns formatted results table
- [ ] search.py --info displays workflow details correctly
- [ ] search.py --list-categories shows all categories
- [ ] search.py --list-subcategories shows subcategories
- [ ] download.py downloads single workflow correctly
- [ ] download.py handles --all-nodes option
- [ ] split.py splits combined JSON into individual files
- [ ] split.py preserves workflow JSON structure
- [ ] All scripts handle empty/error responses gracefully

### Testing Requirements
- [ ] Each command tested with valid inputs
- [ ] Each command tested with edge cases
- [ ] Error handling verified
- [ ] Output formatting verified

### Quality Gates
- [ ] All files ASCII-encoded
- [ ] Unix LF line endings
- [ ] Code follows project conventions (ruff check passes)
- [ ] No unhandled exceptions during testing

---

## 8. Implementation Notes

### Key Considerations
- Test with real n8n API calls to validate actual behavior
- Document exact commands used for reproducibility
- Fix issues immediately rather than accumulating a bug list
- Verify rich table formatting renders correctly in terminal

### Potential Challenges
- **API Rate Limits**: n8n API may throttle requests - add delays between bulk tests if needed
- **Network Dependency**: Tests require live API - no offline fallback
- **Output Verification**: Visual inspection required for formatted output - no automated assertions

### Relevant Considerations
- **[P00] n8n Public API**: Rate limits unknown - space out API calls during testing to avoid throttling
- **[P00] Embedded Python for JSON**: Verify split.py maintains JSON parsing quality from original implementation

### ASCII Reminder
All output files must use ASCII-only characters (0-127).

---

## 9. Testing Strategy

### Unit Tests
- Not applicable for this session (manual testing approach)

### Integration Tests
- Script-to-API integration verified through live calls
- File system operations verified through actual file creation

### Manual Testing

**search.py tests:**
```bash
python scripts/search.py --search "gmail"
python scripts/search.py --search "nonexistent-workflow-xyz"
python scripts/search.py --info 1234
python scripts/search.py --list-categories
python scripts/search.py --list-subcategories
```

**download.py tests:**
```bash
python scripts/download.py --workflow 1234
python scripts/download.py --workflow 1234 --all-nodes
python scripts/download.py --workflow 99999999  # invalid ID
```

**split.py tests:**
```bash
python scripts/split.py input.json output_dir/
python scripts/split.py empty.json output_dir/  # empty array
```

### Edge Cases
- Empty search results (search for gibberish string)
- Invalid workflow IDs (download non-existent workflow)
- Workflow names with special characters (verify filename sanitization)
- Very long workflow names (verify truncation)
- Empty JSON array input to split.py
- Single workflow JSON input to split.py

---

## 10. Dependencies

### External Libraries
- click: 8.x
- requests: 2.x
- rich: 13.x

### Other Sessions
- **Depends on**: phase00-session01 through phase00-session04 (all scripts implemented)
- **Depended by**: phase00-session06-documentation (cannot document until testing confirms behavior)

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
