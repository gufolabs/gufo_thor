# ---------------------------------------------------------------------
# Gufo Thor: backup tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import datetime
import os
from contextlib import nullcontext
from pathlib import Path
from typing import ContextManager

# Third-party modules
import pytest

# Gufo Thor modules
import gufo.thor.backup.backup as backup_module
import gufo.thor.backup.restore as restore_module
from gufo.thor.backup.info import BackupInfo
from gufo.thor.backup.rm import remove_backup
from gufo.thor.services.db import DBService


class FakeDBService(DBService):
    """Minimal database service for backup and restore tests.

    Attributes:
        compose_image: Test image name required by the base class.
    """

    compose_image = "test/database"

    def __init__(self, name: str) -> None:
        """Initialize a fake service.

        Args:
            name: Service name.
        """
        super().__init__()
        self.name = name
        self.compose_volumes = ["backup:/var/lib/backup"]
        self.backup_file_name = f"{name}.dump"

    def get_backup_script(self) -> str:
        """Return a placeholder backup script.

        Returns:
            Placeholder shell script.
        """
        return "#!/bin/sh\n"

    def get_restore_script(self) -> str:
        """Return a placeholder restore script.

        Returns:
            Placeholder shell script.
        """
        return "#!/bin/sh\n"


def test_backup_info_from_dir(tmp_path: Path) -> None:
    backup_path = tmp_path / "backup-1"
    backup_path.mkdir()
    expected_sizes = {
        "postgres.dump": 5,
        "mongo.dump": 2,
        "clickhouse.zip": 9,
    }
    for name, size in expected_sizes.items():
        (backup_path / name).write_bytes(b"x" * size)
    dir_stat = backup_path.stat()
    created_timestamp = getattr(dir_stat, "st_birthtime", dir_stat.st_ctime)
    created_at = datetime.datetime.fromtimestamp(created_timestamp)
    for offset, name in enumerate(expected_sizes, start=1):
        dump = backup_path / name
        modified = created_at.timestamp() + 10 * offset
        os.utime(dump, (modified, modified))

    info = BackupInfo.from_dir(backup_path)

    assert info.name == "backup-1"
    assert info.ts == created_at
    assert info.postgres_size == expected_sizes["postgres.dump"]
    assert info.mongo_size == expected_sizes["mongo.dump"]
    assert info.clickhouse_size == expected_sizes["clickhouse.zip"]
    assert info.duration == datetime.timedelta(seconds=30)


def test_backup_info_from_empty_dir(tmp_path: Path) -> None:
    backup_path = tmp_path / "empty"
    backup_path.mkdir()

    info = BackupInfo.from_dir(backup_path)

    assert info.name == "empty"
    assert info.postgres_size is None
    assert info.mongo_size is None
    assert info.clickhouse_size is None
    assert info.duration is None


def test_backup_runs_selected_service(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    postgres = FakeDBService("postgres")
    services: dict[str, DBService] = {"postgres": postgres}
    monkeypatch.setattr(backup_module, "loader", services)
    started: list[list[str]] = []
    paused: list[bool] = []

    def with_started(names: list[str]) -> ContextManager[None]:
        started.append(names)
        return nullcontext()

    def with_paused() -> ContextManager[None]:
        paused.append(True)
        return nullcontext()

    def run_backup(service: DBService, name: str) -> None:
        artifact = Path("data/backup") / name / service.get_backup_file_name()
        artifact.write_bytes(b"dump")

    monkeypatch.setattr(backup_module.docker, "with_started", with_started)
    monkeypatch.setattr(backup_module.docker, "with_paused", with_paused)
    monkeypatch.setattr(backup_module, "_run_backup", run_backup)

    info = backup_module.backup(["postgres"], name="test-backup")

    assert info.name == "test-backup"
    assert info.postgres_size == 4
    assert started == [["postgres"]]
    assert paused == [True]
    assert (
        Path("data/backup/test-backup") / postgres.get_backup_script_name()
    ).is_file()
    assert (
        Path("data/backup/test-backup") / postgres.get_restore_script_name()
    ).is_file()


def test_restore_defaults_to_dumps_present(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    backup_path = Path("data/backup/test-backup")
    backup_path.mkdir(parents=True)
    (backup_path / "postgres.dump").write_bytes(b"dump")
    services: dict[str, DBService] = {
        "postgres": FakeDBService("postgres"),
        "mongo": FakeDBService("mongo"),
        "clickhouse": FakeDBService("clickhouse"),
    }
    monkeypatch.setattr(restore_module, "loader", services)
    started: list[list[str]] = []
    paused: list[bool] = []
    exec_calls: list[tuple[str, ...]] = []

    def with_started(names: list[str]) -> ContextManager[None]:
        started.append(names)
        return nullcontext()

    def with_paused() -> ContextManager[None]:
        paused.append(True)
        return nullcontext()

    def compose_exec(*args: str) -> bool:
        exec_calls.append(args)
        return True

    monkeypatch.setattr(restore_module.docker, "with_started", with_started)
    monkeypatch.setattr(restore_module.docker, "with_paused", with_paused)
    monkeypatch.setattr(restore_module.docker, "compose_exec", compose_exec)

    restore_module.restore("test-backup")

    assert started == [["postgres"]]
    assert paused == [True]
    assert exec_calls == [
        (
            "-T",
            "-w",
            "/var/lib/backup/test-backup",
            "postgres",
            "./postgres-restore.sh",
        )
    ]
    assert (backup_path / "postgres-restore.sh").is_file()


def test_restore_rejects_missing_selected_dump(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    (Path("data/backup/test-backup")).mkdir(parents=True)
    monkeypatch.setattr(
        restore_module,
        "loader",
        {"mongo": FakeDBService("mongo")},
    )

    with pytest.raises(ValueError, match="does not contain dumps for: mongo"):
        restore_module.restore("test-backup", ["mongo"])


def test_remove_backup_removes_only_named_backup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    backup_path = Path("data/backup/nightly")
    backup_path.mkdir(parents=True)
    (backup_path / "postgres.dump").write_bytes(b"dump")
    outside_path = Path("outside")
    outside_path.mkdir()

    remove_backup("nightly")

    assert not backup_path.exists()
    assert outside_path.is_dir()
    with pytest.raises(ValueError, match="Backup name"):
        remove_backup("../outside")
