# ---------------------------------------------------------------------
# Gufo Thor: database restore orchestration
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Restore database services from a local backup."""

# Python modules
from pathlib import Path, PurePosixPath
from typing import cast

# Gufo Thor modules
from ..config import config
from ..docker import docker
from ..services.base import loader
from ..services.db import DBService
from .backup import BACKUP_NAME_RE, BACKUP_SERVICES


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


def _run_restore(service: DBService, backup_name: str, backup_path: Path) -> None:
    """Run one database restore script inside its Compose service.

    Args:
        service: Database service whose restore script will be run.
        backup_name: Name of the backup directory mounted in the container.
        backup_path: Local directory containing the backup artifact.
    """
    script_path = backup_path / service.get_restore_script_name()
    script_path.write_text(service.get_restore_script())
    script_path.chmod(0o755)
    workdir = PurePosixPath(_get_backup_mount_path(service)) / backup_name
    if not docker.compose_exec(
        "-T",
        "-w",
        str(workdir),
        service.get_compose_name(),
        f"./{service.get_restore_script_name()}",
    ):
        msg = f"Restore failed for service {service.name}"
        raise RuntimeError(msg)


def restore(name: str, items: list[str] | None = None) -> None:
    """Restore selected database services from a local backup.

    If no services are selected, every supported dump present in the backup
    directory is restored.

    Args:
        name: Name of the backup directory.
        items: Database service names to restore, or None for all available.
    """
    if not BACKUP_NAME_RE.fullmatch(name):
        msg = (
            "Backup name must start with a letter or digit and contain only "
            "letters, digits, dots, underscores, and hyphens"
        )
        raise ValueError(msg)
    selected = BACKUP_SERVICES if items is None else set(items)
    unsupported = selected - BACKUP_SERVICES
    if unsupported:
        names = ", ".join(sorted(unsupported))
        msg = f"Restore is not supported for services: {names}"
        raise ValueError(msg)
    backup_path = config.local_backup_path / name
    if not backup_path.is_dir():
        msg = f"Backup {name} does not exist"
        raise ValueError(msg)
    services = [
        cast(DBService, loader[service_name])
        for service_name in sorted(selected)
    ]
    if items is None:
        services = [
            service
            for service in services
            if (backup_path / service.get_backup_file_name()).is_file()
        ]
    missing = [
        service.name
        for service in services
        if not (backup_path / service.get_backup_file_name()).is_file()
    ]
    if missing:
        names = ", ".join(missing)
        msg = f"Backup {name} does not contain dumps for: {names}"
        raise ValueError(msg)
    if not services:
        msg = f"Backup {name} does not contain database dumps"
        raise ValueError(msg)
    compose_names = [service.get_compose_name() for service in services]
    with docker.with_started(compose_names), docker.with_paused():
        for service in services:
            _run_restore(service, name, backup_path)
