"""Structured logging utility for n8n workflow analyzer scripts.

Provides colored console output using rich and JSON error capture.
Mirrors the API from logging.sh for consistency.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.console import Console

# Module-level console instances
_console = Console()
_error_console = Console(stderr=True)

# Determine project paths
_SCRIPT_DIR = Path(__file__).parent.parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_LOGS_DIR = _PROJECT_ROOT / "logs"


def _get_timestamp() -> str:
    """Get ISO 8601 timestamp with milliseconds."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _get_file_timestamp() -> str:
    """Get filesystem-safe timestamp for filenames."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S")


def _ensure_logs_dir() -> Path:
    """Ensure logs directory exists and return its path."""
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return _LOGS_DIR


class Logger:
    """Structured logger with colored console output.

    Example:
        logger = Logger()
        logger.info("Processing started")
        logger.error("Failed to download", context="download")
    """

    def __init__(self, verbose: bool = False) -> None:
        """Initialize logger.

        Args:
            verbose: If True, show debug messages.
        """
        self.verbose = verbose
        self._console = _console
        self._error_console = _error_console

    def debug(self, msg: str) -> None:
        """Log debug message (only shown if verbose=True).

        Args:
            msg: Message to log.
        """
        if self.verbose:
            timestamp = _get_timestamp()
            self._console.print(f"[blue][{timestamp}][/blue] [dim]DEBUG[/dim] {msg}")

    def info(self, msg: str) -> None:
        """Log info message.

        Args:
            msg: Message to log.
        """
        timestamp = _get_timestamp()
        self._console.print(f"[blue][{timestamp}][/blue] [green]INFO[/green]  {msg}")

    def warn(self, msg: str) -> None:
        """Log warning message to stderr.

        Args:
            msg: Message to log.
        """
        timestamp = _get_timestamp()
        self._error_console.print(f"[blue][{timestamp}][/blue] [yellow]WARN[/yellow]  {msg}")

    def error(
        self,
        msg: str,
        context: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Log error message to stderr and optionally capture to JSON.

        Args:
            msg: Error message.
            context: Optional context name (e.g., "download", "parse").
            extra: Optional extra JSON data to include.
        """
        timestamp = _get_timestamp()
        self._error_console.print(f"[blue][{timestamp}][/blue] [red]ERROR[/red] {msg}")

        if context:
            capture_error("ShellError", msg, context=extra or {}, operation=context)


def capture_error(
    error_type: str,
    message: str,
    stack_trace: str | None = None,
    context: dict[str, Any] | None = None,
    operation: str | None = None,
) -> Path:
    """Capture structured error to JSON file (AI-friendly format).

    Args:
        error_type: Error type (e.g., "ConnectionError", "ValidationError").
        message: Error message.
        stack_trace: Optional stack trace string.
        context: Optional context dictionary.
        operation: Optional operation name.

    Returns:
        Path to the created error JSON file.
    """
    logs_dir = _ensure_logs_dir()
    timestamp = _get_timestamp()
    file_timestamp = _get_file_timestamp()

    output_file = logs_dir / f"last_error_{file_timestamp}.json"

    ctx = context or {}
    if operation:
        ctx["operation"] = operation

    error_data = {
        "timestamp": timestamp,
        "level": "error",
        "msg": message,
        "error": {
            "type": error_type,
            "message": message,
            "stack": stack_trace,
        },
        "context": ctx,
    }

    output_file.write_text(json.dumps(error_data, indent=2), encoding="utf-8")
    return output_file


def log_structured(
    level: str,
    msg: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Append structured log entry to daily log file.

    Args:
        level: Log level (e.g., "info", "error").
        msg: Log message.
        context: Optional context dictionary.
    """
    logs_dir = _ensure_logs_dir()
    timestamp = _get_timestamp()
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")

    log_file = logs_dir / f"{date_str}.log"

    entry = {
        "timestamp": timestamp,
        "level": level,
        "msg": msg,
        "context": context or {},
    }

    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# Convenience function to get a configured logger
def get_logger(verbose: bool = False) -> Logger:
    """Get a configured Logger instance.

    Args:
        verbose: If True, show debug messages.

    Returns:
        Configured Logger instance.
    """
    return Logger(verbose=verbose)
