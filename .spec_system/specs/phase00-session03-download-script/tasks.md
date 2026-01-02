# Task Checklist

**Session ID**: `phase00-session03-download-script`
**Total Tasks**: 20
**Estimated Duration**: 6-8 hours
**Created**: 2026-01-02

---

## Legend

- `[x]` = Completed
- `[ ]` = Pending
- `[P]` = Parallelizable (can run with other [P] tasks)
- `[S0003]` = Session reference (Phase 00, Session 03)
- `TNNN` = Task ID

---

## Progress Summary

| Category | Total | Done | Remaining |
|----------|-------|------|-----------|
| Setup | 2 | 2 | 0 |
| Foundation | 5 | 5 | 0 |
| Implementation | 9 | 9 | 0 |
| Testing | 4 | 4 | 0 |
| **Total** | **20** | **20** | **0** |

---

## Setup (2 tasks)

Initial configuration and environment preparation.

- [x] T001 [S0003] Verify prerequisites met - Python 3.11+, dependencies in requirements.txt, network access
- [x] T002 [S0003] Review search.py patterns for consistency - console setup, api_request style, verbose handling

---

## Foundation (5 tasks)

Core structures and base implementations.

- [x] T003 [S0003] Create download.py with module docstring, imports, and configuration constants (`scripts/download.py`)
- [x] T004 [S0003] Define URL pattern regex constants for n8n.io and api.n8n.io extraction (`scripts/download.py`)
- [x] T005 [S0003] Implement extract_workflow_id() function with multi-pattern support (`scripts/download.py`)
- [x] T006 [S0003] Implement sanitize_filename() function for workflow names (`scripts/download.py`)
- [x] T007 [S0003] Implement api_download() function with error handling following search.py pattern (`scripts/download.py`)

---

## Implementation (9 tasks)

Main feature implementation.

- [x] T008 [S0003] Implement download_workflow() function - fetch, validate JSON, save to file (`scripts/download.py`)
- [x] T009 [S0003] Implement temp file download pattern - write to temp, validate, move to final (`scripts/download.py`)
- [x] T010 [S0003] Create click CLI structure with @click.command and global options (`scripts/download.py`)
- [x] T011 [S0003] Add --output/-o directory option with default to n8n-workflows/ (`scripts/download.py`)
- [x] T012 [S0003] Add --file/-f option for batch input from file (`scripts/download.py`)
- [x] T013 [S0003] Implement read_ids_from_file() - parse file, skip comments/blanks (`scripts/download.py`)
- [x] T014 [S0003] Add --split flag with subprocess call to split-workflows.sh (`scripts/download.py`)
- [x] T015 [S0003] Add --verbose/-v flag with debug output for API URLs (`scripts/download.py`)
- [x] T016 [S0003] Implement main download loop with success/failure tracking and exit code (`scripts/download.py`)

---

## Testing (4 tasks)

Verification and quality assurance.

- [x] T017 [S0003] [P] Manual test - download by numeric ID and both URL patterns
- [x] T018 [S0003] [P] Manual test - batch download (multiple args) and file input (--file)
- [x] T019 [S0003] Manual test - --split flag, --output dir, --verbose, and error handling
- [x] T020 [S0003] Quality gates - ruff format, ruff check, ASCII encoding validation

---

## Completion Checklist

Before marking session complete:

- [x] All tasks marked `[x]`
- [x] All manual tests passing
- [x] All files ASCII-encoded (0-127)
- [x] implementation-notes.md updated
- [x] Ready for `/validate`

---

## Notes

### Parallelization
Tasks T017 and T018 can be run in parallel during testing phase.

### Task Timing
Target ~20-25 minutes per task.

### Dependencies
- T003-T007 (Foundation) must complete before T008-T016 (Implementation)
- T016 depends on T008-T015 being complete
- Testing tasks (T017-T020) depend on all implementation tasks

### Key Patterns from search.py
- Global `_verbose` flag pattern
- `console` and `err_console` for rich output
- `api_request()` function pattern with timeout and error handling
- `sys.exit(1)` for CLI failures
- pathlib.Path for file operations

### URL Patterns to Support
1. Numeric ID: `5428`
2. n8n.io URL: `https://n8n.io/workflows/5428-workflow-name/`
3. API URL: `https://api.n8n.io/api/templates/workflows/5428`

---

## Next Steps

Run `/implement` to begin AI-led implementation.
