# ---------------------------------------------------------------------
# Gufo Thor: State management
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Persistent state management for Gufo Thor installations.

Attributes:
    state: Current persistent state of the Gufo Thor installation.
"""

# Python modules
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Gufo Thor modules
from .utils import ensure_directory

STATE_FILE = Path("data", "state.json")


@dataclass
class State:
    """Persistent state of a Gufo Thor installation.

    Attributes:
        noc_version: NOC version associated with the current installation
            state.
        mongo_fcv: MongoDB Feature Compatibility Version (FCV) associated
            with the current installation state.
    """

    noc_version: str | None = None
    mongo_fcv: str | None = None

    @classmethod
    def from_file(cls, path: Path) -> State:
        """Load installation state from a file.

        If the file does not exist, an empty state is returned.

        Args:
            path: Path to the state file.

        Returns:
            Loaded installation state.

        Raises:
            RuntimeError: If the state file does not contain a JSON object.
        """
        state = cls()
        if not path.exists():
            return state
        with path.open() as fp:
            try:
                data = json.load(fp)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Broken JSON: {e}") from e
        if not isinstance(data, dict):
            raise RuntimeError("Broken state")
        if (noc_version := data.get("noc_version")) is not None:
            if not isinstance(noc_version, str):
                raise RuntimeError("Invalid noc_version")
            state.noc_version = noc_version
        if (mongo_fcv := data.get("mongo_fcv")) is not None:
            if not isinstance(mongo_fcv, str):
                raise RuntimeError("Invalid mongo_fcv")
            state.mongo_fcv = mongo_fcv
        return state

    def save(self) -> None:
        """Save the current installation state to the state file.

        The state is written to a temporary file and atomically moved to
        the target path to avoid leaving a partially written state file.
        """
        ensure_directory(STATE_FILE.parent)
        tmp = STATE_FILE.with_suffix(".tmp")
        with tmp.open("w") as fp:
            json.dump(
                {"noc_version": self.noc_version, "mongo_fcv": self.mongo_fcv},
                fp,
                indent=2,
            )
        tmp.replace(STATE_FILE)


state = State.from_file(STATE_FILE)
