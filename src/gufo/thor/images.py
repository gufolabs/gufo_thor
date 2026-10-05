# ---------------------------------------------------------------------
# Gufo Thor: images settings
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Docker image settings for NOC services and versions."""

# Python modules
from dataclasses import dataclass
from typing import cast

# Gufo Thor modules
from .config import config


@dataclass
class VersionSettings:
    """
    Docker image settings for a NOC version.

    Attributes:
        noc_image: Docker image for the NOC application.
        postgres_image: Docker image for PostgreSQL.
        mongo_image: Docker image for MongoDB.
        clickhouse_image: Docker image for ClickHouse.
        kafka_image: Docker image for Kafka.
        consul_image: Docker image for Consul.
    """

    noc_image: str
    postgres_image: str
    mongo_image: str
    clickhouse_image: str
    kafka_image: str
    consul_image: str


# Docker image settings indexed by NOC version.
NOC_VERSION_SETTINGS = {
    "26-dev": VersionSettings(
        noc_image="ghcr.io/gufolabs/noc:master",
        postgres_image="postgres:16",
        mongo_image="mongo:4.4",
        clickhouse_image="clickhouse/clickhouse-server:23",
        kafka_image="bitnamilegacy/kafka:3.6.2",
        consul_image="consul:1.15",
    )
}

# Sentinel object used to indicate a missing value.
SENTINEL = object()


def get_image(name: str) -> str:
    """
    Get the Docker image for a service.

    Args:
        name: Service name.

    Returns:
        Docker image name.

    Raises:
        RuntimeError: If the configured NOC version is not supported or
            the requested service image is not defined.
    """
    nv = config.noc.version
    vs = NOC_VERSION_SETTINGS.get(nv, SENTINEL)
    if vs is SENTINEL:
        msg = f"NOC {nv} is not supported"
        raise RuntimeError(msg)
    img = getattr(vs, f"{name}_image", SENTINEL)
    if img is SENTINEL:
        msg = f"Cannot get image for {name}"
        raise RuntimeError(msg)
    return cast(str, img)
