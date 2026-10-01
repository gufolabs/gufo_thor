# ---------------------------------------------------------------------
# Gufo Thor: backup orchestration
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Database backup orchestration."""

# Python modules
import datetime
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
from typing import cast

# Gufo Thor modules
from ..config import config
from ..docker import docker
from ..services.base import loader
from ..services.db import DBService
from .info import BackupInfo

BACKUP_SERVICES: set[str] = {"clickhouse", "mongo", "postgres"}
BACKUP_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")


def _get_backup_mount_path(service: DBService) -> str:
    """Get the service container path for the backup volume.

    Args:
        service: Database service whose backup mount is being resolved.

    Returns:
        Container path where the shared backup volume is mounted.
    """
    for volume in service.compose_volumes or ():
        parts = volume.split(":")
        if parts[0] == "backup" and len(parts) > 1:
            return parts[1]
    msg = f"Service {service.name} does not mount the backup volume"
    raise ValueError(msg)


def _write_scripts(service: DBService, root: Path) -> None:
    """Write backup and restore scripts for a database service.

    Args:
        service: Database service that provides script names and contents.
        root: Directory where the scripts will be written.
    """
    backup_script = root / service.get_backup_script_name()
    backup_script.write_text(service.get_backup_script())
    backup_script.chmod(0o755)

    restore_script = root / service.get_restore_script_name()
    restore_script.write_text(service.get_restore_script())
    restore_script.chmod(0o755)


def _run_backup(service: DBService, backup_name: str) -> None:
    """Run one database backup script inside its Compose service.

    Args:
        service: Database service whose backup script will be run.
        backup_name: Name of the backup directory mounted in the container.
    """
    workdir = PurePosixPath(_get_backup_mount_path(service)) / backup_name
    if not docker.compose_exec(
        "-T",
        "-w",
        str(workdir),
        service.get_compose_name(),
        f"./{service.get_backup_script_name()}",
    ):
        msg = f"Backup failed for service {service.name}"
        raise RuntimeError(msg)


def backup(
    items: list[str] | None = None, *, name: str | None = None
) -> BackupInfo:
    """Back up selected database services.

    Args:
        items: Database service names to back up, or None for all allowed.
        name: Backup directory name. Defaults to the current timestamp.

    Returns:
        Metadata for the newly created backup.
    """
    selected = BACKUP_SERVICES if items is None else set(items)
    unsupported = selected - BACKUP_SERVICES
    if unsupported:
        names = ", ".join(sorted(unsupported))
        msg = f"Backup is not supported for services: {names}"
        raise ValueError(msg)
    if name is None:
        backup_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    elif not BACKUP_NAME_RE.fullmatch(name):
        msg = (
            "Backup name must start with a letter or digit and contain only "
            "letters, digits, dots, underscores, and hyphens"
        )
        raise ValueError(msg)
    else:
        backup_name = name
    services = [
        cast(DBService, loader[service_name])
        for service_name in sorted(selected)
    ]
    backup_path = config.local_backup_path / backup_name
    backup_path.mkdir(parents=True)
    for service in services:
        _write_scripts(service, backup_path)
    compose_names = [service.get_compose_name() for service in services]
    with (
        docker.with_started(compose_names),
        docker.with_paused(),
        ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as executor,
    ):
        futures = [
            executor.submit(_run_backup, service, backup_name)
            for service in services
        ]
        for future in futures:
            future.result()
    info = BackupInfo.from_dir(backup_path)
    for service in services:
        if not (backup_path / service.get_backup_file_name()).is_file():
            msg = f"Backup for service {service.name} did not create a dump"
            raise RuntimeError(msg)
    return info
