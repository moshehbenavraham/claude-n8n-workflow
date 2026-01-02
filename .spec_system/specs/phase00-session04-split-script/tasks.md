# Task Checklist

**Session ID**: `phase00-session04-split-script`
**Total Tasks**: 20
**Estimated Duration**: 6-8 hours
**Created**: 2026-01-02

---

## Legend

- `[x]` = Completed
- `[ ]` = Pending
- `[P]` = Parallelizable (can run with other [P] tasks)
- `[S0004]` = Session reference (Phase 00, Session 04)
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

- [x] T001 [S0004] Verify prerequisites met (Python 3.11+, click, rich installed)
- [x] T002 [S0004] Verify test workflows available in n8n-workflows/ for testing

---

## Foundation (5 tasks)

Core structures, constants, and helper functions.

- [x] T003 [S0004] Create scripts/split.py with docstring, imports, and constants (`scripts/split.py`)
- [x] T004 [S0004] [P] Implement sanitize_filename helper function (`scripts/split.py`)
- [x] T005 [S0004] [P] Implement count_formatted_lines helper function (`scripts/split.py`)
- [x] T006 [S0004] [P] Implement write_json helper function (`scripts/split.py`)
- [x] T007 [S0004] Set up click CLI structure with main command and options (`scripts/split.py`)

---

## Implementation (9 tasks)

Main splitting logic implementation.

- [x] T008 [S0004] Implement find_json_files function to discover workflow files (`scripts/split.py`)
- [x] T009 [S0004] Implement extract_metadata function for 01-metadata.json (`scripts/split.py`)
- [x] T010 [S0004] Implement extract_settings function for 02-settings.json (`scripts/split.py`)
- [x] T011 [S0004] Implement extract_connections function for 03-connections.json (`scripts/split.py`)
- [x] T012 [S0004] Implement extract_nodes function for 04-nodes.json with threshold check (`scripts/split.py`)
- [x] T013 [S0004] Implement split_nodes_to_files function for individual node files (`scripts/split.py`)
- [x] T014 [S0004] Implement handle_template_nodes function for 05-template-nodes.json (`scripts/split.py`)
- [x] T015 [S0004] Implement split_workflow function combining all extraction logic (`scripts/split.py`)
- [x] T016 [S0004] Implement main CLI with progress bar and summary table (`scripts/split.py`)

---

## Testing (4 tasks)

Verification and quality assurance.

- [x] T017 [S0004] [P] Run ruff format and ruff check, fix any issues (`scripts/split.py`)
- [x] T018 [S0004] [P] Validate ASCII encoding on all output files
- [x] T019 [S0004] Manual testing: default directory, single file, custom threshold
- [x] T020 [S0004] Manual testing: edge cases (empty dir, invalid JSON, large workflows)

---

## Completion Checklist

Before marking session complete:

- [x] All tasks marked `[x]`
- [x] All tests passing (manual tests documented)
- [x] All files ASCII-encoded
- [x] implementation-notes.md updated
- [x] Ready for `/validate`

---

## Notes

### Parallelization
Tasks T004-T006 (helper functions) can be worked on simultaneously.
Tasks T017-T018 (quality checks) can be run in parallel.

### Task Timing
Target ~20-25 minutes per task.

### Dependencies
- T003 must complete before T004-T007
- T007 must complete before T008-T016
- T008-T015 should be done in order (building blocks)
- T016 depends on all extraction functions

### Key Implementation Details

**From existing split-workflows.sh to preserve:**
- Line threshold default: 300
- Output structure: workflow.json (small) OR 01-metadata.json, 02-settings.json, etc.
- Node splitting: nodes/ directory with _index.json
- Filename sanitization: Replace /:*?"<>|\n\r\t with underscore

**CLI Options to implement:**
```
python scripts/split.py                          # All files in n8n-workflows/
python scripts/split.py workflow.json            # Single file
python scripts/split.py --threshold 500          # Custom threshold
python scripts/split.py --input-dir /path        # Custom input directory
python scripts/split.py --output-dir /path       # Custom output directory
python scripts/split.py --verbose                # Debug output
```

**Output Files Structure:**
```
workflow-name/
  workflow.json              # If small (< threshold lines)
  01-metadata.json           # If large
  02-settings.json
  03-connections.json
  04-nodes.json              # OR nodes/ directory
  05-template-nodes.json     # Optional
  06-image.json              # Optional
  nodes/
    _index.json
    00-type-name.json
    01-type-name.json
    ...
```

---

## Next Steps

Run `/implement` to begin AI-led implementation.
