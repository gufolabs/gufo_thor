# ---------------------------------------------------------------------
# Gufo Thor: Config tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import tempfile
from pathlib import Path

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.config import Config, get_sample
from gufo.thor.validator import override_errors


def test_simple() -> None:
    sample = get_sample("simple")
    cfg = Config.from_yaml(sample)
    assert cfg.noc.tag == "master"
    assert cfg.noc.installation_name == "Unconfigured Installation"
    assert cfg.noc.path is None
    assert cfg.noc.custom is None
    assert cfg.expose.domain_name == "go.getnoc.com"
    assert cfg.expose.web
    assert cfg.expose.web.port == 32777
    assert len(cfg.services) == 3
    assert "web" in cfg.services
    assert "card" in cfg.services


def test_nonexistent_file() -> None:
    with override_errors(), tempfile.TemporaryDirectory() as tmp:
        nonexistent_path = Path(tmp) / "not_exists.yaml"
        with pytest.raises(RuntimeError) as exc_info:
            Config.from_file(nonexistent_path)
        assert "Cannot read file" in exc_info.value.args[0]


def test_from_file() -> None:
    sample = get_sample("simple")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yml"
        with open(path, "w") as fp:
            fp.write(sample)
        cfg = Config.from_file(path)
        assert cfg.noc.tag == "master"
        assert cfg.noc.installation_name == "Unconfigured Installation"


def test_non_dict() -> None:
    with override_errors():
        with pytest.raises(RuntimeError) as exc_info:
            Config.from_yaml("abc")
        assert exc_info.value.args[0] == "Config must be dict"


def test_empty_config() -> None:
    Config.from_yaml("services: [web]")
