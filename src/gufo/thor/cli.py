# ---------------------------------------------------------------------
# Gufo Thor: Command-line utility
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
`gufo-thor` command-line utility.

Attributes:
    NAME: Utility name
"""
# Python modules
import argparse
import logging
import os
import subprocess
import sys
from enum import IntEnum
from typing import Callable, List

# Gufo Thor modules
from . import __version__
from .error import CancelExecution
from .log import logger

NAME: str = "gufo-thor"


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
        subparsers.add_parser("up", help="Set up ana launch NOC")
        # down
        subparsers.add_parser("stop", help="Stop NOC")
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

    def handle_prepare(self: "Cli", _ns: argparse.Namespace) -> ExitCode:
        """Prepare NOC configuration."""
        from gufo.thor.config import Config
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
        with open(path) as fp:
            config = Config.from_yaml(fp.read())
        # Prepare target
        target = loader["compose"](config)
        target.prepare()
        return ExitCode.OK

    def handle_up(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Prepare NOC configuration and run NOC."""
        r = self.handle_prepare(ns)
        if r != ExitCode.OK:
            return r
        try:
            subprocess.check_call(["docker", "compose", "up", "-d"])
        except subprocess.CalledProcessError:
            return ExitCode.ERR
        return ExitCode.OK

    def handle_stop(self: "Cli", ns: argparse.Namespace) -> ExitCode:
        """Stop NOC."""
        try:
            subprocess.check_call(["docker", "compose", "stop"])
        except subprocess.CalledProcessError:
            return ExitCode.ERR
        return ExitCode.OK


def main() -> int:
    """Run `noc-thor` with command-line arguments."""
    return Cli().run(sys.argv[1:]).value
