# ---------------------------------------------------------------------
# Gufo Thor: mongo service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
mongo service.

Attributes:
    mongo: mongo service singleton.
"""

# NOC modules
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService, ComposeDependsCondition, Role


class MongoService(BaseService):
    """mongo service."""

    name = "mongo"
    compose_image = "mongo:4.4"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "mongo", "--eval", "db.runCommand({ ping: 1 })"],
        "interval": "3s",
        "timeout": "3s",
        "start_period": "1s",
        "retries": 10,
    }
    compose_command = "--wiredTigerCacheSizeGB 1.5 --bind_ip_all"
    compose_volumes = ["mongo_data:/data/db", "backup:/data/backup"]
    compose_volumes_config = {"mongo_data": {}}
    service_discovery = {"mongo": 27017}
    role = Role.DB

    def get_compose_ports(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Expose port."""
        r = super().get_compose_ports(config, svc) or []
        if config.expose.mongo:
            r.append(config.expose.mongo.docker_compose_port(27017))
        return r if r else None


mongo = MongoService()
