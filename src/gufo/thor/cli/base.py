# -----------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------
# Copyright (C) 2015-2026 Gufo Labs
# See LICENSE.md for details
# -----------------------------------------------------------------------
"""CLI entrypoint and shared Click context."""

# Python modules
from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from functools import wraps
from typing import Any, NoReturn, cast

# Third-party modules
import click
from gufo.loader import Loader

# Gufo Thor modules
from ..error import CancelExecution
from ..log import logger
from ..targets.base import loader as target_loader

NAME = "gufo-thor"


class Context:
    """CLI execution context."""

    def __init__(self) -> None:
        self._verbose = False

    @property
    def verbose(self) -> bool:
        """Whether verbose output is enabled."""
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Enable or disable verbose output.

        Args:
            value: Whether to enable verbose logging.
        """
        self._verbose = value
        logger.setLevel(logging.DEBUG if value else logging.INFO)
        logging.basicConfig(
            level=logging.DEBUG if value else logging.INFO,
            format="%(asctime)s [%(name)s] %(message)s",
        )

    def print(self, msg: str) -> None:
        """Print a message to standard output.

        Args:
            msg: Message to print.
        """
        print(msg)

    def debug(self, msg: str) -> None:
        """Print a debug message to standard output if verbose mode is enabled.

        Args:
            msg: Message to print.
        """
        if self._verbose:
            print(msg)

    def die(self, msg: str | None = None) -> NoReturn:
        """Print an error message and terminate the process.

        Args:
            msg: Optional error message to print.
        """
        if msg:
            self.print(msg)
        sys.exit(1)


pass_context = click.make_pass_decorator(Context, ensure=True)


class Entrypoint:
    """CLI entrypoint registered with the Gufo Loader.

    Args:
        fn: Click command associated with the entrypoint.
    """

    def __init__(self, fn: click.Command) -> None:
        self.fn = fn
        if fn.callback is None:
            raise TypeError("CLI entrypoint must have a command callback")
        self.__module__ = fn.callback.__module__

    def get_command(self) -> click.Command:
        """Return the Click command associated with the entrypoint.

        Returns:
            Click command registered as the entrypoint.
        """
        return self.fn


def entrypoint(fn: click.Command) -> Entrypoint:
    """Register a Click command as a Gufo Thor CLI entrypoint.

    The decorator must be placed above all Click decorators::

        @entrypoint
        @click.command()
        def foo() -> None:
            ...

    Args:
        fn: Click command to register.

    Returns:
        Entrypoint instance.
    """
    return Entrypoint(fn)


def prepared(fn: Callable[..., object]) -> Callable[..., object]:
    """Mark a CLI callback as requiring configuration preparation.

    The decorator must be placed below all Click decorators::

        @entrypoint
        @click.command()
        @prepared
        def foo() -> None:
            ...

    This ensures that ``prepared`` is applied to the callback before
    Click creates the command.

    Args:
        fn: CLI callback to mark for configuration preparation.

    Returns:
        The unchanged CLI callback.
    """

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        target = target_loader["compose"]()
        target.prepare()
        return fn(*args, **kwargs)

    return wrapper


loader = Loader[Entrypoint](base="gufo.thor.cli", exclude="base")


class CLIDispatcher(click.Group):
    """Click command group that dynamically discovers CLI entrypoints."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List available CLI commands.

        Args:
            ctx: Current CLI context.

        Returns:
            Sorted list of available command names.
        """
        return sorted(name.replace("_", "-") for name in loader)

    def get_command(
        self, ctx: click.Context, cmd_name: str
    ) -> click.Command | None:
        """Get a CLI command by name.

        Args:
            ctx: Current CLI context.
            cmd_name: Command name.

        Returns:
            The command, or ``None`` if it is not found.
        """
        entrypoint = loader.get(cmd_name.replace("-", "_"))
        if entrypoint is None:
            return None
        return entrypoint.get_command()

    def invoke(self, ctx: click.Context) -> object:
        """Run the selected command and convert Thor cancellation to exit 1."""
        try:
            return cast(object, super().invoke(ctx))
        except CancelExecution:
            cast(Context, ctx.obj).die("Execution cancelled.")


@click.command(
    cls=CLIDispatcher,
    context_settings={"auto_envvar_prefix": "THOR"},
    help="Simple NOC management tool.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_context
def main(ctx: Context, verbose: bool) -> None:
    """Gufo Thor command-line interface.

    Args:
        ctx: Current CLI context.
        verbose: Enable verbose output.
    """
    ctx.verbose = verbose
