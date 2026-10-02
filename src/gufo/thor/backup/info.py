# ---------------------------------------------------------------------
# Gufo Thor: backup information
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Backup information model."""

# Python modules
import datetime
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BackupInfo:
    """Metadata describing a completed backup.

    Attributes:
        name: Backup directory name.
        ts: Backup directory creation time.
        postgres_size: PostgreSQL dump size in bytes, if present.
        mongo_size: MongoDB dump size in bytes, if present.
        clickhouse_size: ClickHouse archive size in bytes, if present.
        duration: Time from directory creation to the latest dump modification.
    """

    name: str
    ts: datetime.datetime
    postgres_size: int | None = None
    mongo_size: int | None = None
    clickhouse_size: int | None = None
    duration: datetime.timedelta | None = None

    @classmethod
    def from_dir(cls, path: Path) -> "BackupInfo":
        """Create backup metadata from a backup directory.

        Args:
            path: Backup directory path.

        Returns:
            Metadata for the backup directory.
        """
        stat = path.stat()
        created_at = datetime.datetime.fromtimestamp(
            getattr(stat, "st_birthtime", stat.st_ctime)
        )
        postgres_dump = path / "postgres.dump"
        size = (
            postgres_dump.stat().st_size if postgres_dump.is_file() else None
        )
        mongo_dump = path / "mongo.dump"
        mongo_size = (
            mongo_dump.stat().st_size if mongo_dump.is_file() else None
        )
        clickhouse_dump = path / "clickhouse.zip"
        clickhouse_size = (
            clickhouse_dump.stat().st_size
            if clickhouse_dump.is_file()
            else None
        )
        dump_paths = [postgres_dump, mongo_dump, clickhouse_dump]
        dump_mtimes = [
            dump.stat().st_mtime for dump in dump_paths if dump.is_file()
        ]
        duration = None
        if dump_mtimes:
            latest_dump = datetime.datetime.fromtimestamp(max(dump_mtimes))
            duration = latest_dump - created_at
        return cls(
            name=path.name,
            ts=created_at,
            postgres_size=size,
            mongo_size=mongo_size,
            clickhouse_size=clickhouse_size,
            duration=duration,
        )
