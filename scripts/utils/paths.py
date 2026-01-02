"""Cross-platform path utilities for n8n workflow analyzer scripts.

Uses pathlib.Path consistently for cross-platform compatibility.
"""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to the project root (parent of scripts/).
    """
    return Path(__file__).parent.parent.parent.resolve()


def get_scripts_dir() -> Path:
    """Get the scripts directory.

    Returns:
        Path to the scripts/ directory.
    """
    return Path(__file__).parent.parent.resolve()


def get_logs_dir() -> Path:
    """Get the logs directory, creating it if needed.

    Returns:
        Path to the logs/ directory.
    """
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def ensure_dir(path: Path | str) -> Path:
    """Ensure a directory exists, creating it if needed.

    Args:
        path: Directory path to ensure exists.

    Returns:
        The Path object for the directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_path(path: Path | str, base: Path | None = None) -> Path:
    """Resolve a path, optionally relative to a base directory.

    Args:
        path: Path to resolve.
        base: Optional base directory for relative paths.

    Returns:
        Resolved absolute Path.
    """
    path = Path(path)
    if path.is_absolute():
        return path.resolve()
    if base is not None:
        return (Path(base) / path).resolve()
    return path.resolve()


def is_safe_path(path: Path | str, allowed_root: Path | str) -> bool:
    """Check if a path is safely within an allowed root directory.

    Prevents path traversal attacks by ensuring the resolved path
    is within the allowed root.

    Args:
        path: Path to check.
        allowed_root: Root directory that path must be within.

    Returns:
        True if path is within allowed_root, False otherwise.
    """
    path = Path(path).resolve()
    allowed_root = Path(allowed_root).resolve()
    try:
        path.relative_to(allowed_root)
        return True
    except ValueError:
        return False
