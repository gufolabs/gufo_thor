# ---------------------------------------------------------------------
# Gufo Thor: postgres service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
postgres service.

Attributes:
    postgres: postgres service singleton.
"""

# Python modules
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService, ComposeDependsCondition, Role


class PostgresService(BaseService):
    """postgres service."""

    name = "postgres"
    compose_image = "postgres:16"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "pg_isready", "-d", "noc"],
        "interval": "3s",
        "timeout": "3s",
        "start_period": "1s",
        "retries": 10,
    }
    compose_volumes = [
        "postgres_data:/var/lib/postgresql/data",
        "backup:/var/lib/postgres/backup",
    ]
    compose_volumes_config = {"postgres_data": {}}
    compose_environment = {
        "POSTGRES_DB": "noc",
        "POSTGRES_USER": "noc",
        "POSTGRES_PASSWORD": "noc",
    }
    service_discovery = {"postgres": 5432}
    role = Role.DB

    def get_compose_ports(
        self: "PostgresService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Expose port."""
        r = super().get_compose_ports(config, svc) or []
        if config.expose.postgres:
            r.append(config.expose.postgres.docker_compose_port(5432))
        return r if r else None


postgres = PostgresService()
