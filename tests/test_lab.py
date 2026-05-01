# ---------------------------------------------------------------------
# Gufo Thor: Lab tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Dict

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.config import Config, LabConfig, LabNodeConfig
from gufo.thor.labs.base import BaseLab


def test_vyos15_docker_console_args() -> None:
    lab = BaseLab.get("vyos15")
    cargs = lab.get_docker_console_args()
    assert cargs
    assert cargs.args == ["-u", "vyos"]
    assert cargs.argv == ["/bin/vbash"]


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({}, "ghcr.io/gufolabs/vyos15:latest"),
        ({"version": "nightly"}, "ghcr.io/gufolabs/vyos15:nightly"),
    ],
)
def test_lab_compose_image(cfg: Dict[str, str], expected: str) -> None:
    lab = BaseLab.get("vyos15")
    node_cfg = LabNodeConfig.from_dict("test", cfg)
    lab_cfg = LabConfig(name="test", nodes={"test": node_cfg}, links=[])
    image = lab.get_compose_image(Config.default(), lab_cfg, node_cfg)
    assert image == expected
