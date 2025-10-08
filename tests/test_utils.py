# ---------------------------------------------------------------------
# Gufo Thor: Utils tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict

# Third party modules
import pytest

# Gufo Thor modules
from gufo.thor.utils import ensure_directory, is_test, merge_dict, write_file


def read_file(path: Path) -> str:
    with open(path) as fp:
        return fp.read()


@pytest.mark.parametrize("path", [Path("a"), Path("b", "c"), Path("d", "e")])
def test_ensure_directory(path: Path) -> None:
    with TemporaryDirectory() as tmpdir:
        ensure_directory(Path(tmpdir) / path)


@pytest.mark.parametrize(("path", "content"), [(Path("test"), "123")])
def test_write_file(path: Path, content: str) -> None:
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / path
        for expected in (True, False, False):
            r = write_file(file_path, content)
            assert r is expected
            assert read_file(file_path) == content


def test_write_file_backup() -> None:
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "file.txt"
        backup_path = Path(tmpdir) / "file.bak"
        c1 = "1234"
        c2 = "5678"
        c3 = "9012"
        # First write, no backup
        r = write_file(file_path, c1, backup_path=backup_path)
        assert r is True
        assert not backup_path.exists()
        assert read_file(file_path) == c1
        # Second write, has backup
        r = write_file(file_path, c2, backup_path=backup_path)
        assert r is True
        assert read_file(file_path) == c2
        assert backup_path.exists()
        assert read_file(backup_path) == c1
        # Try to write the same, backup not affected
        r = write_file(file_path, c2, backup_path=backup_path)
        assert r is False
        assert read_file(file_path) == c2
        assert backup_path.exists()
        assert read_file(backup_path) == c1
        # Write new
        r = write_file(file_path, c3, backup_path=backup_path)
        assert r is True
        assert read_file(file_path) == c3
        assert backup_path.exists()
        assert read_file(backup_path) == c2


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ({}, {}, {}),
        ({"x": 1, "y": 2}, {}, {"x": 1, "y": 2}),
        ({}, {"x": 1, "y": 2}, {"x": 1, "y": 2}),
        ({"x": 1, "z": 3}, {"x": 1, "y": 2}, {"x": 1, "y": 2, "z": 3}),
        (
            {"x": 1, "y": {"z": 3, "k": 4}},
            {"a": 5, "y": {"z": 6, "n": 7}},
            {"x": 1, "a": 5, "y": {"z": 6, "k": 4, "n": 7}},
        ),
    ],
)
def test_merge_dict(
    x: Dict[str, Any], y: Dict[str, Any], expected: Dict[str, Any]
) -> None:
    r = merge_dict(x, y)
    assert r == expected


def test_is_test() -> None:
    assert is_test() is True
