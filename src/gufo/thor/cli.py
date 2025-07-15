# ---------------------------------------------------------------------
# Gufo Thor: Command-line utility
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
`gufo-thor` command-line utility.

Attributes:
    NAME: Utility name
"""

# Python modules
import argparse
import contextlib
import logging
import os
import subprocess
import sys
from enum import IntEnum
from functools import cached_property
from pathlib import Path
from typing import Callable, List, NoReturn, Optional

# Gufo Thor modules
from . import __version__
from .config import Config
from .docker import docker
from .error import CancelExecution
from .log import logger
from .targets.base import BaseTarget

NAME: str = "gufo-thor"
DEFAULT_HTTPS_PORT = 443


class ExitCode(IntEnum):
    """
    Cli exit codes.

    Attributes:
        OK: Successful exit
    """

    OK = 0
    ERR = 1


class Cli(object):
    """`gufo-thor` CLI utility class."""

    @staticmethod
    def die(msg: Optional[str] = None) -> NoReturn:
        """Die with message."""
        if msg:
            print(msg)
        sys.exit(1)

    def run(self: "Cli", args: List[str]) -> ExitCode:
        """
        Parse command-line arguments and run appropriate command.

        Args:
            args: List of command-line arguments
        Returns:
            ExitCode
        """
        # Prepare command-line parser
        parser = argparse.ArgumentParser(
            prog=NAME, description="Simple NOC management tool"
        )
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # version
        subparsers.add_parser("version", help=f"Show {NAME} version")
        # sample-config
        sample_config_parser = subparsers.add_parser(
            "sample-config", help="Generate sample config"
        )
        sample_config_parser.add_argument(
            "-t",
            "--template",
            default="simple",
            help="Select sample config template",
        )
        # prepare
        subparsers.add_parser("prepare", help="Prepare services configuration")
        # up
        up_parser = subparsers.add_parser("up", help="Set up and launch NOC")
        up_parser.add_argument(
            "--migrate", action="store_true", help="Run migrations"
        )
        up_parser.add_argument(
            "--no-migrate", action="store_true", help="Skip migrations on run"
        )
        # down
        subparsers.add_parser("stop", help="Stop NOC")
        # logs
        logs_parser = subparsers.add_parser("logs", help="Show process' logs")
        logs_parser.add_argument(
            "-f", "--follow", action="store_true", help="Follow logs"
        )
        logs_parser.add_argument(
            "services", nargs=argparse.ONE_OR_MORE, help="Service names"
        )
        # shell
        subparsers.add_parser("shell", help="Run shell")
        # stats
        subparsers.add_parser("stats", help="Show container stats")
        # restart
        restart_parser = subparsers.add_parser(
            "restart", help="Restart service"
        )
        restart_parser.add_argument(
            "services", nargs=argparse.ONE_OR_MORE, help="Service names"
        )
        # backup
        backup_parser = subparsers.add_parser(
            "backup", help="Backup databases"
        )
        backup_parser.add_argument(
            "list", action="store_true", help="List backups"
        )
        backup_parser.add_argument(
            "postgres", action="store_true", help="Backup postgres database"
        )
        backup_parser.add_argument(
            "mongo", action="store_true", help="Backup mongo database"
        )
        # restore
        subparsers.add_parser("restore", help="Restore database")
        # destroy
        destroy_parser = subparsers.add_parser(
            "destroy", help="Destroy installation and free resources"
        )
        destroy_parser.add_argument(
            "--yes",
            action="store_true",
            help="Execute without explicit confirmation",
        )
        # upgrade
        subparsers.add_parser("upgrade", help="Update NOC")
        # Parse arguments
        ns = parser.parse_args(args)
        # Set up logging
        self.setup_logging()
        # Process command
        handler = self.get_handler(ns.cmd)
        try:
            return handler(ns)
        except CancelExecution:
            return ExitCode.ERR

    def get_handler(
        self: "Cli", name: str
    ) -> Callable[[argparse.Namespace], ExitCode]:
        """
        Get handler for command.

        Args:
            name: Command name

        Returns:
            Callable, accepting Namespace and returning exit code
        """
        h: Callable[[argparse.Namespace], ExitCode] = getattr(
            self, f"handle_{name.replace('-', '_')}"
        )
        return h

    def setup_logging(self: "Cli") -> None:
        """Setup logger."""
        logger.setLevel(logging.INFO)

    def handle_version(self: "Cli", _ns: argparse.Namespace) -> ExitCode:
        """
        Print Gufo Thor version.

        Args:
            _ns: Options namespace, ignored.

        Returns:
            Exit code.
        """
        print(f"{NAME} {__version__}")
        return ExitCode.OK

    def handle_sample_config(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Generate sample config."""
        from gufo.thor.config import get_sample

        sample = get_sample(ns.template)
        path = "thor.yml"
        if os.path.exists(path):
            logger.error("%s is already exists", path)
            return ExitCode.ERR
        logger.warning("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(sample)
        return ExitCode.OK

    @cached_property
    def config(self: "Cli") -> Config:
        """
        Get config.

        Returns:
            Config instance.
        """
        path = Path("thor.yml")
        return Config.from_file(path)

    @cached_property
    def target(self: "Cli") -> BaseTarget:
        """
        Get target.

        Returns:
            Target instance.
        """
        from gufo.thor.targets.base import loader

        # Read config
        path = "thor.yml"
        if not os.path.exists(path):
            from gufo.thor.config import get_sample

            # Generate config
            sample = get_sample("simple")
            logger.warning("Writing %s", path)
            with open(path, "w") as fp:
                fp.write(sample)
        # Get target
        return loader["compose"](self.config)

    def handle_prepare(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Prepare NOC configuration."""
        self.target.prepare()
        return ExitCode.OK

    def _get_ui_url(self: "Cli") -> str:
        """
        Get user interface url.

        Returns:
            URL.
        """
        cfg = self.config
        parts = ["https://", cfg.expose.domain_name]
        if cfg.expose.web and cfg.expose.web.port != DEFAULT_HTTPS_PORT:
            parts.append(f":{cfg.expose.web.port}")
        parts.append("/")
        return "".join(parts)

    def handle_up(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Prepare NOC configuration and run NOC."""
        # Migrate status
        if ns.migrate:
            self.config.noc.migrate = True
        elif ns.no_migrate:
            self.config.noc.migrate = False
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.up():
            return ExitCode.ERR
        # Open UI
        url = self._get_ui_url()
        logger.warning("To access NOC user interface open %s", url)
        if self.config.expose.open_browser:
            logger.warning("Starting browser")
            with contextlib.suppress(subprocess.CalledProcessError):
                try:
                    subprocess.check_output(["open", url])
                except FileNotFoundError:
                    logger.warning(
                        "Cannot start browser. Command `open` is not found"
                    )
        return ExitCode.OK

    def handle_stop(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Stop NOC."""
        if not docker.stop():
            return ExitCode.ERR
        return ExitCode.OK

    def handle_shell(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Run shell."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.shell():
            return ExitCode.ERR
        return ExitCode.OK

    def handle_restart(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Restart services."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.restart(*ns.services):
            return ExitCode.ERR
        return ExitCode.OK

    def handle_stats(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Show stats."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.stats():
            return ExitCode.ERR
        return ExitCode.OK

    def handle_logs(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Show logs."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.logs(*ns.services, _follow=ns.follow):
            return ExitCode.ERR
        return ExitCode.OK

    def handle_destroy(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Destroy installation."""
        if not self.confirm(
            "Destroy installation? All data will be lost!", ns=ns
        ):
            logger.warning("Cancelled!")
            return ExitCode.ERR
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        if not docker.destroy():
            return ExitCode.ERR
        return ExitCode.OK

    def handle_upgrade(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Upgrade NOC."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        logger.warning("Cleaning containers")
        docker.down()
        logger.warning("Pulling new images")
        if not docker.pull():
            return ExitCode.ERR
        logger.warning("Running migrate")
        return ExitCode.OK

    def confirm(self: "Cli", question: str, ns: argparse.Namespace) -> bool:
        """Ask for confirmation."""
        if ns.yes:
            return True
        while True:
            r = input(f"{question} [y/N]: ").strip().lower()
            if not r or r == "n":
                return False
            if r == "y":
                return True
            logger.warning("Please respond `y` or `n`")


def main() -> int:
    """Run `noc-thor` with command-line arguments."""
    return Cli().run(sys.argv[1:]).value
