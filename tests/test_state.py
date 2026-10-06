# ---------------------------------------------------------------------
# Gufo Thor: State tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import json
from pathlib import Path

# Third-party modules
import pytest

# Gufo Thor modules
import gufo.thor.state as state_module
from gufo.thor.state import State


def test_from_file_returns_empty_state_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    state = State.from_file(tmp_path / "missing.json")

    assert state == State()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({}, State()),
        (
            {"noc_version": "stable", "mongo_fcv": "7.0"},
            State(noc_version="stable", mongo_fcv="7.0"),
        ),
        (
            {"noc_version": None, "mongo_fcv": None},
            State(),
        ),
        (
            {"noc_version": "stable"},
            State(noc_version="stable"),
        ),
        (
            {"mongo_fcv": "7.0"},
            State(mongo_fcv="7.0"),
        ),
    ],
)
def test_from_file_loads_valid_state(
    tmp_path: Path, data: dict[str, str | None], expected: State
) -> None:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(data))

    state = State.from_file(path)

    assert state == expected


def test_from_file_rejects_broken_json(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("{")

    with pytest.raises(RuntimeError, match="Broken JSON") as exc_info:
        State.from_file(path)

    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


@pytest.mark.parametrize("data", [None, [], "state", 42])
def test_from_file_rejects_non_object_json(
    tmp_path: Path, data: object
) -> None:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(data))

    with pytest.raises(RuntimeError, match="Broken state"):
        State.from_file(path)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"noc_version": 1}, "Invalid noc_version"),
        ({"noc_version": False}, "Invalid noc_version"),
        ({"mongo_fcv": 1}, "Invalid mongo_fcv"),
        ({"mongo_fcv": False}, "Invalid mongo_fcv"),
    ],
)
def test_from_file_rejects_non_string_versions(
    tmp_path: Path, data: dict[str, object], message: str
) -> None:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(data))

    with pytest.raises(RuntimeError, match=message):
        State.from_file(path)


def test_save_writes_json_and_replaces_temporary_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "nested" / "state.json"
    monkeypatch.setattr(state_module, "STATE_FILE", state_file)
    state = State(noc_version="stable", mongo_fcv="7.0")

    state.save()

    assert json.loads(state_file.read_text()) == {
        "noc_version": "stable",
        "mongo_fcv": "7.0",
    }
    assert not state_file.with_suffix(".tmp").exists()


def test_save_writes_null_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "state.json"
    monkeypatch.setattr(state_module, "STATE_FILE", state_file)

    State().save()

    assert json.loads(state_file.read_text()) == {
        "noc_version": None,
        "mongo_fcv": None,
    }
