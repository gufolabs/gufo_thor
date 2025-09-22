# ---------------------------------------------------------------------
# Gufo Thor: Validator tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Dict, List, Optional, Union

# Third party modules
import pytest

# Gufo Thor modules
from gufo.thor.validator import (
    ErrorContext,
    ErrorPoint,
    as_str,
    errors,
    override_errors,
)


def test_die() -> None:
    ctx = ErrorContext()
    with pytest.raises(RuntimeError) as exc_info:
        ctx.die("test")
    assert exc_info.value.args[0] == "test"


@pytest.mark.parametrize(
    ("point", "expected"),
    [
        (ErrorPoint("test"), "test"),
        (ErrorPoint("test", ["x"]), "x: test"),
        (ErrorPoint("test", ["x", "y"]), "x.y: test"),
        (ErrorPoint("test", ["x", "y", "z"]), "x.y.z: test"),
    ],
)
def test_error_point_str(point: ErrorPoint, expected: str) -> None:
    assert str(point) == expected


@pytest.mark.parametrize(
    ("msg", "path", "expected"),
    [
        ("test", None, "test"),
        ("test", ["x"], "x: test"),
        ("test", ["x", "y"], "x.y: test"),
        ("test", ["x", "y", "z"], "x.y.z: test"),
    ],
)
def test_error_context_die(
    msg: str, path: Optional[List[str]], expected: str
) -> None:
    ctx = ErrorContext()
    ctx.error(msg, path=path)
    with pytest.raises(RuntimeError) as exc_info:
        ctx.check()
    assert exc_info.value.args[0] == expected


@pytest.mark.parametrize(
    ("msg", "path", "expected"),
    [
        ("test", ["x"], "x: test"),
        ("test", ["x", "y"], "x.y: test"),
        ("test", ["x", "y", "z"], "x.y.z: test"),
    ],
)
def test_error_context_with_die(
    msg: str, path: Union[str, List[str]], expected: str
) -> None:
    ctx = ErrorContext()
    with ctx.context(path):
        ctx.error(msg)
    with pytest.raises(RuntimeError) as exc_info:
        ctx.check()
    assert exc_info.value.args[0] == expected


def test_error_level_up1() -> None:
    ctx = ErrorContext()
    with (
        ctx.context("a"),
        ctx.context("b"),
        ctx.context(".."),
        ctx.context("c"),
    ):
        ctx.error("test")
    with pytest.raises(RuntimeError) as exc_info:
        ctx.check()
    assert exc_info.value.args[0] == "a.c: test"


def test_error_level_up2() -> None:
    ctx = ErrorContext()
    with (
        ctx.context(".."),
        ctx.context("a"),
        ctx.context("b"),
        ctx.context("c"),
    ):
        ctx.error("test")
    with pytest.raises(RuntimeError) as exc_info:
        ctx.check()
    assert exc_info.value.args[0] == "a.b.c: test"


@pytest.mark.parametrize(
    ("data", "name", "expected"), [({"x": 1}, "x", "1"), ({"x": 1}, "y", None)]
)
def test_as_str(
    data: Dict[str, Any], name: str, expected: Optional[str]
) -> None:
    r = as_str(data, name, required=False)
    if expected is None:
        assert r is None
    else:
        assert r == expected


def test_as_str_required() -> None:
    with override_errors():
        as_str({}, "x", required=True)
        with pytest.raises(RuntimeError) as exc_info:
            errors.check()
        assert exc_info.value.args[0] == "x: must be set"


def test_override_errors() -> None:
    assert not errors.has_errors()
    with override_errors():
        errors.error("test")
        assert errors.has_errors()
    assert not errors.has_errors()
