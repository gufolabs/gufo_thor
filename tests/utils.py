# ---------------------------------------------------------------------
# Gufo Thor: Test utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import sys
from contextlib import contextmanager
from functools import wraps
from typing import Any, Iterator

# Gufo Thor modules
from gufo.thor.validator import errors


@contextmanager
def suppress_is_test():
    """
    Make is_test return False.

    Usage:

    ``` python
    with suppress_is_test():
        assert is_test() is False
    ```
    """
    pt = sys.modules.pop("pytest", None)
    try:
        yield
    finally:
        if pt:
            sys.modules["pytest"] = pt


@contextmanager
def override_errors() -> Iterator[None]:
    """
    Temporary replace errors.

    Used for tests.
    """
    prev = errors.copy()
    try:
        yield None
    finally:
        errors.from_errors(prev)


def isolated_errors(fn):
    """
    Decorator to denote tests which can create errors.

    ```
    @isolated_errors
    def test_xxx()->None: ...
    ```
    """

    @wraps(fn)
    def inner(*args: Any, **kwargs: Any):
        with override_errors():
            return fn(*args, **kwargs)

    return inner
