# ---------------------------------------------------------------------
# Gufo Thor: syslogcollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
syslogcollector service.

Attributes:
    syslogcollector: syslogcollector service singleton.
"""

# Python modules
from typing import Any, Dict, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .chwriter import chwriter
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class SyslogcollectorService(NocService):
    """syslogcollector service."""

    name = "syslogcollector"
    dependencies = (chwriter, datastream, kafka, migrate)
    is_pooled = True
    require_pool_network = True

    def get_compose_networks(
        self: "SyslogcollectorService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Dict[str, Any]:
        """Generate docker-compose network."""
        r = super().get_compose_networks(config, svc)
        if not self._pool:
            msg = f"Cannot use pooled service {self.name} without pool"
            raise ValueError(msg)
        addr = config.pools[self._pool].address.syslog
        if addr:
            r[f"pool-{self._pool}"]["ipv4_address"] = str(addr)
        return r

    def get_compose_environment(
        self: "SyslogcollectorService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[Dict[str, str]]:
        """Set listen address."""
        env = super().get_compose_environment(config, svc) or {}
        if not self._pool:
            msg = f"Cannot use pooled service {self.name} without pool"
            raise ValueError(msg)
        addr = config.pools[self._pool].address.syslog
        if addr:
            env["NOC_LISTEN"] = f"{addr}:514"
        return env if env else None


syslogcollector = SyslogcollectorService()
