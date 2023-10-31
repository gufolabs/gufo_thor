# ---------------------------------------------------------------------
# Gufo Thor: postgres service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
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
from .base import BaseService, ComposeDependsCondition
from .registrator import registrator


class PostgresService(BaseService):
    name = "postgres"
    dependencies = (registrator,)
    compose_image = "postgres:16"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "pg_isready", "-d", "noc"],
        "interval": "3s",
        "timeout": "3s",
        "start_period": "1s",
        "retries": 3,
    }
    compose_volumes = ["./data/postgres:/var/lib/postgresql/data"]
    compose_environment = {
        "POSTGRES_DB": "noc",
        "POSTGRES_USER": "noc",
        "POSTGRES_PASSWORD": "noc",
    }

    def get_compose_dirs(
        self: "PostgresService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["data/postgres"]


postgres = PostgresService()
