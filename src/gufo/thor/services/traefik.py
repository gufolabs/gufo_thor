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
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService
from .consul import consul


class TraefikService(BaseService):
    name = "traefik"
    dependencies = (consul,)

    def get_compose_image(
        self: "TraefikService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "traefik:1.6"

    def get_compose_volumes(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["/dev/null:/traefik.toml"]

    def get_compose_command(
        self: BaseService, config: Config, svc: ServiceConfig | None
    ) -> str | None:
        return " ".join(
            [
                "--web",
                "--loglevel=INFO",
                "--consulcatalog.endpoint=consul:8500",
                "--consulcatalog.prefix=traefik",
                '--consulcatalog.constraints="tag==backend"',
                "--graceTimeout=10s",
            ]
        )


traefik = TraefikService()
