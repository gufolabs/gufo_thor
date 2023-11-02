# ---------------------------------------------------------------------
# Gufo Thor: mongo service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mongo service.

Attributes:
    mongo: mongo service singleton.
"""

# Python modules
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService, ComposeDependsCondition
from .registrator import registrator


class MongoService(BaseService):
    """mongo service."""

    name = "mongo"
    dependencies = (registrator,)
    compose_image = "mongo:4.4"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "mongo", "--eval", "db.runCommand({ ping: 1 })"],
        "interval": "3s",
        "timeout": "3s",
        "start_period": "1s",
        "retries": 10,
    }
    compose_command = "--wiredTigerCacheSizeGB 4 --bind_ip_all"
    compose_volumes = ["./data/mongo:/data/db"]

    def get_compose_dirs(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Request data directories."""
        return ["data/mongo"]


mongo = MongoService()
