# Task Checklist

**Session ID**: `phase00-session05-testing`
**Total Tasks**: 18
**Estimated Duration**: 6-8 hours
**Created**: 2026-01-02

---

## Legend

- `[x]` = Completed
- `[ ]` = Pending
- `[P]` = Parallelizable (can run with other [P] tasks)
- `[S0005]` = Session reference (Phase 00, Session 05)
- `TNNN` = Task ID

---

## Progress Summary

| Category | Total | Done | Remaining |
|----------|-------|------|-----------|
| Setup | 3 | 3 | 0 |
| Foundation | 2 | 2 | 0 |
| Testing | 10 | 10 | 0 |
| Validation | 3 | 3 | 0 |
| **Total** | **18** | **18** | **0** |

---

## Setup (3 tasks)

Initial configuration and environment preparation.

- [x] T001 [S0005] Verify Python environment and dependencies installed (`scripts/`)
- [x] T002 [S0005] Verify all three scripts exist and are executable (`scripts/search.py`, `scripts/download.py`, `scripts/split.py`)
- [x] T003 [S0005] Create test_results.md template file (`.spec_system/specs/phase00-session05-testing/test_results.md`)

---

## Foundation (2 tasks)

Review scripts and prepare test data.

- [x] T004 [S0005] Review search.py CLI interface and expected behavior (`scripts/search.py`)
- [x] T005 [S0005] Review download.py and split.py CLI interfaces (`scripts/download.py`, `scripts/split.py`)

---

## Testing (10 tasks)

Manual testing of all CLI commands and edge cases.

### search.py Testing

- [x] T006 [S0005] Test search.py search with valid query ("gmail") (`scripts/search.py`)
- [x] T007 [S0005] Test search.py search with empty results ("nonexistent-workflow-xyz") (`scripts/search.py`)
- [x] T008 [S0005] [P] Test search.py categories command (`scripts/search.py`)
- [x] T009 [S0005] [P] Test search.py collections command (`scripts/search.py`)
- [x] T010 [S0005] [P] Test search.py stats and collection commands (`scripts/search.py`)

### download.py Testing

- [x] T011 [S0005] Test download.py with valid ID (`scripts/download.py`)
- [x] T012 [S0005] Test download.py with --split option (Bug fixed: updated to use split.py) (`scripts/download.py`)
- [x] T013 [S0005] Test download.py with invalid workflow ID (error handling) (`scripts/download.py`)

### split.py Testing

- [x] T014 [S0005] Test split.py with workflow JSON file (`scripts/split.py`)
- [x] T015 [S0005] Test split.py edge cases (empty, minimal, invalid JSON) (`scripts/split.py`)

---

## Validation (3 tasks)

Final verification and quality assurance.

- [x] T016 [S0005] Run ruff check on all modified files (`scripts/`)
- [x] T017 [S0005] Validate ASCII encoding and LF line endings on all files (`scripts/`, `.spec_system/`)
- [x] T018 [S0005] Document all test results and finalize test_results.md (`.spec_system/specs/phase00-session05-testing/test_results.md`)

---

## Completion Checklist

Before marking session complete:

- [x] All tasks marked `[x]`
- [x] All tests passing
- [x] All files ASCII-encoded
- [x] implementation-notes.md updated
- [x] Ready for `/validate`

---

## Notes

### Parallelization
Tasks T008, T009, T010 can be run in parallel (independent search.py subcommands).

### Task Timing
Target ~20-25 minutes per task.

### Dependencies
- T001-T003 must complete before testing begins
- T004-T005 must complete before respective script testing
- T016-T018 run after all testing complete

### Bug Fix Protocol
If any test fails:
1. Document the failure in test_results.md
2. Fix the bug immediately in the relevant script
3. Re-run the test to verify the fix
4. Continue with remaining tests

### API Considerations
- Space out API calls to avoid rate limiting
- Tests require internet connectivity
- Use real n8n API endpoints for authentic validation

---

## Next Steps

Run `/implement` to begin AI-led implementation.
