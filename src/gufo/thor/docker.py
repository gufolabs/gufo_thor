# ---------------------------------------------------------------------
# Gufo Thor: Docker utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

"""
Docker utilities.

Attributes:
    docker: Docker singleton.
"""

# Python modules
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from functools import cached_property
from typing import NoReturn

# Gufo Thor modules
from .log import logger


@dataclass
class DockerConfig(object):
    """
    Docker daemon configuration.

    Attributes:
        logging_driver: Current logging driver.
        server_version: Current docker server version.
    """

    logging_driver: str
    server_version: str


class Docker(object):
    """Docker wrapper."""

    @staticmethod
    def die(msg: str) -> NoReturn:
        """Show error message and die."""
        print(msg)
        sys.exit(1)

    @cached_property
    def _config(self: "Docker") -> DockerConfig:
        """
        Docker configuration.

        Returns:
            DockerConfig.
        """
        if "pytest" in sys.modules:
            # Testing stub
            return DockerConfig(
                logging_driver="json-file",
                server_version="24.0.6",
            )
        return self._read_config()

    def _read_config(self: "Docker") -> DockerConfig:
        """
        Read configuration from docker daemon.

        Returns:
            Parsed config.
        """
        logger.warning("Reading docker config")
        try:
            r = subprocess.check_output(
                ["docker", "info", "--format", "{{ json . }}"]
            )
        except subprocess.CalledProcessError:
            self.die("Docker is not running. Please run docker.")
        data = json.loads(r)
        # Check plugins
        client_plugins = data["ClientInfo"]["Plugins"]
        has_compose = any(
            True for d in client_plugins if d["Name"] == "compose"
        )
        cfg = DockerConfig(
            logging_driver=data["LoggingDriver"],
            server_version=data["ServerVersion"],
        )
        logger.warning("Docker %s found", cfg.server_version)
        if not has_compose:
            self.die("Compose plugin is not installed")
        return cfg

    @cached_property
    def logging_driver(self: "Docker") -> str:
        """
        Get docker logging driver.

        Returns:
            logging driver name.
        """
        return self._config.logging_driver

    def _commpose_command(
        self: "Docker", *args: str, _exec: bool = False
    ) -> bool:
        """
        Run compose subcommand.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        cmd = ["docker", "compose"]
        cmd.extend(args)
        if _exec:
            return os.execvp(cmd[0], cmd)  # noqa: S606
        try:
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError:
            return False

    def up(self: "Docker") -> bool:
        """
        Perform docker compose up -d.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Starting containers")
        return self._commpose_command("up", "-d", _exec=True)

    def stop(self: "Docker") -> bool:
        """
        Perform docker compose stop.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Stopping containers")
        return self._commpose_command("stop", _exec=True)

    def logs(self: "Docker", *args: str, _follow: bool = False) -> bool:
        """Show logs."""
        cmd = ["logs"]
        if _follow:
            cmd.append("-f")
        cmd.extend(args)
        return self._commpose_command(*cmd, _exec=True)

    def restart(self: "Docker", *args: str) -> bool:
        """
        Perform services restart.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Restarting containers: %s", ", ".join(args))
        return self._commpose_command(
            *("stop", *args)
        ) and self._commpose_command(*("up", "-d", *args), _exec=True)

    def shell(self: "Docker") -> bool:
        """
        Run shell in container.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Running shell")
        return self._commpose_command("run", "--rm", "shell", _exec=True)

    def stats(self: "Docker") -> bool:
        """
        Show container stats.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._commpose_command("stats", _exec=True)

    def destroy(self: "Docker") -> bool:
        """
        Destroy installation.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Destroying installation")
        return self._commpose_command("down", "--volumes", _exec=True)

    def pull(self: "Docker") -> bool:
        """
        Pull containers.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._commpose_command("pull", _exec=True)

    def down(self: "Docker", *args: str) -> bool:
        """
        Down services' containers.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._commpose_command(*("down", *args))


docker = Docker()
