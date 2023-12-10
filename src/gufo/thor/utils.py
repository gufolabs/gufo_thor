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
from typing import Optional, Union

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
