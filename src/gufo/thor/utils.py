# ---------------------------------------------------------------------
# Gufo Thor: Various utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-24, Gufo Labs
# ---------------------------------------------------------------------
"""Various utilities."""

# Python modules
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Gufo Thor modules
from .log import logger


def write_file(
    path: Path, content: Union[str, bytes], backup_path: Optional[Path] = None
) -> bool:
    """
    Write data to file.

    Overwrite file content only if changed. Create all
    nessessary directories.

    Args:
        path: File path.
        content: File content.
        backup_path: Path to store a copy of file when overwritten.

    Returns:
        True: if file was written.
        False: if file wasn't changed.
    """
    ensure_directory(path.parent)
    if os.path.exists(path):
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
    Check directory is exists and create, if necessary.

    Args:
        path: Directory path.
    """
    if os.path.exists(path):
        return
    logger.warning("Creating directory %s", path)
    os.makedirs(path)


def merge_dict(x: Dict[str, Any], y: Dict[str, Any]) -> Dict[str, Any]:
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
    r: Dict[str, Any] = {}
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
