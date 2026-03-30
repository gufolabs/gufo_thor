# ---------------------------------------------------------------------
# Gufo Thor: docker tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import List, Tuple

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.docker import Docker


class MockDocker(Docker):
    def __init__(self) -> None:
        super().__init__()
        self.exec_cmd: List[Tuple[str, ...]] = []
        self._output: List[str] = []

    def feed_output(self, out: str) -> None:
        self._output.append(out)

    def _log_cmd(self, cmd: List[str]) -> None:
        self.exec_cmd.append(tuple(cmd))

    def _execvp(self, cmd: List[str]) -> bool:
        self._log_cmd(cmd)
        return True

    def _capture_output(self, cmd: List[str]) -> str:
        if not self._output:
            self.die("no output")
        self._log_cmd(cmd)
        return self._output.pop(0)

    def _check_call(self, cmd: List[str]) -> bool:
        self._log_cmd(cmd)
        return True


def test_die() -> None:
    docker = MockDocker()
    with pytest.raises(SystemExit):
        docker.die("test")


def test_execvp() -> None:
    docker = MockDocker()
    docker._execvp(["docker", "ps"])
    assert docker.exec_cmd == [("docker", "ps")]


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
    assert docker.exec_cmd == [("docker", "info", "--format", "{{ json .}}")]
    assert cfg.server_version == "28.5.2"
    assert cfg.logging_driver == "json-file"


COMPOSE_CONFIG = """{"name": "test1"}"""


def test_read_compose_config() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    cfg = docker._read_compose_config()
    assert docker.exec_cmd == [
        ("docker", "compose", "config", "--format=json")
    ]
    assert cfg.name == "test1"


def test_up() -> None:
    docker = MockDocker()
    docker.up()
    assert docker.exec_cmd == [("docker", "compose", "up", "-d")]


def test_stop() -> None:
    docker = MockDocker()
    docker.stop()
    assert docker.exec_cmd == [("docker", "compose", "stop")]


def test_down() -> None:
    docker = MockDocker()
    docker.down()
    assert docker.exec_cmd == [("docker", "compose", "down")]


def test_pull() -> None:
    docker = MockDocker()
    docker.pull()
    assert docker.exec_cmd == [("docker", "compose", "pull")]


def test_stats() -> None:
    docker = MockDocker()
    docker.stats()
    assert docker.exec_cmd == [("docker", "compose", "stats")]


def test_destroy() -> None:
    docker = MockDocker()
    docker.destroy()
    assert docker.exec_cmd == [("docker", "compose", "down", "--volumes")]


DOCKER_PS = """{"Names": "test1-web-1"}
{"Names": "test1-web-2"}"""


def test_pause() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    docker.feed_output(DOCKER_PS)
    docker.pause()
    assert docker.exec_cmd == [
        ("docker", "compose", "config", "--format=json"),
        (
            "docker",
            "ps",
            "-a",
            "--format=json",
            "--filter",
            "label=com.docker.compose.project=test1",
            "--filter",
            "status=running",
            "--filter",
            "label=com.gufolabs.noc.role=app",
        ),
        ("docker", "pause", "test1-web-1", "test1-web-2"),
    ]


def test_pause_label() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    docker.feed_output(DOCKER_PS)
    docker.pause(["com.gufolabs.noc.test=1"])
    assert docker.exec_cmd == [
        ("docker", "compose", "config", "--format=json"),
        (
            "docker",
            "ps",
            "-a",
            "--format=json",
            "--filter",
            "label=com.docker.compose.project=test1",
            "--filter",
            "status=running",
            "--filter",
            "label=com.gufolabs.noc.role=app",
            "--filter",
            "label=com.gufolabs.noc.test=1",
        ),
        ("docker", "pause", "test1-web-1", "test1-web-2"),
    ]


def test_unpause() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    docker.feed_output(DOCKER_PS)
    docker.unpause()
    assert docker.exec_cmd == [
        ("docker", "compose", "config", "--format=json"),
        (
            "docker",
            "ps",
            "-a",
            "--format=json",
            "--filter",
            "label=com.docker.compose.project=test1",
            "--filter",
            "status=paused",
            "--filter",
            "label=com.gufolabs.noc.role=app",
        ),
        ("docker", "unpause", "test1-web-1", "test1-web-2"),
    ]


def test_unpause_label() -> None:
    docker = MockDocker()
    docker.feed_output(COMPOSE_CONFIG)
    docker.feed_output(DOCKER_PS)
    docker.unpause(["com.gufolabs.noc.test=1"])
    assert docker.exec_cmd == [
        ("docker", "compose", "config", "--format=json"),
        (
            "docker",
            "ps",
            "-a",
            "--format=json",
            "--filter",
            "label=com.docker.compose.project=test1",
            "--filter",
            "status=paused",
            "--filter",
            "label=com.gufolabs.noc.role=app",
            "--filter",
            "label=com.gufolabs.noc.test=1",
        ),
        ("docker", "unpause", "test1-web-1", "test1-web-2"),
    ]


@pytest.mark.parametrize(
    ("args", "follow", "expected"),
    [
        ("", False, [("docker", "compose", "logs")]),
        (("web",), False, [("docker", "compose", "logs", "web")]),
        (("web",), True, [("docker", "compose", "logs", "-f", "web")]),
    ],
)
def test_logs(
    args: Tuple[str, ...], follow: bool, expected: List[Tuple[str]]
) -> None:
    docker = MockDocker()
    docker.logs(*args, _follow=follow)
    assert docker.exec_cmd == expected


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (
            (),
            [
                ("docker", "compose", "stop"),
                ("docker", "compose", "up", "-d"),
            ],
        ),
        (
            ("web",),
            [
                ("docker", "compose", "stop", "web"),
                ("docker", "compose", "up", "-d", "web"),
            ],
        ),
    ],
)
def test_restart(
    args: Tuple[str, ...], expected: List[Tuple[str, ...]]
) -> None:
    docker = MockDocker()
    docker.restart(*args)
    assert docker.exec_cmd == expected


def test_check_call() -> None:
    docker = Docker()
    docker._check_call(["ls", "-l"])


@pytest.mark.parametrize(
    ("cmd", "expected"),
    [(["ls", "-l"], True), (["nonexistentcommand"], False)],
)
def test_check_call_fail(cmd: List[str], expected: bool) -> None:
    docker = Docker()
    r = docker._check_call(cmd)
    assert r is expected
