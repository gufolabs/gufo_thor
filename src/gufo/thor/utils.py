# ---------------------------------------------------------------------
# Gufo Thor: Various utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Various utilities."""

# Python modules
import datetime
import shutil
import sys
from pathlib import Path
from typing import Any

# Gufo Thor modules
from .log import logger


def split_version(v: str) -> tuple[int, ...]:
    """Parse a version string into comparable integer components.

    Args:
        v: Dot-separated version string.

    Returns:
        Version components as a tuple of integers.
    """
    return tuple(int(x) for x in v.split("."))


def write_file(
    path: Path, content: str | bytes, backup_path: Path | None = None
) -> bool:
    """
    Write data to file.

    Overwrite file content only if changed. Create all
    necessary directories.

    Args:
        path: File path.
        content: File content.
        backup_path: Path to store a copy of file when overwritten.

    Returns:
        True: if file was written.
        False: if file wasn't changed.
    """
    ensure_directory(path.parent)
    if path.exists():
        with open(path) as fp:
            fdata = fp.read()
            if fdata == content:
                return False  # Not changed
        if backup_path:
            shutil.move(path, backup_path)
    logger.warning("Writing file %s", path)
    mode = "w" if isinstance(content, str) else "wb"
    with open(path, mode) as fp:
        fp.write(content)
    return True


def ensure_directory(path: Path) -> None:
    """
    Ensure that the directory exists.

    Args:
        path: Directory path.
    """
    if not path.exists():
        logger.warning("Creating directory %s", path)
    path.mkdir(parents=True, exist_ok=True)


def merge_dict(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge dictionaries.

    Do not affect source dictionaries.
    Second dictionary overrides first.

    Args:
        x: First dictionary.
        y: Second dictionary.

    Returns:
        Merged dictionary.
    """
    r: dict[str, Any] = {}
    xk = set(x)
    yk = set(y)
    # Append keys which are only in first dictionary
    for k in xk - yk:
        r[k] = x[k]
    # Append keys which are only in second dictionary
    for k in yk - xk:
        r[k] = y[k]
    # Merge overlapped keys
    for k in xk.intersection(yk):
        if isinstance(x[k], dict) and isinstance(y[k], dict):
            r[k] = merge_dict(x[k], y[k])
        else:
            r[k] = y[k]
    return r


def is_test() -> bool:
    """
    Check if code executed in the test suite.

    Returns:
        True: If is in test suite.
        False: Otherwise.
    """
    return "pytest" in sys.modules


def humanize_size(size: int) -> str:
    """Convert a size in bytes to a human-readable representation.

    Sizes of 1 KiB and above are represented using binary units:
    K, M, and G. Values below 1 KiB are represented in bytes.

    Args:
        size: Size in bytes.

    Returns:
        Human-readable size with at most one decimal place.
    """
    for unit, suffix in (
        (1024 * 1024 * 1024, "G"),
        (1024 * 1024, "M"),
        (1024, "K"),
    ):
        if size >= unit:
            value = size / unit
            return f"{value:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{size}B"


def humanize_time(duration: datetime.timedelta) -> str:
    """Convert a duration to a compact human-readable representation.

    Args:
        duration: Duration to format.

    Returns:
        Duration expressed in days, hours, minutes, and seconds.
    """
    sign = "-" if duration < datetime.timedelta(0) else ""
    duration = abs(duration)
    seconds = int(duration.total_seconds())
    if seconds == 0:
        return f"{sign}<1s" if duration else "0s"
    days, seconds = divmod(seconds, 24 * 60 * 60)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    for value, unit in (
        (days, "d"),
        (hours, "h"),
        (minutes, "m"),
        (seconds, "s"),
    ):
        if value:
            parts.append(f"{value}{unit}")
    return sign + " ".join(parts)
