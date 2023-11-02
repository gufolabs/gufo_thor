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
from pathlib import Path

# Gufo Thor modules
from .base import BaseService, ComposeDependsCondition


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
    compose_volumes = ["./data/postgres:/var/lib/postgresql/data"]
    compose_environment = {
        "POSTGRES_DB": "noc",
        "POSTGRES_USER": "noc",
        "POSTGRES_PASSWORD": "noc",
    }
    compose_data_dirs = [Path("postgres")]
    service_discovery = {"postgres": 5432}


postgres = PostgresService()
