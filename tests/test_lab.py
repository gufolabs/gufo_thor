# ---------------------------------------------------------------------
# Gufo Thor: Lab tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.config import Config, LabConfig, LabNodeConfig
from gufo.thor.labs.base import BaseLab, DockerConsoleArgs

from .utils import isolated_errors


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        (
            {"type": "vyos15"},
            DockerConsoleArgs(args=["-u", "vyos"], argv=["/bin/vbash"]),
        ),
        (
            {"type": "vyos15", "users": [{"user": "vy1", "password": "pass"}]},
            DockerConsoleArgs(args=["-u", "vy1"], argv=["/bin/vbash"]),
        ),
    ],
)
def test_vyos15_docker_console_args(
    cfg: Dict[str, Any], expected: DockerConsoleArgs
) -> None:
    node_cfg = LabNodeConfig.from_dict("test", cfg)
    lab_cfg = LabConfig(
        name="test", nodes={"test": node_cfg}, links=[], pool="test"
    )
    node = BaseLab.get(node_cfg.type)
    cargs = node.get_docker_console_args(Config.default(), lab_cfg, node_cfg)
    assert cargs
    assert cargs == expected


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({}, "ghcr.io/gufolabs/vyos15:latest"),
        ({"version": "nightly"}, "ghcr.io/gufolabs/vyos15:nightly"),
    ],
)
@isolated_errors
def test_lab_compose_image(cfg: Dict[str, str], expected: str) -> None:
    lab = BaseLab.get("vyos15")
    node_cfg = LabNodeConfig.from_dict("test", cfg)
    lab_cfg = LabConfig(
        name="test", nodes={"test": node_cfg}, links=[], pool="test"
    )
    image = lab.get_compose_image(Config.default(), lab_cfg, node_cfg)
    assert image == expected
