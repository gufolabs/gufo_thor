# ---------------------------------------------------------------------
# Gufo Thor: Mongo migration tests
# ---------------------------------------------------------------------
# Copyright (C) 2026, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from types import SimpleNamespace

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.migrate import mongo


@pytest.mark.parametrize(
    ("current", "target", "expected"),
    [
        (
            None,
            "9.0",
            ["5.0", "6.0", "7.0", "8.0", "8.2", "8.3", "9.0"],
        ),
        ("5.0", "8.2", ["6.0", "7.0", "8.0", "8.2"]),
        ("8.2", "9.0", ["8.3", "9.0"]),
        ("8.2", "8.2", []),
        ("9.0", "8.2", []),
        ("4.4", "7.0", ["5.0", "6.0", "7.0"]),
    ],
)
def test_iter_intermediate_fcv(
    monkeypatch: pytest.MonkeyPatch,
    current: str | None,
    target: str,
    expected: list[str],
) -> None:
    monkeypatch.setattr(mongo.state, "mongo_fcv", current)
    monkeypatch.setattr(
        mongo,
        "get_version_settings",
        lambda: SimpleNamespace(target_mongo_fcv=target),
    )

    assert list(mongo.iter_intermediate_fcv()) == expected
