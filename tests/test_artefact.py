# ---------------------------------------------------------------------
# Gufo Thor: Artefact tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import os
from operator import attrgetter
from pathlib import Path
from tempfile import TemporaryDirectory

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.artefact import DEFAULT_LOCAL_BASE, Artefact, ArtefactMountPoint

from .utils import suppress_is_test


def test_file_artefact() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        local_path = Path(root) / "test.txt"
        local_path.touch()
        container_path = Path("/", "tmp", "test.txt")
        art = Artefact(name, local_path)
        art_mount = art.at(container_path)
        mounts = list(art_mount.iter_mounts())
        assert mounts == [
            ArtefactMountPoint(
                name=name, local_path=local_path, container_path=container_path
            )
        ]


def test_dir_artefact() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        local_root = Path(root)
        for n in range(3):
            local_path = local_root / f"{n}.txt"
            local_path.touch()
        container_path = Path("/", "mnt")
        art = Artefact(name, local_root)
        art_mount = art.at(container_path)
        mounts = sorted(art_mount.iter_mounts(), key=attrgetter("local_path"))
        assert mounts
        # local_path contains random prefix, split it for tests
        for m in mounts:
            m.local_path = m.local_path.relative_to(local_root)
        assert mounts == [
            ArtefactMountPoint(
                name="test-f79bdd",
                local_path=Path("0.txt"),
                container_path=Path("/mnt/0.txt"),
            ),
            ArtefactMountPoint(
                name="test-0a23af",
                local_path=Path("1.txt"),
                container_path=Path("/mnt/1.txt"),
            ),
            ArtefactMountPoint(
                name="test-1c46e2",
                local_path=Path("2.txt"),
                container_path=Path("/mnt/2.txt"),
            ),
        ]


def test_file_write() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        local_path = Path(root) / "test.txt"
        art = Artefact(name, local_path)
        sample = "12345"
        art.write(sample)
        with open(local_path) as fp:
            data = fp.read()
            assert data == sample


def test_copy_from() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        sample = "12345"
        source_path = Path(root) / "source.txt"
        with open(source_path, "w") as fp:
            fp.write(sample)
        local_path = Path(root) / "test.txt"
        art = Artefact(name, local_path)
        art.copy_from(source_path)
        with open(local_path) as fp:
            data = fp.read()
            assert data == sample


def test_fail_symlink() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        file_path = Path(root) / "orig.txt"
        file_path.touch()
        local_path = Path(root) / "test.txt"
        local_path.symlink_to(file_path)
        container_path = Path("/", "tmp", "test.txt")
        art = Artefact(name, local_path)
        art_mount = art.at(container_path)
        with pytest.raises(ValueError):
            list(art_mount.iter_mounts())


def test_fail_not_mounted() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        local_path = Path(root) / "test.txt"
        local_path.touch()
        art = Artefact(name, local_path)
        with pytest.raises(ValueError):
            list(art.iter_mounts())


def test_fail_not_exists() -> None:
    with TemporaryDirectory() as root:
        name = "test"
        local_path = Path(root) / "test.txt"
        local_path.touch()
        non_existed_file = Path(root) / "nonexistent.txt"
        container_path = Path("/", "tmp", "test.txt")
        art = Artefact(name, non_existed_file)
        art_mount = art.at(container_path)
        with pytest.raises(ValueError):
            list(art_mount.iter_mounts())


def test_mount_hash():
    a1 = ArtefactMountPoint(
        name="test", local_path=Path("/"), container_path=Path("/")
    )
    a2 = ArtefactMountPoint(
        name="test", local_path=Path("/"), container_path=Path("/")
    )
    assert hash(a1) == hash(a2)


@pytest.mark.parametrize(
    ("artefact", "expected"),
    [
        (
            Artefact("test", Path("/", "tmp", "1")),
            "<Artefact test from /tmp/1>",
        ),
        (
            Artefact("test", Path("/", "tmp", "1")).at(Path("/", "opt")),
            "<Artefact test from /tmp/1 mounted at /opt>",
        ),
    ],
)
def test_repr(artefact: Artefact, expected: str) -> None:
    assert repr(artefact) == expected


def test_no_local_base_fail() -> None:
    local_base = Artefact._local_base
    Artefact._local_base = DEFAULT_LOCAL_BASE
    try:
        with pytest.raises(RuntimeError):
            Artefact("test", Path("/", "tmp"))
    finally:
        Artefact._local_base = local_base


def test_set_local_base_fail() -> None:
    with suppress_is_test(), pytest.raises(RuntimeError):
        Artefact._set_local_base()


def test_iter_mounts_fail() -> None:
    with TemporaryDirectory() as root:
        p = Path(root) / "file.txt"
        os.mkfifo(p)
        artefact = Artefact("test", p)
        mounted = artefact.at(Path("/", "var", "run", "link"))
        with pytest.raises(ValueError):
            list(mounted.iter_mounts())
