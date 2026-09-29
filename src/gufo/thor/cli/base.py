# -----------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------
# Copyright (C) 2015-2026 Gufo Labs
# See LICENSE.md for details
# -----------------------------------------------------------------------
"""CLI entrypoint and shared Click context."""

from __future__ import annotations

# Python modules
import logging
import os
import sys
from functools import cached_property
from pathlib import Path
from typing import NoReturn, cast

# Third-party modules
import click
from gufo.loader import Loader

# Gufo Thor modules
from ..config import Config, get_sample
from ..error import CancelExecution
from ..log import logger
from ..targets.base import BaseTarget
from ..targets.base import loader as target_loader

NAME = "gufo-thor"
DEFAULT_HTTPS_PORT = 443


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

    @cached_property
    def config(self) -> Config:
        """Load the Thor configuration.

        Returns:
            Parsed Thor configuration.
        """
        return Config.from_file(Path("thor.yml"))

    @cached_property
    def target(self) -> BaseTarget:
        """Load the configured target, creating a default config if needed.

        Returns:
            Configured target instance.
        """
        path = "thor.yml"
        if not os.path.exists(path):
            logger.warning("Writing %s", path)
            with open(path, "w") as fp:
                fp.write(get_sample("simple"))
        return target_loader["compose"](self.config)

    def prepare(self) -> None:
        """Prepare services configuration."""
        self.target.prepare()

    def get_ui_url(self) -> str:
        """Build the NOC UI URL from the current configuration.

        Returns:
            HTTPS URL for the configured NOC web interface.
        """
        cfg = self.config
        parts = ["https://", cfg.expose.domain_name]
        if cfg.expose.web and cfg.expose.web.port != DEFAULT_HTTPS_PORT:
            parts.append(f":{cfg.expose.web.port}")
        parts.append("/")
        return "".join(parts)


pass_context = click.make_pass_decorator(Context, ensure=True)


class Entrypoint:
    """CLI entrypoint registered with the Gufo Loader.

    Args:
        fn: Click command associated with the entrypoint.
    """

    def __init__(self, fn: click.Command) -> None:
        self.fn = fn
        if fn.callback is None:
            message = "CLI entrypoint must have a command callback"
            raise TypeError(message)
        self.__module__ = fn.callback.__module__


def entrypoint(fn: click.Command) -> Entrypoint:
    """Register a Click command as a Gufo Thor CLI entrypoint.

    The decorator must be applied to a command created by
    `click.command`.

    Example::

        @entrypoint
        @click.command("version", short_help="Show Gufo Thor version")
        def version() -> None:
            ...

    Args:
        fn: Click command to register.

    Returns:
        Entrypoint wrapping the Click command.
    """
    return Entrypoint(fn)


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
        self, ctx: click.Context, name: str
    ) -> click.Command | None:
        """Get a CLI command by name.

        Args:
            ctx: Current CLI context.
            name: Command name.

        Returns:
            The command, or ``None`` if it is not found.
        """
        wrapper = loader.get(name.replace("-", "_"))
        if wrapper is None:
            return None
        return wrapper.fn

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
