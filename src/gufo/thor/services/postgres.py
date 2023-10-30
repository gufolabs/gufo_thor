# ---------------------------------------------------------------------
# Gufo Thor: postgres service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List, Optional

# Gufo Thor modules
from gufo.thor.config import Config, ServiceConfig

from .base import BaseService


class PostgresService(BaseService):
    name = "postgres"

    def get_compose_image(
        self: "PostgresService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "postgres:16"

    def get_compose_volumes(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["./data/postgres:/var/lib/postgresql/data"]

    def get_compose_dirs(
        self: "PostgresService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["data/postgres"]

    def get_compose_environment(
        self: "PostgresService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        return {
            "POSTGRES_DB": "noc",
            "POSTGRES_USER": "noc",
            "POSTGRES_PASSWORD": "noc",
        }


postgres = PostgresService()
