# ---------------------------------------------------------------------
# Gufo Thor: Config tests
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from gufo.thor.config import Config, get_sample


def test_simple() -> None:
    sample = get_sample("simple")
    cfg = Config.from_yaml(sample)
    assert cfg.noc.tag == "master"
    assert cfg.noc.installation_name == "Unconfigured Installation"
    assert cfg.noc.path is None
    assert cfg.noc.custom is None
    assert cfg.expose.domain_name == "go.getnoc.com"
    assert cfg.expose.port == 32777
    assert len(cfg.services) == 2
    assert "web" in cfg.services
    assert "card" in cfg.services
