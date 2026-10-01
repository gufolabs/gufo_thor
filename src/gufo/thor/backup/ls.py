# ---------------------------------------------------------------------
# Gufo Thor: backup listing
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""List local database backups."""

# Gufo Thor modules
from ..config import config
from .info import BackupInfo


def list_backups() -> list[BackupInfo]:
    """List backups from the local backup directory, newest first.

    Returns:
        Backup metadata sorted by creation timestamp in descending order.
    """
    root = config.local_backup_path
    if not root.is_dir():
        return []
    backups: list[BackupInfo] = []
    for path in root.iterdir():
        if not path.is_dir():
            continue
        info = BackupInfo.from_dir(path)
        if any(
            size is not None
            for size in (
                info.postgres_size,
                info.mongo_size,
                info.clickhouse_size,
            )
        ):
            backups.append(info)
    return sorted(backups, key=lambda info: info.ts, reverse=True)
