# ---------------------------------------------------------------------
# Gufo Thor: traefik service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
traefik service.

Attributes:
    traefik: traefik service singleton.
"""

# Gufo Thor modules
from .base import BaseService
from .consul import consul


class TraefikService(BaseService):
    """traefik service."""

    name = "traefik"
    dependencies = (consul,)
    compose_image = "traefik:1.6"
    compose_command = " ".join(
        [
            "--web",
            "--loglevel=INFO",
            "--consulcatalog.endpoint=consul:8500",
            "--consulcatalog.prefix=traefik",
            '--consulcatalog.constraints="tag==backend"',
            "--graceTimeout=10s",
        ]
    )
    compose_volumes = ["/dev/null:/traefik.toml"]


traefik = TraefikService()
