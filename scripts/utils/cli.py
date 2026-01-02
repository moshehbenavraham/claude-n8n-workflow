"""Shared CLI utilities and decorators for n8n workflow analyzer scripts.

Provides reusable click decorators for common options like --verbose and --dry-run.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

import click

F = TypeVar("F", bound=Callable[..., Any])


def verbose_option(func: F) -> F:
    """Add --verbose/-v option to a click command.

    Args:
        func: Click command function to decorate.

    Returns:
        Decorated function with verbose option.
    """
    return click.option(
        "--verbose",
        "-v",
        is_flag=True,
        default=False,
        help="Enable verbose output with debug messages.",
    )(func)


def dry_run_option(func: F) -> F:
    """Add --dry-run/-n option to a click command.

    Args:
        func: Click command function to decorate.

    Returns:
        Decorated function with dry-run option.
    """
    return click.option(
        "--dry-run",
        "-n",
        is_flag=True,
        default=False,
        help="Show what would be done without making changes.",
    )(func)


def common_options(func: F) -> F:
    """Add common options (--verbose, --dry-run) to a click command.

    Usage:
        @click.command()
        @common_options
        def my_command(verbose: bool, dry_run: bool):
            pass

    Args:
        func: Click command function to decorate.

    Returns:
        Decorated function with common options.
    """

    @verbose_option
    @dry_run_option
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def output_option(func: F) -> F:
    """Add --output/-o option for output file path.

    Args:
        func: Click command function to decorate.

    Returns:
        Decorated function with output option.
    """
    return click.option(
        "--output",
        "-o",
        type=click.Path(),
        default=None,
        help="Output file path.",
    )(func)


def format_option(
    formats: list[str] | None = None,
    default: str = "json",
) -> Callable[[F], F]:
    """Add --format/-f option for output format selection.

    Args:
        formats: List of allowed format strings. Defaults to ["json", "text", "table"].
        default: Default format. Defaults to "json".

    Returns:
        Decorator function.
    """
    if formats is None:
        formats = ["json", "text", "table"]

    def decorator(func: F) -> F:
        return click.option(
            "--format",
            "-f",
            "output_format",
            type=click.Choice(formats, case_sensitive=False),
            default=default,
            help=f"Output format. Choices: {', '.join(formats)}.",
        )(func)

    return decorator
