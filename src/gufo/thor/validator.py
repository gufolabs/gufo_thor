# ---------------------------------------------------------------------
# Gufo Thor: Validation framework
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Config validator primitives."""

# Python modules
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    NoReturn,
    Optional,
    Union,
    overload,
)

# Gufo Thor modules
from .ip import IPv4Address, IPv4Prefix


@dataclass
class ErrorPoint(object):
    """Error position."""

    message: str
    path: Optional[List[str]] = None

    def __str__(self) -> str:
        """str() implementation."""
        if self.path:
            return f"{'.'.join(self.path)}: {self.message}"
        return self.message


class ErrorContext(object):
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
        self._errors: List[ErrorPoint] = []
        self._paths: List[List[str]] = []

    def check(self) -> None:
        """
        Check there is no errors.

        Die with message if they are.
        """
        if self._errors:
            self.die()

    def error(self, message: str, /, path: Optional[List[str]] = None) -> None:
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
    def context(self, path: Union[str, List[str]]) -> Iterator[None]:
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

    def die(self, msg: Optional[str] = None) -> NoReturn:
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
        sys.exit(1)


# Singletone
errors = ErrorContext()


@overload
def as_str(
    data: Dict[str, Any], name: str, /, required: Literal[True]
) -> str: ...


@overload
def as_str(
    data: Dict[str, Any], name: str, /, required: Literal[False]
) -> Optional[str]: ...


def as_str(
    data: Dict[str, Any], name: str, /, required: bool = True
) -> Optional[str]:
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
        else:
            return None
    return str(v)


@overload
def as_int(
    data: Dict[str, Any], name: str, /, required: Literal[True]
) -> int: ...


@overload
def as_int(
    data: Dict[str, Any], name: str, /, required: Literal[False]
) -> Optional[int]: ...


def as_int(
    data: Dict[str, Any], name: str, /, required: bool = True
) -> Optional[int]:
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
        else:
            return None
    try:
        return int(v)
    except ValueError:
        with errors.context(name):
            errors.error("invalid integer")
            return 0


@overload
def as_ipv4(
    data: Dict[str, Any], name: str, /, required: Literal[True]
) -> IPv4Address: ...


@overload
def as_ipv4(
    data: Dict[str, Any], name: str, /, required: Literal[False]
) -> Optional[IPv4Address]: ...


def as_ipv4(
    data: Dict[str, Any], name: str, /, required: bool = True
) -> Optional[IPv4Address]:
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
    data: Dict[str, Any], name: str, /, required: Literal[True]
) -> IPv4Prefix: ...


@overload
def as_ipv4_prefix(
    data: Dict[str, Any], name: str, /, required: Literal[False]
) -> Optional[IPv4Prefix]: ...


def as_ipv4_prefix(
    data: Dict[str, Any], name: str, /, required: bool = True
) -> Optional[IPv4Prefix]:
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
