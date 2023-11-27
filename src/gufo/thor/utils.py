# ---------------------------------------------------------------------
# Gufo Thor: Various utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""Various utilities."""

# Python modules
import os
import shutil
from pathlib import Path
from typing import Optional

# Gufo Thor modules
from .log import logger


def write_file(
    path: Path, content: str, backup_path: Optional[Path] = None
) -> bool:
    """
    Write data to file.

    Overwrite file content only if changed.

    Args:
        path: File path.
        content: File content.
        backup_path: Path to store a copy of file when overwritten.

    Returns:
        True: if file was written.
        False: if file wasn't changed.
    """
    if os.path.exists(path):
        with open(path) as fp:
            fdata = fp.read()
            if fdata == content:
                return False  # Not changed
        if backup_path:
            shutil.move(path, backup_path)
    logger.warning("Writing file %s", path)
    with open(path, "w") as fp:
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
