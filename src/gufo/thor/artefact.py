# ---------------------------------------------------------------------
# Gufo Thor: Artefacts
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Artefact class."""

# Python modules
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Optional

# Gufo Thor modules
from .utils import write_file


@dataclass
class ArtefactMountPoint(object):
    """
    Artefact mounting point.

    Attributes:
        name: Unique artefact name.
        local_path: Path to the artefact on local file system.
        container_path: Path to the artefact in the container.
    """

    name: str
    local_path: Path
    container_path: Path

    def __hash__(self) -> int:
        """hash() implementation."""
        return hash(self.name)


class Artefact(object):
    """
    Artefact.

    Artefacts are delivered to the containers and may contain
    various configuration settings. Delivery methods may vary
    depending on target.

    Artefact may refer to a single file or to a directory.
    If artefact refers to directory, all directory members
    are exposed as single file.

    Args:
        name: Unique artefact name.
        local_path: Artefact path on thor's local filesystem.
    """

    def __init__(self, name: str, local_path: Path) -> None:
        self.name = name
        self.local_path = local_path
        self._container_path: Optional[Path] = None

    def __repr__(self) -> str:
        """repr() implementation."""
        cls_name = self.__class__.__name__
        if self._container_path:
            return (
                f"<{cls_name} {self.name} from {self.local_path} "
                f"mounted at {self._container_path}>"
            )
        return f"<{cls_name} {self.name} from {self.local_path}>"

    def at(self, container_path: Path) -> "Artefact":
        """
        Get mounted artefact.

        Args:
            container_path: Path in the container.

        Returns:
            Mounted artefact instance.
        """
        a = Artefact(self.name, self.local_path)
        a._container_path = container_path
        return a

    def iter_mounts(self) -> Iterable[ArtefactMountPoint]:
        """
        Iterate over artefacts's mount points.

        Artefact must be mounted and obtained via `at()`.

        Raises:
            ValueError: on misconfigurations.
        """
        if not self._container_path:
            msg = "Artefact {self.name} is not mounted"
            raise ValueError(msg)
        if not self.local_path.exists():
            msg = f"Artefact {self.name}: file {self.local_path} is not exists"
            raise ValueError(msg)
        if self.local_path.is_file():
            yield ArtefactMountPoint(
                name=self.name,
                local_path=self.local_path,
                container_path=self._container_path,
            )
        elif self.local_path.is_dir():
            for p in self.local_path.rglob("*"):
                # @todo: Apply ignores
                rel = p.relative_to(self.local_path)
                # Calculate unique name
                h = sha256(str(rel).encode()).hexdigest()
                name = f"{self.name}-{h[:6]}"
                yield ArtefactMountPoint(
                    name=name,
                    local_path=p,
                    container_path=self._container_path / rel,
                )
        else:
            msg = f"Artefact {self.name}: {self.local_path} must be "
            "file or directory"
            raise ValueError(msg)

    def write(self, data: str) -> None:
        """
        Write data to artefact.

        Args:
            data: File contains.
        """
        write_file(self.local_path, data)

    def copy_from(self, src: Path) -> None:
        """
        Copy file from source file.

        Args:
            src: Source file path.
        """
        with open(src) as fp:
            self.write(fp.read())
