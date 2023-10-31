# ---------------------------------------------------------------------
# Gufo Thor: liftbridge service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
liftbridge service.

Attributes:
    liftbridge: liftbridge service singleton.
"""

# Python modules
from typing import Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..log import logger
from .base import BaseService


class LiftbridgeService(BaseService):
    name = "liftbridge"

    def get_compose_image(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "liftbridge:v1.9.0"

    def get_compose_entrypoint(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        return "liftbridge --config /etc/liftbridge.yml"

    def get_compose_volumes(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return [
            "./data/liftbridge:/data/",
            "./etc/liftbridge.yml:/etc/liftbridge.yml",
        ]

    def get_compose_environment(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        return {
            "SERVICE_9292_NAME": "liftbridge",
        }

    def get_compose_dirs(
        self: "LiftbridgeService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[List[str]]:
        return ["etc", "data/liftbridge"]

    def prepare_compose_config(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        # Prepare nginx.conf
        path = "etc/liftbridge.yml"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(LIFT_CONF)


LIFT_CONF = """listen: 0.0.0.0:9292
host: liftbridge
data:
    dir: /data
nats:
    embedded: true
logging:
    level: info
    raft: true
streams:
    compact.enabled: true
    retention.max:
        age: 24h
cursors:
    stream.partitions: 1
"""

liftbridge = LiftbridgeService()
