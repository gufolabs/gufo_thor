# ---------------------------------------------------------------------
# Gufo Thor: Validation framework
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Config validator primitives."""

# Python modules
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Literal, NoReturn, overload

# Gufo Thor modules
from .ip import IPv4Address, IPv4Prefix
from .utils import is_test


@dataclass
class ErrorPoint:
    """Error position."""

    message: str
    path: list[str] | None = None

    def __str__(self) -> str:
        """str() implementation."""
        if self.path:
            return f"{'.'.join(self.path)}: {self.message}"
        return self.message


class ErrorContext:
    """
    Error reporting context.

    Usually used as singletone.

    Example:
        ``` python
        with errors.context("section1"):
            ...
            with errors.context("subsection1"):
                ...
                errors.error("There is error")
        ```
    """

    def __init__(self) -> None:
        self._errors: list[ErrorPoint] = []
        self._paths: list[list[str]] = []

    def copy(self) -> "ErrorContext":
        """Create copy of ErrorContext."""
        r = ErrorContext()
        r._errors = self._errors.copy()
        r._paths = self._paths.copy()
        return r

    def from_errors(self, ctx: "ErrorContext") -> None:
        """Restore state from error context."""
        self._errors = ctx._errors.copy()
        self._paths = ctx._paths.copy()

    def has_errors(self) -> bool:
        """
        Check if errors are present.

        Returns:
            True: If there is errors.
            False: Otherwise
        """
        return bool(self._errors)

    def check(self) -> None:
        """
        Check there is no errors.

        Die with message if they are.
        """
        if self.has_errors():
            self.die()

    def error(self, message: str, /, path: list[str] | None = None) -> None:
        """
        Register error.

        Errors registered in current context, if `path` is not set,
        otherwise - in path directly.

        Args:
            message: Error message.
            path: Optional path to override current context.
        """
        if path is None and self._paths:
            path = self._paths[-1]
        self._errors.append(ErrorPoint(message=message, path=path))

    @contextmanager
    def context(self, path: str | list[str]) -> Iterator[None]:
        """
        Set current context.

        Path is appended to existing context.
        `..` can be used to set level up.

        Examples:
            ``` python
            with errors.context("xxx"):
                ...
            ```
        """
        if isinstance(path, str):
            path = [path]
        if self._paths:
            path = self._paths[-1] + path
        # Process `..`
        while path and ".." in path:
            idx = path.index("..")
            if idx > 0:
                path.pop(idx - 1)
                path.pop(idx - 1)
            else:
                path.pop(0)
        self._paths.append(path)
        yield
        self._paths.pop(-1)

    def die(self, msg: str | None = None) -> NoReturn:
        """
        Dump errors and stop execution.

        Args:
            msg: Optional error message to add.
        """
        if msg:
            self.error(msg)
        print("Config errors found:")
        for err in self._errors:
            print(str(err))
        if is_test():
            raise RuntimeError("\n".join(str(x) for x in self._errors))
        sys.exit(1)  # pragma: no cover


# Singletone
errors = ErrorContext()


@overload
def as_str(
    data: dict[str, Any], name: str, /, required: Literal[True]
) -> str: ...


@overload
def as_str(
    data: dict[str, Any], name: str, /, required: Literal[False]
) -> str | None: ...


def as_str(
    data: dict[str, Any], name: str, /, required: bool = True
) -> str | None:
    """
    Extract string from dict.

    Args:
        data: Data dict.
        name: parameter name.
        required: Set or non set error if key is missed.
    """
    v = data.get(name)
    if v is None:
        if required:
            with errors.context(name):
                errors.error("must be set")
                return ""
        return None
    return str(v)


@overload
def as_int(
    data: dict[str, Any], name: str, /, required: Literal[True]
) -> int: ...


@overload
def as_int(
    data: dict[str, Any], name: str, /, required: Literal[False]
) -> int | None: ...


def as_int(
    data: dict[str, Any], name: str, /, required: bool = True
) -> int | None:
    """
    Extract int from dict.

    Args:
        data: Data dict.
        name: parameter name.
        required: Set or non set error if key is missed.

    Returns:
        integer value, if possible.
    """
    v = data.get(name)
    if v is None:
        if required:
            with errors.context(name):
                errors.error("must be set")
                return 0
        return None
    try:
        return int(v)
    except ValueError:
        with errors.context(name):
            errors.error("invalid integer")
            return 0


@overload
def as_ipv4(
    data: dict[str, Any], name: str, /, required: Literal[True]
) -> IPv4Address: ...


@overload
def as_ipv4(
    data: dict[str, Any], name: str, /, required: Literal[False]
) -> IPv4Address | None: ...


def as_ipv4(
    data: dict[str, Any], name: str, /, required: bool = True
) -> IPv4Address | None:
    """
    Extract IPv4Address from dict.

    Args:
        data: Data dict.
        name: parameter name.
        required: Set or non set error if key is missed.

    Returns:
        integer value, if possible.
    """
    v = data.get(name)
    if v is None:
        if required:
            with errors.context(name):
                errors.error("must be set")
                return IPv4Address.default()
        return None
    try:
        return IPv4Address(v)
    except ValueError:
        with errors.context(name):
            errors.error("invalid address")
            return IPv4Address.default()


@overload
def as_ipv4_prefix(
    data: dict[str, Any], name: str, /, required: Literal[True]
) -> IPv4Prefix: ...


@overload
def as_ipv4_prefix(
    data: dict[str, Any], name: str, /, required: Literal[False]
) -> IPv4Prefix | None: ...


def as_ipv4_prefix(
    data: dict[str, Any], name: str, /, required: bool = True
) -> IPv4Prefix | None:
    """
    Extract IPv4Prefix from dict.

    Args:
        data: Data dict.
        name: parameter name.
        required: Set or non set error if key is missed.

    Returns:
        integer value, if possible.
    """
    v = data.get(name)
    if v is None:
        if required:
            with errors.context(name):
                errors.error("must be set")
                return IPv4Prefix.default()
        return None
    try:
        return IPv4Prefix(v)
    except ValueError:
        with errors.context(name):
            errors.error("invalid prefix")
            return IPv4Prefix.default()
