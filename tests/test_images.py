# ---------------------------------------------------------------------
# Gufo Thor: Docker image settings tests
# ---------------------------------------------------------------------
# Copyright (C) 2026, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.config import Config
from gufo.thor.images import get_image


@pytest.mark.parametrize(
    ("service", "expected"),
    [
        ("noc", "ghcr.io/gufolabs/noc:master"),
        ("postgres", "postgres:16"),
        ("mongo", "mongo:4.4"),
        ("clickhouse", "clickhouse/clickhouse-server:23"),
        ("kafka", "bitnamilegacy/kafka:3.6.2"),
        ("consul", "consul:1.15"),
    ],
)
def test_get_image(service: str, expected: str) -> None:
    config = Config.default()
    config.noc.version = "26-dev"

    assert get_image(config, service) == expected


def test_get_image_unsupported_version() -> None:
    config = Config.default()
    config.noc.version = "unsupported"

    with pytest.raises(RuntimeError, match="NOC unsupported is not supported"):
        get_image(config, "noc")


def test_get_image_unsupported_service() -> None:
    config = Config.default()
    config.noc.version = "26-dev"

    with pytest.raises(RuntimeError):
        get_image(config, "unsupported")
