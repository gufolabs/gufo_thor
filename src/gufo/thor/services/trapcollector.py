# ---------------------------------------------------------------------
# Gufo Thor: trapcollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
trapcollector service.

Attributes:
    trapcollector: trapcollector service singleton.
"""

# Python modules
from typing import Any, Dict, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class TrapcollectorService(NocService):
    """trapcollector service."""

    name = "trapcollector"
    dependencies = (datastream, kafka, migrate)
    is_pooled = True
    require_pool_network = True

    def get_compose_networks(
        self: "TrapcollectorService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Dict[str, Any]:
        """Generate docker-compose network."""
        r = super().get_compose_networks(config, svc)
        if not self._pool:
            msg = f"Cannot use pooled service {self.name} without pool"
            raise ValueError(msg)
        addr = config.pools[self._pool].address.trap
        if addr:
            r[f"pool-{self._pool}"]["ipv4_address"] = str(addr)
        return r

    def get_compose_environment(
        self: "TrapcollectorService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[Dict[str, str]]:
        """Set listen address."""
        env = super().get_compose_environment(config, svc) or {}
        if not self._pool:
            msg = f"Cannot use pooled service {self.name} without pool"
            raise ValueError(msg)
        addr = config.pools[self._pool].address.trap
        if addr:
            env["NOC_LISTEN"] = f"{addr}:162"
        return env if env else None


trapcollector = TrapcollectorService()
