# ---------------------------------------------------------------------
# Gufo Thor: Lab tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from gufo.thor.labs.base import BaseLab


def test_vyos_docker_console_args() -> None:
    lab = BaseLab.get("vyos15")
    cargs = lab.get_docker_console_args()
    assert cargs
    assert cargs.args == ["-u", "vyos"]
    assert cargs.argv == ["/bin/vbash"]
