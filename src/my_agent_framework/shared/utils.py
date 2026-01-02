"""General utility functions for indus-agents framework."""

import logging
import warnings
import sys
from typing import Optional, List
from contextlib import contextmanager

def silence_warnings_and_logs(
    suppress_warnings: bool = True,
    log_level: int = logging.ERROR,
    loggers_to_quiet: Optional[List[str]] = None
) -> None:
    """
    Silence warnings and verbose logging for cleaner output.

    Args:
        suppress_warnings: Whether to suppress Python warnings
        log_level: Minimum logging level to show
        loggers_to_quiet: List of logger names to quiet
    """
    if suppress_warnings:
        warnings.filterwarnings("ignore")

    # Common noisy loggers
    default_quiet_loggers = [
        "httpx",
        "httpcore",
        "openai",
        "anthropic",
        "urllib3",
        "requests",
    ]

    loggers = loggers_to_quiet or default_quiet_loggers
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(log_level)


@contextmanager
def suppress_output():
    """Context manager to suppress stdout/stderr temporarily."""
    import io
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def safe_json_parse(json_str: str, default: any = None) -> any:
    """
    Safely parse JSON string.

    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    import json
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
