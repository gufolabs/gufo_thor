# ---------------------------------------------------------------------
# Gufo Thor: backup tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import datetime
import os
import stat
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
from gufo.thor.services.clickhouse import ClickhouseService
from gufo.thor.services.db import DBService
from gufo.thor.services.mongo import MongoService
from gufo.thor.services.postgres import PostgresService


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
    assert info.duration is not None
    assert info.duration.total_seconds() == pytest.approx(30, abs=1e-3)


def test_backup_info_from_empty_dir(tmp_path: Path) -> None:
    backup_path = tmp_path / "empty"
    backup_path.mkdir()

    info = BackupInfo.from_dir(backup_path)

    assert info.name == "empty"
    assert info.postgres_size is None
    assert info.mongo_size is None
    assert info.clickhouse_size is None
    assert info.duration is None


@pytest.mark.parametrize(
    ("service_class", "backup_command", "restore_command"),
    [
        (PostgresService, "pg_dump", "pg_restore"),
        (MongoService, "mongodump", "mongorestore"),
        (ClickhouseService, "BACKUP ALL", "RESTORE ALL"),
    ],
)
def test_write_scripts_renders_service_templates(
    tmp_path: Path,
    service_class: type[DBService],
    backup_command: str,
    restore_command: str,
) -> None:
    service = service_class()

    backup_module._write_scripts(service, tmp_path)

    backup_script = tmp_path / service.get_backup_script_name()
    restore_script = tmp_path / service.get_restore_script_name()
    assert backup_command in backup_script.read_text()
    assert restore_command in restore_script.read_text()
    assert stat.S_IMODE(backup_script.stat().st_mode) == 0o755
    assert stat.S_IMODE(restore_script.stat().st_mode) == 0o755


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
    backup_script = (
        Path("data/backup/test-backup") / postgres.get_backup_script_name()
    )
    restore_script = (
        Path("data/backup/test-backup") / postgres.get_restore_script_name()
    )
    assert backup_script.read_text() == "#!/bin/sh\n"
    assert restore_script.read_text() == "#!/bin/sh\n"
    assert stat.S_IMODE(backup_script.stat().st_mode) == 0o755
    assert stat.S_IMODE(restore_script.stat().st_mode) == 0o755


def test_backup_rejects_unsupported_service() -> None:
    with pytest.raises(ValueError, match="Backup is not supported"):
        backup_module.backup(["unsupported"], name="test-backup")


def test_backup_rejects_invalid_name() -> None:
    with pytest.raises(ValueError, match="Backup name"):
        backup_module.backup([], name="../outside")


def test_run_backup_raises_when_compose_exec_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = FakeDBService("postgres")
    monkeypatch.setattr(backup_module.docker, "compose_exec", lambda *_: False)

    with pytest.raises(
        RuntimeError, match="Backup failed for service postgres"
    ):
        backup_module._run_backup(service, "test-backup")


def test_backup_raises_when_dump_is_not_created(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        backup_module, "loader", {"postgres": FakeDBService("postgres")}
    )
    monkeypatch.setattr(backup_module, "_run_backup", lambda *_: None)
    monkeypatch.setattr(
        backup_module.docker, "with_started", lambda *_: nullcontext()
    )
    monkeypatch.setattr(
        backup_module.docker, "with_paused", lambda: nullcontext()
    )

    with pytest.raises(
        RuntimeError, match="Backup for service postgres did not create a dump"
    ):
        backup_module.backup(["postgres"], name="test-backup")


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


def test_restore_rejects_invalid_name() -> None:
    with pytest.raises(ValueError, match="Backup name"):
        restore_module.restore("../outside")


def test_restore_rejects_missing_backup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        restore_module,
        "loader",
        {"postgres": FakeDBService("postgres")},
    )

    with pytest.raises(ValueError, match="Backup missing does not exist"):
        restore_module.restore("missing", ["postgres"])


def test_restore_rejects_unsupported_service() -> None:
    with pytest.raises(ValueError, match="Restore is not supported"):
        restore_module.restore("backup", ["unsupported"])


def test_restore_rejects_empty_backup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    Path("data/backup/empty").mkdir(parents=True)
    monkeypatch.setattr(
        restore_module,
        "loader",
        {
            "postgres": FakeDBService("postgres"),
            "mongo": FakeDBService("mongo"),
            "clickhouse": FakeDBService("clickhouse"),
        },
    )

    with pytest.raises(ValueError, match="does not contain database dumps"):
        restore_module.restore("empty")


def test_run_restore_raises_when_compose_exec_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    service = FakeDBService("postgres")
    monkeypatch.setattr(
        restore_module.docker, "compose_exec", lambda *_: False
    )

    with pytest.raises(
        RuntimeError, match="Restore failed for service postgres"
    ):
        restore_module._run_restore(service, "test-backup", tmp_path)


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


def test_remove_backup_rejects_missing_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Backup absent does not exist"):
        remove_backup("absent")
