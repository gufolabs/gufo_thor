# ---------------------------------------------------------------------
# Gufo Thor: docker tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import List, Optional

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.docker import Docker


class MockDocker(Docker):
    def __init__(self) -> None:
        super().__init__()
        self.exec_cmd: Optional[List[str]] = None
        self._output: List[str] = []

    def feed_output(self, out: Optional[str] = None) -> None:
        self._output.append(out)

    def _execvp(self, cmd: List[str]) -> bool:
        self.exec_cmd = cmd
        return True

    def _capture_output(self, cmd: List[str]) -> str:
        if not self._output:
            self.die("no output")
        self.exec_cmd = cmd
        return self._output.pop(0)

    def _check_call(self, cmd: List[str]) -> bool:
        self.exec_cmd = cmd
        return True


def test_is_test() -> None:
    assert MockDocker()._is_test() is True


def test_die() -> None:
    docker = MockDocker()
    with pytest.raises(SystemExit):
        docker.die("test")


def test_execvp() -> None:
    docker = MockDocker()
    docker._execvp(["docker", "ps"])
    assert docker.exec_cmd == ["docker", "ps"]


DOCKER_CFG_NO_COMPOSE = """{
    "LoggingDriver": "json-file",
    "ServerVersion": "28.5.2",
    "ClientInfo": {
        "Plugins": []
    }
}"""
DOCKER_CFG_COMPOSE = """{
    "LoggingDriver": "json-file",
    "ServerVersion": "28.5.2",
    "ClientInfo": {
        "Plugins": [
            {
                "Name": "compose"
            }
        ]
    }
}
"""


def test_read_config_no_compose() -> None:
    docker = MockDocker()
    docker.feed_output(DOCKER_CFG_NO_COMPOSE)
    with pytest.raises(SystemExit):
        docker._read_config()


def test_read_config() -> None:
    docker = MockDocker()
    docker.feed_output(DOCKER_CFG_COMPOSE)
    cfg = docker._read_config()
    assert docker.exec_cmd == ["docker", "info", "--format", "{{ json .}}"]
    assert cfg.server_version == "28.5.2"
    assert cfg.logging_driver == "json-file"


COMPOSE_CONFIG = """{"name": "test1"}"""


def test_read_compose_config() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    cfg = docker._read_compose_config()
    assert docker.exec_cmd == ["docker", "compose", "config", "--format=json"]
    assert cfg.name == "test1"


def test_up() -> None:
    docker = MockDocker()
    docker.up()
    assert docker.exec_cmd == ["docker", "compose", "up", "-d"]


def test_stop() -> None:
    docker = MockDocker()
    docker.stop()
    assert docker.exec_cmd == ["docker", "compose", "stop"]


def test_down() -> None:
    docker = MockDocker()
    docker.down()
    assert docker.exec_cmd == ["docker", "compose", "down"]


def test_pull() -> None:
    docker = MockDocker()
    docker.pull()
    assert docker.exec_cmd == ["docker", "compose", "pull"]


def test_stats() -> None:
    docker = MockDocker()
    docker.stats()
    assert docker.exec_cmd == ["docker", "compose", "stats"]


def test_destroy() -> None:
    docker = MockDocker()
    docker.destroy()
    assert docker.exec_cmd == ["docker", "compose", "down", "--volumes"]
