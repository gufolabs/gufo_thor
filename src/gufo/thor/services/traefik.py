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

# Python modules
from pathlib import Path
from typing import Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService
from .consul import consul


class TraefikService(BaseService):
    """traefik service."""

    name = "traefik"
    dependencies = (consul,)
    compose_image = "traefik:2.10"
    compose_etc_dirs = [Path("traefik")]
    compose_volumes = ["./etc/traefik/:/etc/traefik/"]

    def prepare_compose_config(
        self: "TraefikService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """Generate config."""
        self.render_file(Path("etc", "traefik", "traefik.yml"), "traefik.yml")


traefik = TraefikService()
