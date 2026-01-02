# Session Specification

**Session ID**: `phase00-session01-project-setup`
**Phase**: 00 - Python Migration
**Status**: Not Started
**Created**: 2026-01-02

---

## 1. Session Overview

This session establishes the foundational Python project structure required for migrating the existing Bash utility scripts to Python. The current toolkit consists of three Bash scripts (search-workflows.sh, download-workflows.sh, split-workflows.sh) that will be converted to Python in subsequent sessions.

Without proper project scaffolding, the script conversions in sessions 02-04 cannot proceed. This session creates the requirements.txt with pinned dependencies, sets up the package structure with proper `__init__.py` files, and implements shared utility modules that will be reused across all Python scripts.

The session follows the hybrid approach defined in the PRD: Python handles utility operations while Claude Code continues to handle AI orchestration. The Claude Code agents and skills remain completely unchanged.

---

## 2. Objectives

1. Create `scripts/requirements.txt` with pinned production dependencies (click, requests, rich)
2. Establish Python package structure with `__init__.py` files and proper imports
3. Implement shared utilities module (`scripts/utils/`) with logging and common functions
4. Create pyproject.toml for ruff linting/formatting configuration
5. Document virtual environment setup in README

---

## 3. Prerequisites

### Required Sessions
- [x] Initial project state - Bash scripts exist and are functional

### Required Tools/Knowledge
- Python 3.11+ installed
- pip/venv available
- Familiarity with click, requests, rich libraries

### Environment Requirements
- Linux/macOS/WSL environment
- Write access to scripts/ directory

---

## 4. Scope

### In Scope (MVP)
- requirements.txt with pinned versions
- Package structure: `scripts/__init__.py`, `scripts/utils/__init__.py`
- Shared logging utility (Python equivalent of logging.sh)
- Common CLI options/decorators for reuse
- pyproject.toml with ruff configuration
- Virtual environment setup documentation

### Out of Scope (Deferred)
- search.py script - *Reason: Session 02*
- download.py script - *Reason: Session 03*
- split.py script - *Reason: Session 04*
- Pytest test suite - *Reason: Session 05*
- Full documentation - *Reason: Session 06*
- CI/CD pipeline - *Reason: Future phase*

---

## 5. Technical Approach

### Architecture
The Python scripts will live alongside the Bash originals in `scripts/`. A shared `utils/` package provides common functionality: logging, CLI decorators, and path utilities. Each script will be a standalone CLI tool using click decorators.

```
scripts/
  __init__.py              # Package marker
  requirements.txt         # Pinned dependencies
  utils/
    __init__.py           # Utils package marker
    logging.py            # Structured logging (replaces logging.sh)
    cli.py                # Shared CLI options and decorators
    paths.py              # Cross-platform path utilities
```

### Design Patterns
- **Decorator pattern**: click decorators for shared CLI options
- **Module pattern**: Isolated utility modules for single responsibility
- **Factory pattern**: Logging configuration factory

### Technology Stack
- Python 3.11+ (required for modern syntax)
- click>=8.1.0 (CLI framework with decorators)
- requests>=2.31.0 (HTTP client)
- rich>=13.0.0 (terminal formatting and tables)
- ruff (linting and formatting)

---

## 6. Deliverables

### Files to Create
| File | Purpose | Est. Lines |
|------|---------|------------|
| `scripts/requirements.txt` | Pinned production dependencies | ~10 |
| `scripts/__init__.py` | Package marker, version info | ~5 |
| `scripts/utils/__init__.py` | Utils package exports | ~10 |
| `scripts/utils/logging.py` | Structured logging utility | ~50 |
| `scripts/utils/cli.py` | Shared CLI decorators | ~40 |
| `scripts/utils/paths.py` | Cross-platform path handling | ~30 |
| `pyproject.toml` | Ruff configuration | ~25 |

### Files to Modify
| File | Changes | Est. Lines |
|------|---------|------------|
| `scripts/README_scripts.md` | Add Python setup section | ~30 |

---

## 7. Success Criteria

### Functional Requirements
- [ ] `pip install -r scripts/requirements.txt` completes without errors
- [ ] `python -c "from scripts.utils import logging"` imports successfully
- [ ] `python -c "from scripts.utils.cli import common_options"` imports successfully
- [ ] Logging utility produces colored output with rich
- [ ] Path utilities handle both Windows and Unix paths

### Testing Requirements
- [ ] Manual import tests for all modules
- [ ] Manual verification of logging output formatting
- [ ] Virtual environment creation and activation tested

### Quality Gates
- [ ] All files ASCII-encoded (0-127 characters only)
- [ ] Unix LF line endings
- [ ] ruff check passes with zero errors
- [ ] ruff format produces no changes
- [ ] Type hints on all public functions

---

## 8. Implementation Notes

### Key Considerations
- Existing `logging.sh` provides the logging API to mirror in Python
- Use `pathlib.Path` consistently (per CONVENTIONS.md)
- click decorators should compose cleanly for shared options like --verbose, --dry-run
- Consider future Windows compatibility for path handling

### Potential Challenges
- **click decorator composition**: Shared decorators must work with click's group/command hierarchy - test early
- **Relative imports**: Package structure must support `from scripts.utils import X` and `from .utils import X`
- **Logging levels**: Map existing Bash logging (info, warn, error) to Python logging levels

### Relevant Considerations
- [P00] **Embedded Python in Bash**: The existing split-workflows.sh has Python patterns - review for extraction into utils
- [P00] **rich vs colorama**: Using rich as decided in CONSIDERATIONS.md - provides better table formatting
- [P00] **click vs argparse**: Using click as decided - better CLI ergonomics with decorators

### ASCII Reminder
All output files must use ASCII-only characters (0-127). Avoid curly quotes, em-dashes, and non-ASCII punctuation.

---

## 9. Testing Strategy

### Unit Tests
- Deferred to Session 05 (pytest setup)

### Integration Tests
- Deferred to Session 05

### Manual Testing
- Create virtual environment and install dependencies
- Import each module from Python REPL
- Test logging output at each level (debug, info, warn, error)
- Verify path utilities on current platform

### Edge Cases
- Empty path handling in paths.py
- Missing/malformed requirements.txt
- Import cycles between utils modules (avoid by design)

---

## 10. Dependencies

### External Libraries
- click: >=8.1.0
- requests: >=2.31.0
- rich: >=13.0.0
- ruff: >=0.1.0 (dev dependency)

### Other Sessions
- **Depends on**: None (foundational session)
- **Depended by**: phase00-session02-search-script, phase00-session03-download-script, phase00-session04-split-script

---

## Next Steps

Run `/tasks` to generate the implementation task checklist.
