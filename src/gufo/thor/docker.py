# ---------------------------------------------------------------------
# Gufo Thor: Docker utilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
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
from typing import Iterable, List, NoReturn, Optional

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


@dataclass
class ComposeConfig(object):
    """
    Effective docker compose config.

    Attriburtes:
        name: Project name
    """

    name: str


@dataclass
class ContainerStatus(object):
    """
    Container status.

    Attributes:
        name: Container name.
    """

    name: str


class Docker(object):
    """Docker wrapper."""

    @staticmethod
    def die(msg: str) -> NoReturn:
        """Show error message and die."""
        print(msg)
        sys.exit(1)

    def _is_test(self) -> bool:
        """
        Check if runned from pytest.

        Returns:
            True: Running in tests.
            False: Normal run.
        """
        return "pytest" in sys.modules

    @cached_property
    def _config(self) -> DockerConfig:
        """
        Docker configuration.

        Returns:
            DockerConfig.
        """
        if self._is_test():
            # Testing stub
            return DockerConfig(
                logging_driver="json-file",
                server_version="24.0.6",
            )
        return self._read_config()

    @cached_property
    def _compose_config(self) -> ComposeConfig:
        """
        Docker Compose configuration.

        Returns:
            ComposeConfig.
        """
        if self._is_test():
            return ComposeConfig(name="test")
        return self._read_compose_config()

    def _read_config(self) -> DockerConfig:
        """
        Read configuration from docker daemon.

        Returns:
            Parsed config.
        """
        logger.warning("Reading docker config")
        r = self._docker_output("info", "--format", "{{ json .}}")
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

    def _read_compose_config(self) -> ComposeConfig:
        """
        Read configuration from docker compose.

        Returns:
            Docker compose configuration.
        """
        r = self._compose_output("config", "--format=json")
        data = json.loads(r)
        return ComposeConfig(name=data["name"])

    @cached_property
    def logging_driver(self) -> str:
        """
        Get docker logging driver.

        Returns:
            logging driver name.
        """
        return self._config.logging_driver

    def _extend_docker_cmd(self, *args: str) -> List[str]:
        """
        Get docker commands.

        Returns:
            Prefixing commands for docker.
        """
        cmd = ["docker"]
        cmd.extend(args)
        return cmd

    def _extend_compose_cmd(self, *args: str) -> List[str]:
        """
        Get docker compose commands.

        Returns:
            Prefixing commands for compose.
        """
        cmd = ["docker", "compose"]
        cmd.extend(args)
        return cmd

    def _docker_exec(self, *args: str) -> bool:
        """
        Execute compose command.

        Replace current process with docker command.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        cmd = self._extend_docker_cmd(*args)
        return os.execvp(cmd[0], cmd)  # noqa: S606

    def _compose_exec(self, *args: str) -> bool:
        """
        Execute compose command.

        Replace current process with compose command.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        cmd = self._extend_compose_cmd(*args)
        return os.execvp(cmd[0], cmd)  # noqa: S606

    def _compose_command(self, *args: str) -> bool:
        """
        Run compose subcommand.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        cmd = self._extend_compose_cmd(*args)
        try:
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError:
            return False

    def _docker_output(self, *args: str) -> str:
        """
        Run docker command and capture output.

        Returns:
            captured output.
        """
        cmd = self._extend_docker_cmd(*args)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            self.die(f"Failed to run {' '.join(cmd)}")
        return r.stdout

    def _compose_output(self, *args: str) -> str:
        """
        Run compose command and capture output.

        Returns:
            captured output.
        """
        cmd = self._extend_compose_cmd(*args)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            self.die(f"Failed to run {' '.join(cmd)}")
        return r.stdout

    def up(self) -> bool:
        """
        Perform docker compose up -d.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Starting containers")
        return self._compose_exec("up", "-d")

    def stop(self) -> bool:
        """
        Perform docker compose stop.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Stopping containers")
        return self._compose_exec("stop")

    def logs(self, *args: str, _follow: bool = False) -> bool:
        """Show logs."""
        cmd = ["logs"]
        if _follow:
            cmd.append("-f")
        cmd.extend(args)
        return self._compose_exec(*cmd)

    def restart(self, *args: str) -> bool:
        """
        Perform services restart.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Restarting containers: %s", ", ".join(args))
        return self._compose_command(*("stop", *args)) and self._compose_exec(
            *("up", "-d", *args)
        )

    def shell(self) -> bool:
        """
        Run shell in container.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Running shell")
        return self._compose_exec("run", "--rm", "shell")

    def stats(self) -> bool:
        """
        Show container stats.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._compose_exec("stats")

    def destroy(self) -> bool:
        """
        Destroy installation.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        logger.warning("Destroying installation")
        return self._compose_exec("down", "--volumes")

    def pull(self) -> bool:
        """
        Pull containers.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._compose_exec("pull")

    def down(self, *args: str) -> bool:
        """
        Down services' containers.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        return self._compose_command(*("down", *args))

    def _iter_containers(self, *args: str) -> Iterable[ContainerStatus]:
        """
        Itereate containers with given properties.

        Returns:
            Yields ContainerStatus.
        """
        proj_label = self._get_project_label()
        cmd = [
            "ps",
            "-a",
            "--format=json",
            "--filter",
            f"label={proj_label}",
        ]
        for f in args:
            cmd += ["--filter", f]
        r = self._docker_output(*cmd)
        for item in r.split("\n"):
            v = item.strip()
            if v:
                data = json.loads(v)
                yield ContainerStatus(name=data["Names"])

    def _get_app_label(self) -> str:
        """Get app role label."""
        return "com.gufolabs.noc.role=app"

    def _get_project_label(self) -> str:
        """Get project label."""
        name = self._compose_config.name
        return f"com.docker.compose.project={name}"

    def pause(self, labels: Optional[Iterable[str]] = None) -> bool:
        """
        Pause all containers having given labels.

        Args:
            labels: Iterable of all required labels.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        app_label = self._get_app_label()
        flt = ["status=running", f"label={app_label}"]
        if labels is not None:
            flt.extend(f"label={f}" for f in labels)
        cmd = ["pause"] + [c.name for c in self._iter_containers(*flt)]
        return self._docker_exec(*cmd)

    def unpause(self, labels: Optional[Iterable[str]] = None) -> bool:
        """
        Resume all containers having given labels.

        Args:
            labels: Iterable of all required labels.

        Returns:
            True: if command executed successfully.
            False: otherwise.
        """
        app_label = self._get_app_label()
        flt = ["status=paused", f"label={app_label}"]
        if labels is not None:
            flt.extend(f"label={f}" for f in labels)
        cmd = ["unpause"] + [c.name for c in self._iter_containers(*flt)]
        return self._docker_exec(*cmd)


docker = Docker()
