# ---------------------------------------------------------------------
# Gufo Thor: backup removal
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Remove a local database backup."""

# Python modules
import shutil

# Gufo Thor modules
from ..config import config
from .backup import BACKUP_NAME_RE


def remove_backup(name: str) -> None:
    """Remove a backup directory from the local backup directory.

    Args:
        name: Name of the backup directory to remove.

    Raises:
        ValueError: If the name is invalid or the backup does not exist.
        OSError: If the backup directory cannot be removed.
    """
    if not BACKUP_NAME_RE.fullmatch(name):
        msg = (
            "Backup name must start with a letter or digit and contain only "
            "letters, digits, dots, underscores, and hyphens"
        )
        raise ValueError(msg)
    backup_path = config.local_backup_path / name
    if backup_path.is_symlink() or not backup_path.is_dir():
        raise ValueError(f"Backup {name} does not exist")
    shutil.rmtree(backup_path)
