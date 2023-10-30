# ---------------------------------------------------------------------
# Gufo Thor: mongo service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import List, Optional

# Gufo Thor modules
from gufo.thor.config import Config, ServiceConfig

from .base import BaseService


class MongoService(BaseService):
    name = "mongo"

    def get_compose_image(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "mongo:4.4"

    def get_compose_command(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        return "--wiredTigerCacheSizeGB 4 --bind_ip_all"

    def get_compose_volumes(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["./data/mongo:/data/db"]

    def get_compose_dirs(
        self: "MongoService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["data/mongo"]


mongo = MongoService()
