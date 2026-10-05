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

# Gufo Thor modules
from ..config import ServiceConfig, config
from ..images import get_image
from .base import ComposeDependsCondition
from .db import DBService


class MongoService(DBService):
    """mongo service."""

    name = "mongo"
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
    service_port = 27017
    backup_script_template = "mongo_backup.sh.j2"
    restore_script_template = "mongo_restore.sh.j2"

    def get_compose_image(self, svc: ServiceConfig | None = None) -> str:
        """Get docker-compose.yml `image` section.

        Args:
            svc: Service's config from `services` part, if any.

        Returns:
            Image name.
        """
        return get_image(self.name)

    def get_compose_ports(
        self, svc: ServiceConfig | None = None
    ) -> list[str] | None:
        """Expose port."""
        r = super().get_compose_ports(svc) or []
        if config.expose.mongo:
            r.append(config.expose.mongo.docker_compose_port(27017))
        return r if r else None


mongo = MongoService()
